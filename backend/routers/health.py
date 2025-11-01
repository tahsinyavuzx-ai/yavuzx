"""
Health check endpoint.
"""
from fastapi import APIRouter, Depends
from datetime import datetime
import logging
from ..models.schemas import HealthResponse
from ..models.model_loader import ModelManager
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/health", tags=["Health"])
settings = get_settings()


def get_model_manager() -> ModelManager:
    """Dependency to get model manager singleton."""
    if not hasattr(get_model_manager, "instance"):
        get_model_manager.instance = ModelManager()
    return get_model_manager.instance


@router.get("/", response_model=HealthResponse)
async def health_check(model_manager: ModelManager = Depends(get_model_manager)):
    """Health check endpoint."""
    try:
        models_loaded = len(model_manager.get_available_assets())
        local_connected = model_manager.storage.is_connected()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            models_loaded=models_loaded,
            local_connected=local_connected,
            version=settings.APP_VERSION
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            models_loaded=0,
            local_connected=False,
            version=settings.APP_VERSION
        )
