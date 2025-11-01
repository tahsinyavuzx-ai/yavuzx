"""
Azure Blob Storage client for loading trained models.
Handles secure connection and model retrieval.
Supports versioned filenames (e.g., nasdaq_4h_v1_20251030_121740.pkl)
"""

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import pickle
import json
from io import BytesIO
import traceback

logger = logging.getLogger(__name__)


class AzureModelStorage:
    """Manages model storage and retrieval from Azure Blob Storage."""

    def __init__(self, connection_string: str, container_name: str):
        """
        Initialize Azure storage client.

        Args:
            connection_string: Azure Storage connection string
            container_name: Container name for models (e.g., 'trained-models')
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}

    # --------------------------------------------------------
    # MODEL LOAD
    # --------------------------------------------------------
    def load_model(self, asset_class: str, cache_ttl: int = 3600) -> Optional[Any]:
        """
        Load trained model from Azure Blob Storage with caching.
        Automatically finds the latest versioned model file.
        Works with pickled models dumped via pickle.dump.

        Args:
            asset_class: e.g., 'nasdaq', 'crypto', 'gold', etc.
            cache_ttl: Cache time-to-live in seconds
        """
        cache_key = f"model_{asset_class.lower()}"

        # ✅ Check cache
        if cache_key in self._cache:
            if datetime.utcnow() - self._cache_timestamps[cache_key] < timedelta(seconds=cache_ttl):
                logger.info(f"[CACHE] Model for {asset_class} loaded from cache")
                return self._cache[cache_key]

        try:
            # ✅ Be more flexible with naming (handles "nasdaq", "nasdaq_4h", etc.)
            prefix = asset_class.lower().split("_")[0] + "_"
            logger.info(f"[Azure] Searching for blobs with prefix: '{prefix}'")

            blobs = list(self.container_client.list_blobs(name_starts_with=prefix))
            model_blobs = [b for b in blobs if b.name.endswith('.pkl')]

            if not model_blobs:
                logger.error(f"[Azure] No model files found for prefix '{prefix}' in container '{self.container_name}'")
                return None

            # ✅ Pick latest by timestamp in filename
            latest_blob = sorted(model_blobs, key=lambda x: x.name, reverse=True)[0]
            blob_name = latest_blob.name

            logger.info(f"[Azure] Found latest model for {asset_class}: {blob_name}")

            # ✅ Download model bytes
            blob_client = self.container_client.get_blob_client(blob_name)
            model_bytes = blob_client.download_blob().readall()

            # ✅ Load pickled model
            model = pickle.loads(model_bytes)

            # ✅ Update cache
            self._cache[cache_key] = model
            self._cache_timestamps[cache_key] = datetime.utcnow()

            logger.info(f"[Azure] Model '{blob_name}' loaded successfully ({type(model).__name__})")
            return model

        except Exception as e:
            logger.error(f"[Azure] Error loading model for {asset_class}: {e}")
            logger.error(traceback.format_exc())
            return None

    # --------------------------------------------------------
    # METADATA LOAD
    # --------------------------------------------------------
    def load_model_metadata(self, asset_class: str) -> Optional[Dict[str, Any]]:
        """Load metadata (.json) for a specific model."""
        try:
            prefix = asset_class.lower().split("_")[0] + "_"
            blobs = list(self.container_client.list_blobs(name_starts_with=prefix))
            metadata_blobs = [b for b in blobs if b.name.endswith('.json')]

            if not metadata_blobs:
                logger.warning(f"[Azure] No metadata files found for {asset_class}")
                return None

            latest_blob = sorted(metadata_blobs, key=lambda x: x.name, reverse=True)[0]
            blob_name = latest_blob.name

            blob_client = self.container_client.get_blob_client(blob_name)
            metadata_bytes = blob_client.download_blob().readall()
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            return metadata

        except ResourceNotFoundError:
            logger.warning(f"[Azure] Metadata not found for {asset_class}")
            return None
        except Exception as e:
            logger.error(f"[Azure] Error loading metadata for {asset_class}: {e}")
            return None

    # --------------------------------------------------------
    # UTILS
    # --------------------------------------------------------
    def list_available_models(self) -> List[str]:
        """List all available .pkl model base names in the container."""
        try:
            blob_list = list(self.container_client.list_blobs())
            models = set()

            for blob in blob_list:
                if blob.name.endswith('.pkl'):
                    name_part = blob.name.split('_')[0].upper()
                    models.add(name_part)

            logger.info(f"[Azure] Found models: {models}")
            return list(models)
        except Exception as e:
            logger.error(f"[Azure] Error listing models: {e}")
            return []

    def is_connected(self) -> bool:
        """Verify Azure container connection."""
        try:
            self.container_client.get_container_properties()
            return True
        except Exception as e:
            logger.error(f"[Azure] Connection test failed: {e}")
            return False

    def clear_cache(self):
        """Clear in-memory cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("[Azure] Model cache cleared")

    def get_model_version_info(self, asset_class: str) -> Optional[str]:
        """Extract version string (e.g., 'v1') from latest filename."""
        try:
            prefix = asset_class.lower().split("_")[0] + "_"
            blobs = list(self.container_client.list_blobs(name_starts_with=prefix))
            model_blobs = [b for b in blobs if b.name.endswith('.pkl')]

            if not model_blobs:
                return None

            latest_blob = sorted(model_blobs, key=lambda x: x.name, reverse=True)[0]
            filename = latest_blob.name.replace('.pkl', '')
            parts = filename.split('_')

            version = next((p for p in parts if p.startswith('v')), "v1")
            return version

        except Exception as e:
            logger.error(f"[Azure] Error extracting version info for {asset_class}: {e}")
            return None
