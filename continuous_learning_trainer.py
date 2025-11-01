"""
Placeholder classes for unpickling models trained with continuous_learning_trainer.
This file exists only to allow pickle to load models that reference these classes.
"""
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime


@dataclass
class ModelSnapshot:
    """
    Placeholder for ModelSnapshot class used in training.
    Contains the model and metadata.
    """
    model: Any
    preprocessor: Any
    feature_columns: list
    version: str
    accuracy: float
    total_samples: int
    trained_at: datetime
    asset_class: str
    
    def __init__(self, model=None, preprocessor=None, feature_columns=None, 
                 version="1.0.0", accuracy=0.0, total_samples=0, 
                 trained_at=None, asset_class=""):
        self.model = model
        self.preprocessor = preprocessor
        self.feature_columns = feature_columns or []
        self.version = version
        self.accuracy = accuracy
        self.total_samples = total_samples
        self.trained_at = trained_at or datetime.utcnow()
        self.asset_class = asset_class
