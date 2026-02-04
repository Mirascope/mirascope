"""Evaluation framework for migration agent quality assessment."""

from __future__ import annotations

import ast
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, Field

from mirascope import llm, ops
from mirascope.cli.migrate.patterns import scan_file_for_patterns


class MigrationEvaluation(BaseModel):
    """Evaluation result from the LLM judge."""

    correctness_score: float = Field(
        ge=0, le=1, description="Syntactically valid Python, will it run?"
    )
    completeness_score: float = Field(
        ge=0, le=1, description="All v0/v1 patterns migrated?"
    )
    quality_score: float = Field(ge=0, le=1, description="Idiomatic v2 code?")
    safety_score: float = Field(
        ge=0, le=1, description="Comments/docstrings preserved, no unintended changes?"
    )
    overall_score: float = Field(
        ge=0, le=1, description="Weighted overall score (40/30/20/10)"
    )
    issues: list[str] = Field(default_factory=list, description="Specific issues found")
    suggestions: list[str] = Field(
        default_factory=list, description="Improvement suggestions"
    )


@ops.version(name="migration_judge")
@llm.call("anthropic/claude-sonnet-4-5", format=MigrationEvaluation)
def evaluate_migration(
    original_code: str, migrated_code: str, expected_patterns: list[str]
) -> str:
    """Evaluate a migration from v0/v1 to v2.

    Args:
        original_code: The original v0 or v1 code.
        migrated_code: The migrated v2 code.
        expected_patterns: The patterns that should have been migrated.

    Returns:
        MigrationEvaluation with scores and feedback.
    """
    return f"""You are evaluating a Mirascope code migration from v0/v1 to v2.

## Original Code (v0/v1):
```python
{original_code}
```

## Migrated Code (v2):
```python
{migrated_code}
```

## Expected patterns to migrate:
{expected_patterns}

## V2 Migration Rules:
- Imports: `from mirascope import llm` (not mirascope.openai or mirascope.core)
- Decorators: `@llm.call("provider/model")` instead of `@openai.call("model")`
- Tools: `@llm.tool` function-based instead of class-based BaseTool
- Response content: `.text()` method instead of `.content` property
- Streaming: `.stream().text_stream()` instead of `stream=True` in decorator
- Tool calls: `response.tool_calls` and `execute_tools()` instead of `.tool`
- Continuation: `response.resume(tool_outputs)` instead of `messages=response.messages`

## Evaluation Criteria:

1. **CORRECTNESS (40%)**: Is the migrated code syntactically valid Python? Will it run?
   - Check for syntax errors
   - Check for undefined names (imports present)
   - Check for type mismatches

2. **COMPLETENESS (30%)**: Are ALL v0/v1 patterns migrated?
   - Check that expected patterns are all converted
   - Look for any remaining legacy patterns
   - Verify all import statements updated

3. **QUALITY (20%)**: Is the code idiomatic v2?
   - Uses @llm.call("provider/model") format
   - Uses response.text() not response.content
   - Uses function-based tools with @llm.tool
   - Clean, readable code structure

4. **SAFETY (10%)**: Are comments/docstrings preserved? No unintended changes?
   - Original docstrings preserved
   - Comments preserved
   - Functionality unchanged
   - No extra code added

Provide scores 0-1 for each criterion.
Calculate overall_score as: 0.4*correctness + 0.3*completeness + 0.2*quality + 0.1*safety
List specific issues and suggestions for improvement."""


def _empty_str_list() -> list[str]:
    return []


@dataclass
class VerificationResult:
    """Result of programmatic verification checks."""

    syntax_valid: bool = False
    pyright_passed: bool = False
    pyright_errors: list[str] = field(default_factory=_empty_str_list)
    legacy_patterns_remaining: int = 0
    remaining_patterns: list[str] = field(default_factory=_empty_str_list)
    has_v2_imports: bool = False
    warnings: list[str] = field(default_factory=_empty_str_list)
    errors: list[str] = field(default_factory=_empty_str_list)


