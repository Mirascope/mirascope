#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mirascope[all]==2.2.2",
#     "pydantic>=2.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Iteration eval: LOO cross-validation with feedback-based program improvement.

Usage:
    ./run_iteration.py --sample SAMPLE.yaml --bootstrap RESULTS.json --output DIR

Requires all bootstrap queries to be annotated.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml
from mirascope import llm, ops
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class QueryExpected(BaseModel):
    invokes_skill: bool = True
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


class EvalSample(BaseModel):
    version: str = "1.0"
    skill_type: str
    sample_id: str
    created_at: str = ""
    metadata: SampleMetadata = Field(default_factory=SampleMetadata)
    bootstrap: Bootstrap
    queries: list[EvalQuery]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "EvalSample":
        with open(path) as f:
            return cls.model_validate(yaml.safe_load(f))


class QueryResult(BaseModel):
    query_id: str
    orchestrated_input: dict | None = None
    raw_output: str = ""
    trace_id: str | None = None
    span_id: str | None = None
    error: str | None = None


class Annotation(BaseModel):
    query_id: str
    acceptable: bool
    feedback: str = ""


class BootstrapResult(BaseModel):
    sample_id: str
    program_path: str
    program_code: str
    query_results: list[QueryResult]
    annotations: list[Annotation] = []

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "BootstrapResult":
        return cls.model_validate_json(Path(path).read_text())


class FoldResult(BaseModel):
    fold_index: int
    held_out_query_id: str
    program_code: str
    query_result: QueryResult
    annotation: Annotation | None = None


class IterationResult(BaseModel):
    sample_id: str
    folds: list[FoldResult]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "IterationResult":
        return cls.model_validate_json(Path(path).read_text())


# ---------------------------------------------------------------------------
# Program helpers
# ---------------------------------------------------------------------------


