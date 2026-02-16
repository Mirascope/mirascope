#!/usr/bin/env -S uv run --python 3.13
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mirascope[all]>=2.0",
#     "pydantic>=2.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Full eval pipeline: bootstrap → score → iterate (leave-one-out) → report.

Usage:
    ./run_eval.py --sample samples/invoice_generator/sample_001.yaml --output results/eval_001/
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from mirascope import llm, ops
from mirascope.llm import SystemMessage, UserMessage, Text
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class QueryExpected(BaseModel):
    invokes_skill: bool = True
    invokes_tools: list[str] = []
    output_contains: list[str] = []
    output_excludes: list[str] = []
    semantic_requirements: list[str] = []


class EvalQuery(BaseModel):
    id: str
    text: str
    specificity: str = ""
    professionalism: str = ""
    expected: QueryExpected = Field(default_factory=QueryExpected)


class Bootstrap(BaseModel):
    prompt: str
    specificity: str = ""
    professionalism: str = ""
    expected_capabilities: list[str] = []


class SampleMetadata(BaseModel):
    description: str = ""
    tags: list[str] = []
    difficulty: str = "medium"


class TestState(BaseModel):
    today: str = ""
    existing_appointments: list[dict] = []


class EvalSample(BaseModel):
    version: str = "1.0"
    skill_type: str
    sample_id: str
    created_at: str = ""
    metadata: SampleMetadata = Field(default_factory=SampleMetadata)
    bootstrap: Bootstrap
    test_state: TestState = Field(default_factory=TestState)
    queries: list[EvalQuery]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "EvalSample":
        with open(path) as f:
            return cls.model_validate(yaml.safe_load(f))

    @property
    def is_agent(self) -> bool:
        return "agent" in self.skill_type.lower() or "agent" in self.metadata.tags


@dataclass
class QueryResult:
    query_id: str
    query_text: str
    orchestrated_input: dict | None = None
    raw_output: str = ""
    parsed_output: dict | None = None
    error: str | None = None
    # Scoring
    passed: bool = False
    score_details: dict = field(default_factory=dict)


@dataclass
class IterationResult:
    query_id: str
    initial_passed: bool
    improved_passed: bool
    improvement: str  # "none", "fixed", "regressed", "unchanged"


@dataclass
class EvalReport:
    sample_id: str
    skill_type: str
    timestamp: str
    # Phase 1
    program_generated: bool
    program_valid: bool
    # Phase 2
    initial_results: list[QueryResult]
    initial_pass_rate: float
    # Phase 3
    iteration_results: list[IterationResult]
    post_iteration_pass_rate: float
    # Summary
    queries_fixed: int
    queries_regressed: int

    def to_dict(self) -> dict:
        return {
            "sample_id": self.sample_id,
            "skill_type": self.skill_type,
            "timestamp": self.timestamp,
            "program_generated": self.program_generated,
            "program_valid": self.program_valid,
            "initial_pass_rate": self.initial_pass_rate,
            "post_iteration_pass_rate": self.post_iteration_pass_rate,
            "queries_fixed": self.queries_fixed,
            "queries_regressed": self.queries_regressed,
            "initial_results": [
                {
                    "query_id": r.query_id,
                    "passed": r.passed,
                    "error": r.error,
                    "score_details": r.score_details,
                }
                for r in self.initial_results
            ],
            "iteration_results": [
                {
                    "query_id": r.query_id,
                    "initial_passed": r.initial_passed,
                    "improved_passed": r.improved_passed,
                    "improvement": r.improvement,
                }
                for r in self.iteration_results
            ],
        }


# ---------------------------------------------------------------------------
# Program helpers
# ---------------------------------------------------------------------------

