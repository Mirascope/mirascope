"""Registry persistence and management."""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .models import (
    FeatureTestResult,
    ModelFeatureMatrix,
    ModelInfo,
    ProviderRegistry,
    TestStatus,
)


class ModelFeatureRegistry:
    """Manages persistence of model feature test results.

    Uses YAML format for human-readable storage with Pydantic for validation.
    """

    def __init__(self, storage_path: Path, provider: str) -> None:
        self.storage_path = storage_path
        self.provider = provider
        self._registry: ProviderRegistry | None = None

    @property
    def registry(self) -> ProviderRegistry:
        """Lazy-load the registry from disk."""
        if self._registry is None:
            self._registry = self._load()
        return self._registry

    def _load(self) -> ProviderRegistry:
        """Load registry from YAML file, or create empty one."""
        if not self.storage_path.exists():
            return ProviderRegistry(provider=self.provider)

        with open(self.storage_path) as f:
            data = yaml.safe_load(f)

        if data is None:
            return ProviderRegistry(provider=self.provider)

        return self._deserialize(data)

    def _deserialize(self, data: dict[str, Any]) -> ProviderRegistry:
        """Deserialize YAML data into ProviderRegistry."""
        provider = data.get("provider", "unknown")

        models: dict[str, ModelFeatureMatrix] = {}
        for model_id, model_data in data.get("models", {}).items():
            model_info = ModelInfo(
                id=model_id,
                owned_by=model_data.get("owned_by"),
                created=datetime.fromisoformat(model_data["created"])
                if model_data.get("created")
                else None,
                discovered_at=datetime.fromisoformat(model_data["discovered_at"])
                if model_data.get("discovered_at")
                else datetime.now(),
                deprecated=model_data.get("deprecated", False),
                metadata=model_data.get("metadata", {}),
            )

            features: dict[str, FeatureTestResult] = {}
            for feature_name, feature_data in model_data.get("features", {}).items():
                features[feature_name] = FeatureTestResult(
                    status=TestStatus(feature_data["status"]),
                    tested_at=datetime.fromisoformat(feature_data["tested_at"])
                    if feature_data.get("tested_at")
                    else datetime.now(),
                    error_message=feature_data.get("error_message"),
                    metadata=feature_data.get("metadata", {}),
                )

            models[model_id] = ModelFeatureMatrix(model=model_info, features=features)

        return ProviderRegistry(
            provider=provider,
            models=models,
            last_discovery=datetime.fromisoformat(data["last_discovery"])
            if data.get("last_discovery")
            else None,
            known_features=set(data.get("known_features", [])),
        )

    def _serialize(self) -> dict[str, Any]:
        """Serialize registry to YAML-friendly dict."""
        registry = self.registry

        models_data: dict[str, Any] = {}
        for model_id, matrix in sorted(registry.models.items()):
            model_data: dict[str, Any] = {
                "owned_by": matrix.model.owned_by,
                "deprecated": matrix.model.deprecated,
            }
            if matrix.model.created:
                model_data["created"] = matrix.model.created.isoformat()
            model_data["discovered_at"] = matrix.model.discovered_at.isoformat()
            if matrix.model.metadata:
                model_data["metadata"] = matrix.model.metadata

            features_data: dict[str, Any] = {}
            for feature_name, feature_result in sorted(matrix.features.items()):
                features_data[feature_name] = feature_result.model_dump_yaml_friendly()

            if features_data:
                model_data["features"] = features_data

            models_data[model_id] = model_data

        result: dict[str, Any] = {
            "provider": registry.provider,
            "known_features": sorted(registry.known_features),
            "models": models_data,
        }
        if registry.last_discovery:
            result["last_discovery"] = registry.last_discovery.isoformat()

        return result

    def save(self) -> None:
        """Save registry to YAML file."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = self._serialize()

        with open(self.storage_path, "w") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120,
            )

    def add_model(self, model_info: ModelInfo) -> ModelFeatureMatrix:
        """Add a model to the registry."""
        return self.registry.add_model(model_info)

    def record_test_result(
        self, model_id: str, feature: str, result: FeatureTestResult
    ) -> None:
        """Record a test result and save."""
        self.registry.record_test_result(model_id, feature, result)

    def update_last_discovery(self) -> None:
        """Update the last discovery timestamp."""
        self.registry.last_discovery = datetime.now()

    def get_untested_combinations(self) -> list[tuple[str, str]]:
        """Get all (model_id, feature) pairs needing testing."""
        return self.registry.get_untested_combinations()

    def register_feature(self, feature_name: str) -> None:
        """Register a feature name so we know to test it."""
        self.registry.known_features.add(feature_name)

    def get_all_model_ids(self) -> set[str]:
        """Get all model IDs in the registry."""
        return set(self.registry.models.keys())

    def prune_deprecated_models(self, keep_days: int = 30) -> list[str]:
        """Remove models that have been deprecated for a while.

        Returns list of removed model IDs.
        """
        removed: list[str] = []
        now = datetime.now()
        for model_id, matrix in list(self.registry.models.items()):
            if matrix.model.deprecated:
                # Check if any feature test shows unavailable
                unavailable_tests = [
                    r
                    for r in matrix.features.values()
                    if r.status == TestStatus.UNAVAILABLE
                ]
                if unavailable_tests:
                    # Use the most recent unavailable test date
                    latest = max(t.tested_at for t in unavailable_tests)
                    if (now - latest).days > keep_days:
                        del self.registry.models[model_id]
                        removed.append(model_id)
        return removed