def _run_uv(program_path: str | Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    return subprocess.run(
        ["uv", "run", str(program_path), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def validate_program(program_path: str | Path) -> tuple[bool, str]:
    """Run --help and --schema to verify the program is well-formed."""
    path = Path(program_path)
    if not path.exists():
        return False, f"Program file not found: {path}"

    try:
        result = _run_uv(path, "--help")
        if result.returncode != 0:
            return False, f"--help failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "--help timed out"

    try:
        result = _run_uv(path, "--schema")
        if result.returncode != 0:
            return False, f"--schema failed: {result.stderr}"
        schema = json.loads(result.stdout)
        if "input" not in schema or "output" not in schema:
            return False, f"--schema missing 'input' or 'output' keys"
    except subprocess.TimeoutExpired:
        return False, "--schema timed out"
    except json.JSONDecodeError as e:
        return False, f"--schema returned invalid JSON: {e}"

    return True, ""


def get_schema(program_path: str | Path) -> dict:
    result = _run_uv(program_path, "--schema")
    if result.returncode != 0:
        raise RuntimeError(f"--schema failed: {result.stderr}")
    return json.loads(result.stdout)


def run_program(program_path: str | Path, input_json: str, timeout: int = 120) -> tuple[str, str]:
    result = _run_uv(program_path, "--input", input_json, timeout=timeout)
    return result.stdout, result.stderr


# ---------------------------------------------------------------------------
# LLM calls
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"


class ImprovedProgram(BaseModel):
    code: str = Field(description="Complete improved Python source code")


@ops.trace(tags=["eval", "iteration", "improve"])
@llm.call(DEFAULT_MODEL, format=ImprovedProgram)
def improve_program(original_code: str, training_examples: str, bootstrap_prompt: str) -> str:
    return f"""You are improving a Mirascope program based on human feedback.

Here is the original bootstrap request that created this program:

<bootstrap_request>
{bootstrap_prompt}
</bootstrap_request>

Here is the current program (v1):

<current_program>
{original_code}
</current_program>

Here are annotated results from running the program against test queries.
Each example shows: the query, the orchestrated input, the program output, whether it was acceptable, and human feedback.

<training_examples>
{training_examples}
</training_examples>

Based on this feedback, create an improved version of the program. Keep the same overall structure (PEP 723 deps, ProgramInput/ProgramOutput models, CLI flags, Mirascope decorators) but improve the prompt, models, or logic to address the feedback.

Return the complete improved Python source code."""


class OrchestrationResult(BaseModel):
    input_json: dict = Field(description="Structured input matching the program's schema")
    reasoning: str = Field(description="Explanation of how the query was translated")


@ops.trace(tags=["eval", "iteration", "orchestrate"])
@llm.call(DEFAULT_MODEL, format=OrchestrationResult)
def orchestrate_query(query_text: str, input_schema: dict) -> str:
    return f"""You are an orchestration layer that translates natural language queries into structured JSON input for a program.

The program accepts input matching this JSON schema:
{json.dumps(input_schema, indent=2)}

Translate the following user query into a valid JSON object matching the schema above.
If information is missing, use reasonable defaults. If the query doesn't relate to this program's purpose, set input_json to an empty object {{}}.

User query:
{query_text}

Return the structured input as input_json and explain your reasoning."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def format_training_examples(bootstrap: BootstrapResult, sample: EvalSample, exclude_query_id: str) -> str:
    """Format annotated results as training examples, excluding the held-out query."""
    annotations_by_id = {a.query_id: a for a in bootstrap.annotations}
    queries_by_id = {q.id: q for q in sample.queries}
    results_by_id = {r.query_id: r for r in bootstrap.query_results}

    lines: list[str] = []
    for qid, annotation in annotations_by_id.items():
        if qid == exclude_query_id:
            continue
        query = queries_by_id.get(qid)
        result = results_by_id.get(qid)
        if not query or not result:
            continue

        lines.append(f"--- Example: {qid} ---")
        lines.append(f"Query: {query.text.strip()}")
        if result.orchestrated_input:
            lines.append(f"Orchestrated input: {json.dumps(result.orchestrated_input)}")
        lines.append(f"Output: {result.raw_output.strip()}")
        lines.append(f"Acceptable: {'yes' if annotation.acceptable else 'no'}")
        if annotation.feedback:
            lines.append(f"Feedback: {annotation.feedback}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Iteration eval: LOO CV with feedback-based improvement"
    )
    parser.add_argument("--sample", required=True, help="Path to YAML eval sample")
    parser.add_argument("--bootstrap", required=True, help="Path to bootstrap results JSON (must be fully annotated)")
    parser.add_argument("--output", required=True, help="Output directory for results")
    args = parser.parse_args()

    # Initialize tracing (requires MIRASCOPE_API_KEY)
    ops.configure()
    ops.instrument_llm()

    sample = EvalSample.from_yaml(args.sample)
    bootstrap = BootstrapResult.load(args.bootstrap)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verify all annotations present
    annotated_ids = {a.query_id for a in bootstrap.annotations}
    query_ids = {q.id for q in sample.queries}
    missing = query_ids - annotated_ids
    if missing:
        print(f"Missing annotations for: {missing}", file=sys.stderr)
        print("All bootstrap queries must be annotated before running iteration eval.", file=sys.stderr)
        sys.exit(1)

    queries_by_id = {q.id: q for q in sample.queries}
    folds: list[FoldResult] = []

    for fold_idx, query in enumerate(sample.queries):
        print(f"\n{'='*60}")
        print(f"Fold {fold_idx}: held-out query = {query.id}")
        print(f"{'='*60}")

        fold_dir = output_dir / "folds" / f"fold_{fold_idx:02d}"
        fold_dir.mkdir(parents=True, exist_ok=True)

        training = format_training_examples(bootstrap, sample, exclude_query_id=query.id)

        with ops.session(id=f"eval-{sample.sample_id}-fold-{fold_idx}"):
            response = improve_program(
                original_code=bootstrap.program_code,
                training_examples=training,
                bootstrap_prompt=sample.bootstrap.prompt,
            )
            improved_code = response.parse().code

        program_path = fold_dir / "program.py"
        program_path.write_text(improved_code)
        print(f"  Improved program written to: {program_path}")

        valid, error = validate_program(program_path)
        if not valid:
            print(f"  Validation failed: {error}")
            folds.append(FoldResult(
                fold_index=fold_idx,
                held_out_query_id=query.id,
                program_code=improved_code,
                query_result=QueryResult(
                    query_id=query.id,
                    error=f"Program invalid: {error}",
                ),
            ))
            continue

        print("  Program validated")

        try:
            schema = get_schema(program_path)
            input_schema = schema["input"]

            with ops.session(id=f"eval-{sample.sample_id}-fold-{fold_idx}"):
                orch_response = orchestrate_query(query.text, input_schema)
                orch = orch_response.parse()
                orchestrated_input = orch.input_json
                print(f"  Orchestrated: {json.dumps(orchestrated_input)[:120]}")
        except Exception as e:
            folds.append(FoldResult(
                fold_index=fold_idx,
                held_out_query_id=query.id,
                program_code=improved_code,
                query_result=QueryResult(
                    query_id=query.id,
                    error=f"Orchestration failed: {e}",
                ),
            ))
            continue

        try:
            input_json_str = json.dumps(orchestrated_input)
            stdout, stderr = run_program(program_path, input_json_str)

            if stderr and not stdout:
                qr = QueryResult(
                    query_id=query.id,
                    orchestrated_input=orchestrated_input,
                    raw_output=stderr,
                    error=f"Program error: {stderr[:500]}",
                )
            else:
                qr = QueryResult(
                    query_id=query.id,
                    orchestrated_input=orchestrated_input,
                    raw_output=stdout,
                )
                print(f"  Output: {stdout[:120]}")
        except Exception as e:
            qr = QueryResult(
                query_id=query.id,
                orchestrated_input=orchestrated_input,
                error=f"Execution failed: {e}",
            )

        folds.append(FoldResult(
            fold_index=fold_idx,
            held_out_query_id=query.id,
            program_code=improved_code,
            query_result=qr,
        ))

    result = IterationResult(sample_id=sample.sample_id, folds=folds)
    result_path = output_dir / "iteration_results.json"
    result.save(result_path)
    print(f"\nResults saved to: {result_path}")
    print(f"Folds completed: {len(folds)}")
    print(f"Errors: {sum(1 for f in folds if f.query_result.error)}")


if __name__ == "__main__":
    main()
