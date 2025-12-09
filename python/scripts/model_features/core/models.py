"""Pydantic models for model feature testing framework."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TestStatus(str, Enum):
    """Status of a feature test for a model."""

    SUPPORTED = "supported"
    """Feature is supported for this model."""
    NOT_SUPPORTED = "not_supported"
    """Feature is not supported for this model."""
    ERROR = "error"
    """Error during testing."""
    UNAVAILABLE = "unavailable"
    """Model doesn't exist or is deprecated."""
    SKIPPED = "skipped"
    """Test skipped due to unmet dependencies."""


class FeatureTestResult(BaseModel):
    """Result of testing a single feature on a single model."""

    status: TestStatus
    tested_at: datetime = Field(default_factory=datetime.now)
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def model_dump_yaml_friendly(self) -> dict[str, Any]:
        """Return a dict suitable for YAML serialization."""
        result: dict[str, Any] = {
            "status": self.status.value,
            "tested_at": self.tested_at.isoformat(),
        }
        if self.error_message:
            result["error_message"] = self.error_message
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class ModelInfo(BaseModel):
    """Information about a model from the provider API."""

    id: str
    owned_by: str | None = None
    created: datetime | None = None
    discovered_at: datetime = Field(default_factory=datetime.now)
    deprecated: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelFeatureMatrix(BaseModel):
    """Complete feature test results for a single model."""

    model: ModelInfo
    features: dict[str, FeatureTestResult] = Field(default_factory=dict)

    def get_untested_features(self, all_features: set[str]) -> set[str]:
        """Return features that haven't been tested for this model."""
        return all_features - set(self.features.keys())

    def needs_retest(self, feature: str, max_age_days: int | None = None) -> bool:
        """Check if a feature needs retesting (e.g., due to age or error status)."""
        if feature not in self.features:
            return True
        result = self.features[feature]
        if result.status == TestStatus.ERROR:
            return True
        if max_age_days is not None:
            age = datetime.now() - result.tested_at
            return age.days > max_age_days
        return False


class ProviderRegistry(BaseModel):
    """Complete registry of models and their feature test results for a provider."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    provider: str
    models: dict[str, ModelFeatureMatrix] = Field(default_factory=dict)
    last_discovery: datetime | None = None
    known_features: set[str] = Field(default_factory=set)

    def get_model(self, model_id: str) -> ModelFeatureMatrix | None:
        """Get feature matrix for a model, or None if not found."""
        return self.models.get(model_id)

    def add_model(self, model_info: ModelInfo) -> ModelFeatureMatrix:
        """Add a new model to the registry."""
        if model_info.id not in self.models:
            self.models[model_info.id] = ModelFeatureMatrix(model=model_info)
        return self.models[model_info.id]

    def record_test_result(
        self, model_id: str, feature: str, result: FeatureTestResult
    ) -> None:
        """Record a test result for a model/feature combination."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not in registry")
        self.models[model_id].features[feature] = result
        self.known_features.add(feature)

    def get_untested_combinations(self) -> list[tuple[str, str]]:
        """Return all (model_id, feature) pairs that haven't been tested."""
        combinations: list[tuple[str, str]] = []
        for model_id, matrix in self.models.items():
            for feature in self.known_features:
                if feature not in matrix.features:
                    combinations.append((model_id, feature))
        return combinations

    def get_models_needing_test(
        self, feature: str, max_age_days: int | None = None
    ) -> list[str]:
        """Return model IDs that need testing for a specific feature."""
        return [
            model_id
            for model_id, matrix in self.models.items()
            if matrix.needs_retest(feature, max_age_days)
        ]

    def mark_deprecated(self, model_id: str) -> None:
        """Mark a model as deprecated."""
        if model_id in self.models:
            self.models[model_id].model.deprecated = True
