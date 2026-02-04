"""Evaluation runner for migration agent quality assessment."""

from __future__ import annotations

import contextlib
import tempfile

# TEMPORARY: Patch closure computation to include mirascope.cli.* modules
# This allows versioning of CLI code for development/testing purposes
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

from mirascope import ops
from mirascope.cli.migrate.evaluation import (
    CombinedEvaluation,
    evaluate_migration_full,
)
from mirascope.ops._internal import closure as _closure_module

_original_is_third_party = _closure_module._is_third_party  # pyright: ignore[reportPrivateUsage]


def _patched_is_third_party(module: ModuleType, site_packages: set[str]) -> bool:
    """Allow mirascope.cli.* modules to be included in closures."""
    # Allow CLI modules for eval/testing, but still exclude mirascope.ops/llm
    # to avoid traversing into VersionedCall objects
    name = module.__name__
    if name.startswith("mirascope.cli."):
        return False
    # Keep mirascope.ops, mirascope.llm, etc. as third-party
    if name.startswith("mirascope."):
        return True
    return _original_is_third_party(module, site_packages)


_closure_module._is_third_party = _patched_is_third_party  # pyright: ignore[reportPrivateUsage]

# Also patch _DependencyCollector._get_source_code to handle objects without __qualname__
_original_get_source_code = _closure_module._DependencyCollector._get_source_code  # pyright: ignore[reportPrivateUsage]


def _patched_get_source_code(
    self: _closure_module._DependencyCollector,  # pyright: ignore[reportPrivateUsage]
    definition: Callable[..., Any],
) -> str | None:
    """Handle objects without __qualname__ (like VersionedCall)."""
    if not hasattr(definition, "__qualname__"):
        return None
    return _original_get_source_code(self, definition)


_closure_module._DependencyCollector._get_source_code = _patched_get_source_code  # pyright: ignore[reportPrivateUsage]

# Configure ops and enable full LLM instrumentation for Cloud tracing
ops.configure()
ops.instrument_llm()

if TYPE_CHECKING:
    from mirascope.cli.migrate.test_data import MigrationTestCase


def _empty_str_list() -> list[str]:
    return []


def _empty_eval_result_list() -> list[EvaluationResult]:
    return []


@dataclass
class EvaluationResult:
    """Result for a single test case evaluation."""

    test_case_name: str
    """Name of the test case."""

    migrated_code: str | None
    """The migrated code, or None if migration failed."""

    evaluation: CombinedEvaluation | None
    """Full evaluation, or None if migration failed."""

    error: str | None = None
    """Error message if migration or evaluation failed."""

    @property
    def passed(self) -> bool:
        """Check if this test case passed."""
        if self.evaluation is None:
            return False
        return self.evaluation.passed

    @property
    def score(self) -> float:
        """Get the overall score for this test case."""
        if self.evaluation is None:
            return 0.0
        return self.evaluation.overall_score


@dataclass
class EvaluationReport:
    """Aggregated report of evaluation results."""

    results: list[EvaluationResult] = field(default_factory=_empty_eval_result_list)
    """Individual results for each test case."""

    total_cases: int = 0
    """Total number of test cases evaluated."""

    passed_cases: int = 0
    """Number of test cases that passed."""

    failed_cases: int = 0
    """Number of test cases that failed."""

    error_cases: int = 0
    """Number of test cases that had errors."""

    average_score: float = 0.0
    """Average overall score across all test cases."""

    average_correctness: float = 0.0
    """Average correctness score."""

    average_completeness: float = 0.0
    """Average completeness score."""

    average_quality: float = 0.0
    """Average quality score."""

    average_safety: float = 0.0
    """Average safety score."""

    failed_patterns: list[str] = field(default_factory=_empty_str_list)
    """Patterns that commonly failed to migrate."""

    common_issues: list[str] = field(default_factory=_empty_str_list)
    """Most common issues found across evaluations."""


def _run_migration_on_code(input_code: str) -> str:
    """Run the migration agent on a single code snippet.

    This creates a temporary directory with the code and runs
    the migration agent on it, returning the migrated code.

    Args:
        input_code: The v0/v1 code to migrate.

    Returns:
        The migrated v2 code.

    Raises:
        RuntimeError: If migration fails.
    """
    from mirascope.cli.migrate.agent import run_migration_agent

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Write input code to a file
        input_file = tmp_path / "code.py"
        input_file.write_text(input_code)

        # Run migration (not dry-run, auto-approve)
        with contextlib.suppress(SystemExit):
            run_migration_agent(
                path=str(tmp_path),
                model_id="anthropic/claude-sonnet-4-5",
                dry_run=False,
                auto_approve=True,
                verbose=False,
            )

        # Read the migrated code
        if input_file.exists():
            return input_file.read_text()
        raise RuntimeError("Migration failed: output file not found")


def evaluate_single_case(test_case: MigrationTestCase) -> EvaluationResult:
    """Evaluate a single test case.

    Args:
        test_case: The test case to evaluate.

    Returns:
        EvaluationResult with the outcome.
    """
    try:
        # Run migration
        migrated_code = _run_migration_on_code(test_case.input_code)

        # Run full evaluation
        evaluation = evaluate_migration_full(
            original_code=test_case.input_code,
            migrated_code=migrated_code,
            expected_patterns=test_case.expected_patterns,
        )

        return EvaluationResult(
            test_case_name=test_case.name,
            migrated_code=migrated_code,
            evaluation=evaluation,
        )

    except Exception as e:
        return EvaluationResult(
            test_case_name=test_case.name,
            migrated_code=None,
            evaluation=None,
            error=str(e),
        )


