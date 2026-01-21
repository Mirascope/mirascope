"""Feature test runner with incremental testing support."""

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Generic

from .models import FeatureTestResult, ModelInfo, TestStatus
from .registry import ModelFeatureRegistry
from .testing import ClientT, FeatureTest


def topological_sort_tests(
    tests: list[tuple[str, str]], feature_tests: dict[str, FeatureTest[ClientT]]
) -> list[tuple[str, str]]:
    """Sort tests so dependencies are run before dependent tests.

    Args:
        tests: List of (model_id, feature) tuples
        feature_tests: Dictionary of feature name to FeatureTest

    Returns:
        Sorted list where dependencies come first
    """
    # Group tests by model
    tests_by_model: dict[str, list[str]] = {}
    for model_id, feature in tests:
        if model_id not in tests_by_model:
            tests_by_model[model_id] = []
        tests_by_model[model_id].append(feature)

    # Sort features for each model using topological sort
    sorted_tests: list[tuple[str, str]] = []
    for model_id, features in tests_by_model.items():
        # Build dependency graph
        in_degree: dict[str, int] = dict.fromkeys(features, 0)
        adjacency: dict[str, list[str]] = {f: [] for f in features}

        for feature in features:
            test = feature_tests.get(feature)
            if test and test.dependencies:
                for dep in test.dependencies:
                    if dep in in_degree:  # Only consider deps in our test set
                        adjacency[dep].append(feature)
                        in_degree[feature] += 1

        # Kahn's algorithm for topological sort
        queue = [f for f in features if in_degree[f] == 0]
        sorted_features: list[str] = []

        while queue:
            # Sort queue for deterministic ordering
            queue.sort()
            current = queue.pop(0)
            sorted_features.append(current)

            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Add sorted tests for this model
        for feature in sorted_features:
            sorted_tests.append((model_id, feature))

    return sorted_tests


# Type aliases
ResultCallback = Callable[[str, str, FeatureTestResult], None]


class TestRunSummary:
    """Summary of a test run."""

    def __init__(self) -> None:
        self.supported = 0
        self.not_supported = 0
        self.unavailable = 0
        self.errors = 0
        self.skipped = 0

    def record(self, status: TestStatus) -> None:
        match status:
            case TestStatus.SUPPORTED:
                self.supported += 1
            case TestStatus.NOT_SUPPORTED:
                self.not_supported += 1
            case TestStatus.UNAVAILABLE:
                self.unavailable += 1
            case TestStatus.ERROR:
                self.errors += 1
            case TestStatus.SKIPPED:
                self.skipped += 1

    @property
    def total(self) -> int:
        return (
            self.supported
            + self.not_supported
            + self.unavailable
            + self.errors
            + self.skipped
        )

    def __str__(self) -> str:
        parts = [
            f"Tested: {self.total}",
            f"Supported: {self.supported}",
            f"Not supported: {self.not_supported}",
            f"Unavailable: {self.unavailable}",
            f"Errors: {self.errors}",
        ]
        if self.skipped > 0:
            parts.append(f"Skipped: {self.skipped}")
        return " | ".join(parts)


