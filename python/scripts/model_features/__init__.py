"""Model feature testing framework.

This module provides a reusable framework for discovering models from provider APIs
and testing their feature support incrementally.

The core framework lives in the `core` submodule. Provider-specific implementations
are in top-level scripts like `openai.py`, `google.py`, etc.

Usage:
    # Run OpenAI tests
    python -m model_features.openai --list-features

    # Run other provider tests (when implemented)
    python -m model_features.google --list-features
    python -m model_features.anthropic --list-features
"""

from .core import (
    ClientT,
    FeatureTest,
    FeatureTestResult,
    FeatureTestRunner,
    ModelFeatureMatrix,
    ModelFeatureRegistry,
    ModelInfo,
    TestStatus,
)

__all__ = [
    "ClientT",
    "FeatureTest",
    "FeatureTestResult",
    "FeatureTestRunner",
    "ModelFeatureMatrix",
    "ModelFeatureRegistry",
    "ModelInfo",
    "TestStatus",
]
