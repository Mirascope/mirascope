"""Core framework for model feature testing."""

from .models import (
    FeatureTestResult,
    ModelFeatureMatrix,
    ModelInfo,
    ProviderConfig,
    TestStatus,
)
from .registry import ModelFeatureRegistry
from .runner import FeatureTestRunner, ModelDiscovery
from .testing import ClientT, FeatureTest

__all__ = [
    "ClientT",
    "FeatureTest",
    "FeatureTestResult",
    "FeatureTestRunner",
    "ModelDiscovery",
    "ModelFeatureMatrix",
    "ModelFeatureRegistry",
    "ModelInfo",
    "ProviderConfig",
    "TestStatus",
]