class FeatureTestRunner(Generic[ClientT]):
    """Orchestrates feature testing for models.

    Supports:
    - Incremental testing (only test new model/feature combinations)
    - Resumable runs (progress saved after each test)
    - Multiple feature tests
    - Dependency-aware test ordering
    """

    def __init__(
        self,
        registry: ModelFeatureRegistry,
        client: ClientT,
    ) -> None:
        self.registry = registry
        self.client = client
        self._feature_tests: dict[str, FeatureTest[ClientT]] = {}

    def register_feature_test(self, test: FeatureTest[ClientT]) -> None:
        """Register a feature test to run."""
        self._feature_tests[test.name] = test
        self.registry.register_feature(test.name)

    def _check_dependencies(
        self, model_id: str, feature: str
    ) -> tuple[bool, list[str]]:
        """Check if all dependencies for a test are met.

        Returns:
            Tuple of (dependencies_met, list of failed dependencies)
        """
        test = self._feature_tests.get(feature)
        if test is None or not test.dependencies:
            return (True, [])

        model_matrix = self.registry.registry.get_model(model_id)
        if model_matrix is None:
            return (True, [])

        failed_deps: list[str] = []
        for dep in test.dependencies:
            dep_result = model_matrix.features.get(dep)
            # Dependency is failed if it's not tested, unavailable, or errored
            if dep_result is None or dep_result.status in (
                TestStatus.UNAVAILABLE,
                TestStatus.ERROR,
                TestStatus.NOT_SUPPORTED,
                TestStatus.SKIPPED,
            ):
                failed_deps.append(dep)
        return (len(failed_deps) == 0, failed_deps)

    def add_models(self, models: Iterable[ModelInfo]) -> int:
        """Add discovered models to the registry.

        Args:
            models: Iterable of ModelInfo objects to add

        Returns:
            Number of new models added
        """
        new_count = 0
        existing_ids = self.registry.get_all_model_ids()

        for model_info in models:
            if model_info.id not in existing_ids:
                self.registry.add_model(model_info)
                new_count += 1
                print(f"  Discovered new model: {model_info.id}")

        self.registry.update_last_discovery()
        self.registry.save()
        return new_count

    def get_pending_tests(
        self,
        features: list[str] | None = None,
        models: list[str] | None = None,
        include_errors: bool = True,
        max_age_days: int | None = None,
    ) -> list[tuple[str, str]]:
        """Get list of (model_id, feature) pairs that need testing.

        Args:
            features: Limit to specific features (default: all registered)
            models: Limit to specific models (default: all in registry)
            include_errors: Re-test combinations that previously errored
            max_age_days: Re-test if result older than this many days

        Returns:
            List of (model_id, feature_name) tuples

        Note:
            Tests with SKIPPED status are always included (dependencies may now be met).
        """
        feature_set = set(features) if features else set(self._feature_tests.keys())
        model_set = set(models) if models else self.registry.get_all_model_ids()

        pending: list[tuple[str, str]] = []
        for model_id in model_set:
            model_matrix = self.registry.registry.get_model(model_id)
            if model_matrix is None:
                continue

            for feature in feature_set:
                if feature not in self._feature_tests:
                    continue

                existing = model_matrix.features.get(feature)
                if (
                    existing is None
                    or existing.status
                    == TestStatus.SKIPPED  # Always retry skipped tests
                    or (include_errors and existing.status == TestStatus.ERROR)
                    or (
                        max_age_days is not None
                        and (datetime.now() - existing.tested_at).days > max_age_days
                    )
                ):
                    pending.append((model_id, feature))

        return pending

    def run_tests(
        self,
        pending: list[tuple[str, str]] | None = None,
        save_interval: int = 1,
        on_result: "ResultCallback | None" = None,
    ) -> TestRunSummary:
        """Run pending feature tests.

        Args:
            pending: Specific tests to run (default: all pending)
            save_interval: Save after every N tests
            on_result: Optional callback for each result

        Returns:
            Summary of test results
        """
        if pending is None:
            pending = self.get_pending_tests()

        # Sort tests to run dependencies first
        pending = topological_sort_tests(pending, self._feature_tests)

        summary = TestRunSummary()
        tests_since_save = 0

        for model_id, feature in pending:
            test = self._feature_tests.get(feature)
            if test is None:
                continue

            # Check dependencies first
            deps_met, failed_deps = self._check_dependencies(model_id, feature)
            if not deps_met:
                # Check if this was already skipped with same dependencies
                model_matrix = self.registry.registry.get_model(model_id)
                existing = model_matrix.features.get(feature) if model_matrix else None

                if (
                    existing
                    and existing.status == TestStatus.SKIPPED
                    and existing.metadata.get("reason") == "unmet_dependencies"
                    and set(existing.metadata.get("failed_dependencies", []))
                    == set(failed_deps)
                ):
                    # Still skipped with same reason - skip silently
                    summary.record(TestStatus.SKIPPED)
                    continue

                # New skip or skip reason changed
                print(f"  Testing {model_id} / {feature}...", end=" ", flush=True)
                result = FeatureTestResult(
                    status=TestStatus.SKIPPED,
                    metadata={
                        "reason": "unmet_dependencies",
                        "failed_dependencies": failed_deps,
                    },
                )
                self.registry.record_test_result(model_id, feature, result)
                summary.record(result.status)
                print(f"⊘ skipped (missing: {', '.join(failed_deps)})")

                if on_result:
                    on_result(model_id, feature, result)

                tests_since_save += 1
                if tests_since_save >= save_interval:
                    self.registry.save()
                    tests_since_save = 0
                continue

            print(f"  Testing {model_id} / {feature}...", end=" ", flush=True)

            try:
                result = test.test(model_id, self.client)
                self.registry.record_test_result(model_id, feature, result)
                summary.record(result.status)

                status_icon = {
                    TestStatus.SUPPORTED: "✓",
                    TestStatus.NOT_SUPPORTED: "✗",
                    TestStatus.UNAVAILABLE: "⚠",
                    TestStatus.ERROR: "!",
                    TestStatus.SKIPPED: "⊘",
                }[result.status]
                print(f"{status_icon} {result.status.value}")

                if on_result:
                    on_result(model_id, feature, result)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Saving progress...")
                self.registry.save()
                raise
            except Exception as e:
                error_result = FeatureTestResult(
                    status=TestStatus.ERROR, error_message=str(e)
                )
                self.registry.record_test_result(model_id, feature, error_result)
                summary.record(TestStatus.ERROR)
                print(f"! error: {e}")

            tests_since_save += 1
            if tests_since_save >= save_interval:
                self.registry.save()
                tests_since_save = 0

        self.registry.save()
        return summary