def run_uv(program_path: str | Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    # Ensure MIRASCOPE_API_KEY is passed to generated programs
    if "MIRASCOPE_API_KEY" not in env:
        env["MIRASCOPE_API_KEY"] = os.environ.get("MIRASCOPE_API_KEY", "")
    return subprocess.run(
        ["uv", "run", str(program_path), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def validate_program(program_path: Path) -> tuple[bool, str]:
    """Validate program with --help and --schema."""
    if not program_path.exists():
        return False, f"Program not found: {program_path}"

    try:
        result = run_uv(program_path, "--help")
        if result.returncode != 0:
            return False, f"--help failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "--help timed out"

    try:
        result = run_uv(program_path, "--schema")
        if result.returncode != 0:
            return False, f"--schema failed: {result.stderr}"
        schema = json.loads(result.stdout)
        if "input" not in schema or "output" not in schema:
            return False, f"Missing input/output in schema"
    except subprocess.TimeoutExpired:
        return False, "--schema timed out"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON from --schema: {e}"

    return True, ""


def get_schema(program_path: Path) -> dict:
    result = run_uv(program_path, "--schema")
    return json.loads(result.stdout)


def run_program(program_path: Path, input_json: str, timeout: int = 180) -> tuple[str, str]:
    result = run_uv(program_path, "--input", input_json, timeout=timeout)
    return result.stdout, result.stderr


# ---------------------------------------------------------------------------
# LLM Calls
# ---------------------------------------------------------------------------

SKILL_MD = Path(__file__).resolve().parent / "SKILL.md"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-20250514"


class GeneratedProgram(BaseModel):
    code: str = Field(description="Complete Python source code")


@ops.trace(tags=["eval", "generate"])
@llm.call(DEFAULT_MODEL, format=GeneratedProgram)
def generate_program(skill_instructions: str, bootstrap_prompt: str, is_agent: bool = False) -> list:
    if is_agent:
        user_content = f"""Create a complete, self-contained Mirascope TOOL-BASED AGENT program for:

<request>
{bootstrap_prompt}
</request>

Requirements:
1. PEP 723 inline deps with mirascope[all]
2. AgentInput (query field) and AgentOutput (response + tool_calls fields)
3. Tools with @llm.tool decorator
4. Agentic loop with execute_tools/resume
5. --help, --schema, --input CLI
6. Follow "Tool-Based Agent Programs" section
7. CRITICAL: Use model="anthropic/claude-sonnet-4-20250514" (exact string)"""
    else:
        user_content = f"""Create a complete, self-contained Mirascope program for:

<request>
{bootstrap_prompt}
</request>

Requirements:
1. PEP 723 inline deps with mirascope[all]
2. ProgramInput with a `prompt` field (natural language input from user)
3. ProgramOutput with structured fields for the result
4. @llm.call with format=ProgramOutput — the LLM extracts data from natural language
5. --help, --schema, --input CLI
6. Follow robustness patterns
7. CRITICAL: Use model="anthropic/claude-sonnet-4-20250514" (exact string)
8. CRITICAL: Input is ALWAYS natural language via prompt field, NOT pre-structured data"""

    return [
        SystemMessage(content=Text(text=f"You are a Mirascope program generator.\n\n<skill_instructions>\n{skill_instructions}\n</skill_instructions>")),
        UserMessage(content=[Text(text=user_content)]),
    ]


class ImprovedProgram(BaseModel):
    code: str = Field(description="Improved Python source code")
    changes: str = Field(description="What was changed and why")


@ops.trace(tags=["eval", "improve"])
@llm.call(DEFAULT_MODEL, format=ImprovedProgram)
def improve_program(
    skill_instructions: str,
    current_code: str,
    failures: list[dict],
    successes: list[dict],
    is_agent: bool = False,
) -> list:
    failure_text = "\n".join([
        f"- Query: {f['query'][:80]}...\n  Expected: {f['expected']}\n  Got: {f['actual'][:100]}..."
        for f in failures
    ])

    success_text = "\n".join([
        f"- Query: {s['query'][:80]}..."
        for s in successes
    ]) if successes else "(none)"

    return [
        SystemMessage(content=Text(text=f"You improve Mirascope programs based on feedback.\n\n<skill_instructions>\n{skill_instructions}\n</skill_instructions>")),
        UserMessage(content=[Text(text=f"""Current program:
```python
{current_code}
```

FAILING QUERIES (fix these):
{failure_text}

PASSING QUERIES (preserve these - do not break existing behavior):
{success_text}

CRITICAL: Make minimal, targeted changes. Do not refactor working code.
Fix the failing queries while ensuring passing queries continue to work.

Return the complete improved code.""")]),
    ]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_result(
    query: EvalQuery,
    raw_output: str,
    parsed_output: dict | None,
    is_agent: bool,
) -> tuple[bool, dict]:
    """Score a query result against expected behavior."""
    details = {"checks": [], "passed": [], "failed": []}

    if parsed_output is None:
        details["failed"].append("Failed to parse output as JSON")
        return False, details

    # Check output_contains
    output_str = raw_output.lower()
    for pattern in query.expected.output_contains:
        check = f"contains '{pattern}'"
        details["checks"].append(check)
        if pattern.lower() in output_str:
            details["passed"].append(check)
        else:
            details["failed"].append(check)

    # Check output_excludes
    for pattern in query.expected.output_excludes:
        check = f"excludes '{pattern}'"
        details["checks"].append(check)
        if pattern.lower() not in output_str:
            details["passed"].append(check)
        else:
            details["failed"].append(check)

    # Check invokes_tools (for agents)
    if is_agent and query.expected.invokes_tools:
        tool_calls = parsed_output.get("tool_calls", [])
        tools_called = {tc.get("tool") for tc in tool_calls if isinstance(tc, dict)}

        for expected_tool in query.expected.invokes_tools:
            check = f"invokes '{expected_tool}'"
            details["checks"].append(check)
            if expected_tool in tools_called:
                details["passed"].append(check)
            else:
                details["failed"].append(check)

    # Pass if no failures
    passed = len(details["failed"]) == 0
    return passed, details


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_queries(
    program_path: Path,
    sample: EvalSample,
    schema: dict,
) -> list[QueryResult]:
    """Run all queries against a program and return results."""
    results = []

    for query in sample.queries:
        # Build input — programs accept natural language via prompt/query field
        input_props = schema.get("input", {}).get("properties", {})
        if "query" in input_props:
            nl_field = "query"
        elif "prompt" in input_props:
            nl_field = "prompt"
        else:
            # Fallback: use first string field
            nl_field = next(
                (k for k, v in input_props.items() if v.get("type") == "string"),
                "prompt",
            )

        orchestrated_input: dict[str, Any] = {nl_field: query.text}

        # For agent samples, add context if the schema expects it
        if sample.is_agent and "context" in input_props:
            orchestrated_input["context"] = {
                "today": sample.test_state.today or "2025-02-15",
                "existing_appointments": sample.test_state.existing_appointments,
            }

        # Run program
        try:
            input_str = json.dumps(orchestrated_input)
            stdout, stderr = run_program(program_path, input_str)

            if stderr and not stdout:
                results.append(QueryResult(
                    query_id=query.id,
                    query_text=query.text,
                    orchestrated_input=orchestrated_input,
                    raw_output=stderr,
                    error=f"Program error: {stderr[:300]}",
                ))
                continue

            # Parse output
            try:
                parsed = json.loads(stdout)
            except json.JSONDecodeError:
                parsed = None

            # Score
            passed, score_details = score_result(query, stdout, parsed, sample.is_agent)

            results.append(QueryResult(
                query_id=query.id,
                query_text=query.text,
                orchestrated_input=orchestrated_input,
                raw_output=stdout,
                parsed_output=parsed,
                passed=passed,
                score_details=score_details,
            ))

        except Exception as e:
            results.append(QueryResult(
                query_id=query.id,
                query_text=query.text,
                orchestrated_input=orchestrated_input,
                error=f"Execution failed: {e}",
            ))

    return results


def run_full_eval(sample_path: Path, output_dir: Path) -> EvalReport:
    """Run the complete eval pipeline."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load sample
    sample = EvalSample.from_yaml(sample_path)
    skill_instructions = SKILL_MD.read_text()

    print(f"{'='*60}")
    print(f"EVAL: {sample.sample_id} ({sample.skill_type})")
    print(f"{'='*60}")

    timestamp = datetime.now().isoformat()

    # -------------------------------------------------------------------------
    # Phase 1: Bootstrap
    # -------------------------------------------------------------------------
    print("\n[Phase 1] Generating program...")

    try:
        response = generate_program(skill_instructions, sample.bootstrap.prompt, sample.is_agent)
        program_code = response.parse().code
        program_generated = True
    except Exception as e:
        print(f"  ✗ Generation failed: {e}")
        return EvalReport(
            sample_id=sample.sample_id,
            skill_type=sample.skill_type,
            timestamp=timestamp,
            program_generated=False,
            program_valid=False,
            initial_results=[],
            initial_pass_rate=0.0,
            iteration_results=[],
            post_iteration_pass_rate=0.0,
            queries_fixed=0,
            queries_regressed=0,
        )

    program_path = output_dir / "program_v0.py"
    program_path.write_text(program_code)
    print(f"  ✓ Program written to {program_path}")

    # Validate
    valid, error = validate_program(program_path)
    if not valid:
        print(f"  ✗ Validation failed: {error}")
        return EvalReport(
            sample_id=sample.sample_id,
            skill_type=sample.skill_type,
            timestamp=timestamp,
            program_generated=True,
            program_valid=False,
            initial_results=[],
            initial_pass_rate=0.0,
            iteration_results=[],
            post_iteration_pass_rate=0.0,
            queries_fixed=0,
            queries_regressed=0,
        )

    print("  ✓ Program validated")
    schema = get_schema(program_path)

    # -------------------------------------------------------------------------
    # Phase 2: Initial Eval
    # -------------------------------------------------------------------------
    print(f"\n[Phase 2] Running {len(sample.queries)} queries...")

    initial_results = run_queries(program_path, sample, schema)

    for r in initial_results:
        status = "✓" if r.passed else "✗"
        print(f"  {status} {r.query_id}: {r.query_text[:50]}...")
        if r.error:
            print(f"      Error: {r.error[:80]}")
        elif not r.passed and r.score_details.get("failed"):
            print(f"      Failed: {r.score_details['failed']}")

    initial_passed = sum(1 for r in initial_results if r.passed)
    initial_pass_rate = initial_passed / len(initial_results) if initial_results else 0
    print(f"\n  Initial: {initial_passed}/{len(initial_results)} ({initial_pass_rate:.0%})")

    # Save initial results
    (output_dir / "initial_results.json").write_text(json.dumps([
        {
            "query_id": r.query_id,
            "passed": r.passed,
            "error": r.error,
            "score_details": r.score_details,
            "raw_output": r.raw_output[:500] if r.raw_output else None,
        }
        for r in initial_results
    ], indent=2))

    # -------------------------------------------------------------------------
    # Phase 3: Leave-One-Out Cross Validation
    # -------------------------------------------------------------------------
    # For each query i:
    #   1. Use feedback from queries ≠i (from initial_results)
    #   2. Improve the BASE program (same starting point each time)
    #   3. Run ONLY query i on the improved program
    #   4. Record result
    # This gives unbiased estimation of post-iteration performance.
    # -------------------------------------------------------------------------
    print(f"\n[Phase 3] Leave-one-out cross validation...")

    iteration_results: list[IterationResult] = []

    for holdout_idx, holdout_query in enumerate(sample.queries):
        initial_passed_this = initial_results[holdout_idx].passed

        # Build feedback from N-1 queries (excluding holdout)
        failures = []
        successes = []
        for i, r in enumerate(initial_results):
            if i == holdout_idx:
                continue  # Exclude holdout to avoid leakage
            if r.passed:
                successes.append({"query": r.query_text})
            else:
                # Build expected description from query spec
                q = sample.queries[i]
                expected_parts = []
                if q.expected.output_contains:
                    expected_parts.append(f"output should contain: {q.expected.output_contains}")
                if q.expected.output_excludes:
                    expected_parts.append(f"output should NOT contain: {q.expected.output_excludes}")
                if q.expected.invokes_tools:
                    expected_parts.append(f"should invoke tools: {q.expected.invokes_tools}")
                expected = "; ".join(expected_parts) if expected_parts else "successful execution"
                
                actual = r.error if r.error else r.raw_output[:200] if r.raw_output else "no output"
                failures.append({
                    "query": r.query_text,
                    "expected": expected,
                    "actual": actual,
                })

        if not failures:
            # No failures in N-1 queries → no feedback to improve from
            iteration_results.append(IterationResult(
                query_id=holdout_query.id,
                initial_passed=initial_passed_this,
                improved_passed=initial_passed_this,
                improvement="unchanged",
            ))
            print(f"  {holdout_query.id}: No failures in other queries, skipping")
            continue

        # Improve BASE program (program_code) using skill
        # CRITICAL: Always start from same base, never chain improvements
        try:
            response = improve_program(
                skill_instructions, program_code, failures, successes, sample.is_agent
            )
            improved_code = response.parse().code
        except Exception as e:
            print(f"  {holdout_query.id}: Improvement failed: {e}")
            iteration_results.append(IterationResult(
                query_id=holdout_query.id,
                initial_passed=initial_passed_this,
                improved_passed=initial_passed_this,
                improvement="unchanged",
            ))
            continue

        # Save improved program for this holdout
        improved_path = output_dir / f"program_v1_holdout_{holdout_query.id}.py"
        improved_path.write_text(improved_code)

        # Validate improved program
        valid, error = validate_program(improved_path)
        if not valid:
            print(f"  {holdout_query.id}: Improved program invalid: {error}")
            iteration_results.append(IterationResult(
                query_id=holdout_query.id,
                initial_passed=initial_passed_this,
                improved_passed=False,
                improvement="regressed" if initial_passed_this else "unchanged",
            ))
            continue

        # Run ONLY the holdout query on improved program
        improved_schema = get_schema(improved_path)
        holdout_sample = EvalSample(
            skill_type=sample.skill_type,
            sample_id=sample.sample_id,
            bootstrap=sample.bootstrap,
            test_state=sample.test_state,
            queries=[holdout_query],
        )
        holdout_results = run_queries(improved_path, holdout_sample, improved_schema)
        
        improved_passed = holdout_results[0].passed if holdout_results else False

        # Determine improvement status
        if initial_passed_this and improved_passed:
            improvement = "unchanged"
            print(f"  {holdout_query.id}: - unchanged (still passing)")
        elif not initial_passed_this and improved_passed:
            improvement = "fixed"
            print(f"  {holdout_query.id}: ✓ FIXED")
        elif initial_passed_this and not improved_passed:
            improvement = "regressed"
            print(f"  {holdout_query.id}: ✗ REGRESSED")
        else:
            improvement = "unchanged"
            print(f"  {holdout_query.id}: - unchanged (still failing)")

        iteration_results.append(IterationResult(
            query_id=holdout_query.id,
            initial_passed=initial_passed_this,
            improved_passed=improved_passed,
            improvement=improvement,
        ))

    # -------------------------------------------------------------------------
    # Phase 4: Report
    # -------------------------------------------------------------------------
    print(f"\n[Phase 4] Generating report...")

    queries_fixed = sum(1 for r in iteration_results if r.improvement == "fixed")
    queries_regressed = sum(1 for r in iteration_results if r.improvement == "regressed")
    post_passed = sum(1 for r in iteration_results if r.improved_passed)
    post_pass_rate = post_passed / len(iteration_results) if iteration_results else 0

    report = EvalReport(
        sample_id=sample.sample_id,
        skill_type=sample.skill_type,
        timestamp=timestamp,
        program_generated=True,
        program_valid=True,
        initial_results=initial_results,
        initial_pass_rate=initial_pass_rate,
        iteration_results=iteration_results,
        post_iteration_pass_rate=post_pass_rate,
        queries_fixed=queries_fixed,
        queries_regressed=queries_regressed,
    )

    report_path = output_dir / "report.json"
    report_path.write_text(json.dumps(report.to_dict(), indent=2))

    print(f"\n{'='*60}")
    print(f"RESULTS: {sample.sample_id}")
    print(f"{'='*60}")
    print(f"  Initial:        {initial_passed}/{len(initial_results)} ({initial_pass_rate:.0%})")
    print(f"  Post-iteration: {post_passed}/{len(iteration_results)} ({post_pass_rate:.0%})")
    print(f"  Fixed:          {queries_fixed}")
    print(f"  Regressed:      {queries_regressed}")
    print(f"\n  Report: {report_path}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Run full eval pipeline")
    parser.add_argument("--sample", required=True, help="Path to sample YAML")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()

    ops.configure()
    ops.instrument_llm()

    report = run_full_eval(Path(args.sample), Path(args.output))
    sys.exit(0 if report.initial_pass_rate == 1.0 else 1)


if __name__ == "__main__":
    main()