def verify_migration_programmatic(migrated_code: str) -> VerificationResult:
    """Run programmatic verification on migrated code.

    Args:
        migrated_code: The migrated Python code.

    Returns:
        VerificationResult with check outcomes.
    """
    result = VerificationResult()

    # 1. Syntax check via ast.parse()
    try:
        ast.parse(migrated_code)
        result.syntax_valid = True
    except SyntaxError as e:
        result.syntax_valid = False
        result.errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return result  # Can't continue if syntax is invalid

    # 2. Check for v2 imports
    if "from mirascope import llm" in migrated_code:
        result.has_v2_imports = True
    else:
        result.warnings.append("Missing 'from mirascope import llm' import")

    # 3. Pattern scan - check for remaining legacy patterns
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(migrated_code)
        tmp_path = Path(tmp_file.name)

    try:
        patterns = scan_file_for_patterns(tmp_path)
        result.legacy_patterns_remaining = len(patterns)
        result.remaining_patterns = list({p.pattern_type for p in patterns})

        if patterns:
            result.warnings.append(
                f"Legacy patterns still present: {result.remaining_patterns}"
            )

        # 4. Pyright check
        try:
            proc = subprocess.run(
                ["pyright", str(tmp_path), "--outputjson"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            result.pyright_passed = proc.returncode == 0
            if proc.returncode != 0:
                # Parse errors from pyright output
                import json

                try:
                    output = json.loads(proc.stdout)
                    for diag in output.get("generalDiagnostics", []):
                        result.pyright_errors.append(
                            f"Line {diag.get('range', {}).get('start', {}).get('line', '?')}: "
                            f"{diag.get('message', 'Unknown error')}"
                        )
                except json.JSONDecodeError:
                    result.pyright_errors.append(proc.stdout[:500])
        except FileNotFoundError:
            result.warnings.append("pyright not found, skipping type check")
            result.pyright_passed = True  # Don't fail if pyright not installed
        except subprocess.TimeoutExpired:
            result.warnings.append("pyright timed out")
            result.pyright_passed = True
    finally:
        tmp_path.unlink(missing_ok=True)

    return result


@dataclass
class CombinedEvaluation:
    """Combined evaluation from LLM judge and programmatic checks."""

    llm_evaluation: MigrationEvaluation
    verification: VerificationResult

    @property
    def overall_score(self) -> float:
        """Calculate overall score combining LLM and programmatic checks."""
        llm_score = self.llm_evaluation.overall_score

        # Apply penalties for programmatic failures
        penalty = 0.0
        if not self.verification.syntax_valid:
            penalty += 0.4  # Major penalty for syntax errors
        if not self.verification.pyright_passed:
            penalty += 0.2  # Penalty for type errors
        if self.verification.legacy_patterns_remaining > 0:
            penalty += 0.1 * min(
                self.verification.legacy_patterns_remaining, 3
            )  # Penalty per pattern

        return max(0.0, llm_score - penalty)

    @property
    def passed(self) -> bool:
        """Check if migration passes minimum quality bar."""
        return (
            self.verification.syntax_valid
            and self.verification.legacy_patterns_remaining == 0
            and self.overall_score >= 0.7
        )


def evaluate_migration_full(
    original_code: str,
    migrated_code: str,
    expected_patterns: list[str],
) -> CombinedEvaluation:
    """Run full evaluation combining LLM judge and programmatic checks.

    Args:
        original_code: Original v0/v1 code.
        migrated_code: Migrated v2 code.
        expected_patterns: Expected patterns that should be migrated.

    Returns:
        CombinedEvaluation with both LLM and programmatic results.
    """
    # Run programmatic verification first (fast)
    verification = verify_migration_programmatic(migrated_code)

    # Run LLM judge (slower, more nuanced)
    response = evaluate_migration(original_code, migrated_code, expected_patterns)
    llm_eval = response.parse()

    return CombinedEvaluation(
        llm_evaluation=llm_eval,
        verification=verification,
    )