def _aggregate_results(results: list[EvaluationResult]) -> EvaluationReport:
    """Aggregate individual results into a report.

    Args:
        results: List of individual evaluation results.

    Returns:
        Aggregated EvaluationReport.
    """
    report = EvaluationReport(results=results, total_cases=len(results))

    # Count outcomes
    scores: list[float] = []
    correctness_scores: list[float] = []
    completeness_scores: list[float] = []
    quality_scores: list[float] = []
    safety_scores: list[float] = []
    all_issues: list[str] = []
    failed_pattern_counts: dict[str, int] = {}

    for result in results:
        if result.error:
            report.error_cases += 1
        elif result.passed:
            report.passed_cases += 1
        else:
            report.failed_cases += 1

        if result.evaluation:
            scores.append(result.evaluation.overall_score)
            llm_eval = result.evaluation.llm_evaluation
            correctness_scores.append(llm_eval.correctness_score)
            completeness_scores.append(llm_eval.completeness_score)
            quality_scores.append(llm_eval.quality_score)
            safety_scores.append(llm_eval.safety_score)
            all_issues.extend(llm_eval.issues)

            # Track remaining legacy patterns
            for pattern in result.evaluation.verification.remaining_patterns:
                failed_pattern_counts[pattern] = (
                    failed_pattern_counts.get(pattern, 0) + 1
                )

    # Calculate averages
    if scores:
        report.average_score = sum(scores) / len(scores)
    if correctness_scores:
        report.average_correctness = sum(correctness_scores) / len(correctness_scores)
    if completeness_scores:
        report.average_completeness = sum(completeness_scores) / len(
            completeness_scores
        )
    if quality_scores:
        report.average_quality = sum(quality_scores) / len(quality_scores)
    if safety_scores:
        report.average_safety = sum(safety_scores) / len(safety_scores)

    # Find most common failed patterns
    report.failed_patterns = sorted(
        failed_pattern_counts.keys(),
        key=lambda p: failed_pattern_counts[p],
        reverse=True,
    )[:5]

    # Find most common issues
    issue_counts: dict[str, int] = {}
    for issue in all_issues:
        issue_counts[issue] = issue_counts.get(issue, 0) + 1
    report.common_issues = sorted(
        issue_counts.keys(),
        key=lambda i: issue_counts[i],
        reverse=True,
    )[:5]

    return report


@ops.version(name="eval_runner")
def run_evaluation(test_cases: list[MigrationTestCase]) -> EvaluationReport:
    """Run migration agent on test cases and evaluate results.

    Args:
        test_cases: List of test cases to evaluate.

    Returns:
        EvaluationReport with aggregated results.
    """
    results: list[EvaluationResult] = []

    for test_case in test_cases:
        result = evaluate_single_case(test_case)
        results.append(result)

    return _aggregate_results(results)


def run_quick_evaluation(
    n_cases: int = 5,
    difficulty: str | None = None,
    v0_only: bool = False,
    v1_only: bool = False,
) -> EvaluationReport:
    """Run a quick evaluation on a subset of test cases.

    Args:
        n_cases: Number of test cases to run.
        difficulty: Optional difficulty filter ("simple", "medium", "complex").
        v0_only: Only include v0 test cases.
        v1_only: Only include v1 test cases.

    Returns:
        EvaluationReport with results.
    """
    from mirascope.cli.migrate.test_data import (
        get_all_test_cases,
        get_test_cases_by_difficulty,
    )

    if difficulty:
        cases = get_test_cases_by_difficulty(
            difficulty=difficulty,
            include_examples=False,
            include_synthetic=True,
        )
    else:
        cases = get_all_test_cases(
            include_examples=False,
            include_synthetic=True,
            v0_only=v0_only,
            v1_only=v1_only,
        )

    # Limit to n_cases
    cases = cases[:n_cases]

    return run_evaluation(cases)


def print_report(report: EvaluationReport) -> None:
    """Print a formatted evaluation report.

    Args:
        report: The evaluation report to print.
    """
    from mirascope.cli.migrate.ui import console

    console.print("\n[bold]Migration Agent Evaluation Report[/bold]")
    console.print("=" * 50)

    console.print("\n[cyan]Summary:[/cyan]")
    console.print(f"  Total cases:  {report.total_cases}")
    console.print(f"  Passed:       [green]{report.passed_cases}[/green]")
    console.print(f"  Failed:       [yellow]{report.failed_cases}[/yellow]")
    console.print(f"  Errors:       [red]{report.error_cases}[/red]")

    console.print("\n[cyan]Scores:[/cyan]")
    console.print(f"  Overall:      {report.average_score:.2%}")
    console.print(f"  Correctness:  {report.average_correctness:.2%}")
    console.print(f"  Completeness: {report.average_completeness:.2%}")
    console.print(f"  Quality:      {report.average_quality:.2%}")
    console.print(f"  Safety:       {report.average_safety:.2%}")

    if report.failed_patterns:
        console.print("\n[cyan]Most Common Failed Patterns:[/cyan]")
        for pattern in report.failed_patterns:
            console.print(f"  - {pattern}")

    if report.common_issues:
        console.print("\n[cyan]Most Common Issues:[/cyan]")
        for issue in report.common_issues[:3]:
            console.print(f"  - {issue[:80]}...")

    console.print("\n" + "=" * 50)
