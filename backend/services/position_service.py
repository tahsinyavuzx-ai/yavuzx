"""
Position management and P&L calculation service.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from ..database import get_connection, dict_factory
from ..models.paper_trading import Position, PositionWithPnL, PortfolioStats
from ..services.market_data_service import MarketDataService
from ..models.schemas import AssetClass

logger = logging.getLogger(__name__)


class PositionService:
    """Manage paper trading positions and calculate P&L."""
    
    def __init__(self):
        self.market_service = MarketDataService()
    
    def create_position(self, asset_class: str, asset_symbol: str, position_type: str,
                       entry_price: float, quantity: float, leverage: float = 1.0,
                       notes: Optional[str] = None) -> Position:
        """Create a new position."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO positions 
                (asset_class, asset_symbol, position_type, entry_price, quantity, leverage, notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (asset_class, asset_symbol, position_type, entry_price, quantity, leverage, notes, 'OPEN'))
            
            conn.commit()
            position_id = cursor.lastrowid
            logger.info(f"Created position {position_id}: {position_type} {quantity} {asset_symbol} @ ${entry_price}")
            return self.get_position(position_id)
        finally:
            conn.close()
    
    def get_position(self, position_id: int) -> Optional[Position]:
        """Get a single position."""
        conn = get_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM positions WHERE id = ?', (position_id,))
            row = cursor.fetchone()
            return self._row_to_position(row) if row else None
        finally:
            conn.close()
    
    def get_all_positions(self, status: Optional[str] = None) -> List[Position]:
        """Get all positions."""
        conn = get_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        try:
            if status:
                cursor.execute('SELECT * FROM positions WHERE status = ? ORDER BY entry_time DESC', (status,))
            else:
                cursor.execute('SELECT * FROM positions ORDER BY entry_time DESC')
            rows = cursor.fetchall()
            return [self._row_to_position(row) for row in rows]
        finally:
            conn.close()
    
    def get_positions_with_pnl(self) -> List[PositionWithPnL]:
        """Get all open positions with calculated P&L."""
        positions = self.get_all_positions(status='OPEN')
        results = []
        
        for position in positions:
            try:
                current_price = self._get_current_price(position.asset_class)
                if current_price:
                    pnl_data = self._calculate_pnl(position, current_price)
                    pos_with_pnl = PositionWithPnL(
                        **position.dict(),
                        current_price=current_price,
                        **pnl_data
                    )
                    results.append(pos_with_pnl)
            except Exception as e:
                logger.error(f"Error calculating P&L for position {position.id}: {e}")
        
        return results
    
    def update_position(self, position_id: int, quantity: Optional[float] = None,
                       leverage: Optional[float] = None, notes: Optional[str] = None) -> Optional[Position]:
        """Update position details."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            updates, params = [], []
            
            if quantity is not None:
                updates.append("quantity = ?")
                params.append(quantity)
            if leverage is not None:
                updates.append("leverage = ?")
                params.append(leverage)
            if notes is not None:
                updates.append("notes = ?")
                params.append(notes)
            
            if not updates:
                return self.get_position(position_id)
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(position_id)
            
            cursor.execute(f"UPDATE positions SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
            logger.info(f"Updated position {position_id}")
            return self.get_position(position_id)
        finally:
            conn.close()
    
    def close_position(self, position_id: int, exit_price: float,
                      notes: Optional[str] = None) -> Optional[Position]:
        """Close an open position."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE positions 
                SET status = ?, exit_price = ?, exit_time = CURRENT_TIMESTAMP, 
                    notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', ('CLOSED', exit_price, notes, position_id))
            conn.commit()
            logger.info(f"Closed position {position_id} @ ${exit_price}")
            return self.get_position(position_id)
        finally:
            conn.close()
    
    def delete_position(self, position_id: int) -> bool:
        """Delete a position."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM positions WHERE id = ? AND status = ?', (position_id, 'OPEN'))
            conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Deleted position {position_id}")
                return True
            return False
        finally:
            conn.close()
    
    def get_portfolio_stats(self) -> PortfolioStats:
        """Calculate portfolio statistics."""
        all_positions = self.get_all_positions()
        open_positions = [p for p in all_positions if p.status == 'OPEN']
        closed_positions = [p for p in all_positions if p.status == 'CLOSED']
        
        total_pnl, wins, losses = 0.0, [], []
        
        for pos in closed_positions:
            pnl = self._calculate_pnl_for_closed(pos)
            total_pnl += pnl
            (wins if pnl > 0 else losses).append(pnl)
        
        return PortfolioStats(
            total_positions=len(all_positions),
            open_positions=len(open_positions),
            closed_positions=len(closed_positions),
            total_pnl=total_pnl,
            total_pnl_percent=0.0,
            win_rate=(len(wins) / len(closed_positions) * 100) if closed_positions else 0.0,
            largest_win=max(wins) if wins else 0.0,
            largest_loss=min(losses) if losses else 0.0,
            avg_win=sum(wins) / len(wins) if wins else 0.0,
            avg_loss=sum(losses) / len(losses) if losses else 0.0
        )
    
    def _row_to_position(self, row: Dict) -> Position:
        """Convert DB row to Position."""
        return Position(
            id=row['id'],
            asset_class=row['asset_class'],
            asset_symbol=row['asset_symbol'],
            position_type=row['position_type'],
            entry_price=row['entry_price'],
            quantity=row['quantity'],
            leverage=row['leverage'],
            entry_time=datetime.fromisoformat(row['entry_time']),
            exit_price=row['exit_price'],
            exit_time=datetime.fromisoformat(row['exit_time']) if row['exit_time'] else None,
            status=row['status'],
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def _get_current_price(self, asset_class: str) -> Optional[float]:
        """Get current price for an asset."""
        try:
            asset_enum = AssetClass(asset_class.upper())
            return self.market_service.get_current_price(asset_enum)
        except Exception as e:
            logger.error(f"Error getting current price for {asset_class}: {e}")
            return None
    
    def _calculate_pnl(self, position: Position, current_price: float) -> Dict[str, float]:
        """Calculate P&L."""
        if position.position_type == 'LONG':
            pnl = (current_price - position.entry_price) * position.quantity
            pnl_percent = ((current_price - position.entry_price) / position.entry_price) * 100
        else:
            pnl = (position.entry_price - current_price) * position.quantity
            pnl_percent = ((position.entry_price - current_price) / position.entry_price) * 100
        
        return {
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'pnl_with_leverage': pnl * position.leverage,
            'pnl_with_leverage_percent': pnl_percent * position.leverage
        }
    
    def _calculate_pnl_for_closed(self, position: Position) -> float:
        """Calculate P&L for closed position."""
        if not position.exit_price:
            return 0.0
        
        pnl = (position.exit_price - position.entry_price) * position.quantity if position.position_type == 'LONG' else (position.entry_price - position.exit_price) * position.quantity
        return pnl * position.leverage
