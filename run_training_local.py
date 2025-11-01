#!/usr/bin/env python3
"""
100% LOCAL VERSION - No Azure needed!
Saves everything to your PC.
"""

import sys
from datetime import datetime
from continuous_learning_trainer_local import ContinuousLearningTrainer, TOP_100_STOCKS

def main():
    print("\n" + "="*80)
    print("🚀 ML TRADING SYSTEM - 100% LOCAL (NO AZURE)")
    print("="*80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💾 Saves to: ./ml_models/ (in current folder)")
    print(f"📊 Available stocks: {len(TOP_100_STOCKS)}")
    print("="*80 + "\n")
    
    # Initialize LOCAL trainer (no Azure!)
    trainer = ContinuousLearningTrainer(
    local_storage_path="./backend/models_local",
        data_retention_days=365,
        incremental_mode=True
    )
    
    print("✓ Trainer initialized")
    print(f"✓ Models will save to: ml_models/trained-models/")
    print(f"✓ Data will save to: ml_models/training-data/")
    print(f"✓ History will save to: ml_models/training-history/\n")
    
    # Training options
    print("="*80)
    print("TRAINING OPTIONS")
    print("="*80)
    print("1. Train ALL 100+ stocks (~30-45 minutes)")
    print("2. Train TOP 20 stocks (~5-8 minutes)")
    print("3. Train TOP 10 stocks (~2-3 minutes)")
    print("="*80)
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        stocks_to_train = list(TOP_100_STOCKS.keys())
    elif choice == "2":
        stocks_to_train = list(TOP_100_STOCKS.keys())[:20]
    else:
        stocks_to_train = list(TOP_100_STOCKS.keys())[:10]
    
    print(f"\n📋 Will train {len(stocks_to_train)} stocks\n")
    
    results = []
    failed = []
    
    for i, ticker in enumerate(stocks_to_train, 1):
        stock_name = TOP_100_STOCKS.get(ticker, ticker)
        print(f"\n[{i}/{len(stocks_to_train)}] Training: {ticker} ({stock_name})")
        
        try:
            model, metadata, history = trainer.train_with_accumulation(ticker)
            
            results.append({
                'ticker': ticker,
                'name': stock_name,
                'accuracy': metadata.accuracy,
                'samples': metadata.total_training_samples
            })
            
            print(f"✅ {ticker} - Accuracy: {metadata.accuracy:.2%}, Samples: {metadata.total_training_samples:,}")
            
        except Exception as e:
            print(f"❌ {ticker} FAILED: {e}")
            failed.append(ticker)
    
    # Summary
    print("\n" + "="*80)
    print("📈 TRAINING SUMMARY")
    print("="*80)
    print(f"✅ Successful: {len(results)}/{len(stocks_to_train)}")
    if failed:
        print(f"❌ Failed: {len(failed)}")
    
    if results:
        print("\n🏆 Top 5 by Accuracy:")
        top_5 = sorted(results, key=lambda x: x['accuracy'], reverse=True)[:5]
        for rank, r in enumerate(top_5, 1):
            print(f"  {rank}. {r['ticker']} - {r['accuracy']:.2%}")
    
    print("="*80)
    print(f"✅ All models saved to: ./ml_models/")
    print("="*80 + "\n")
    
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
