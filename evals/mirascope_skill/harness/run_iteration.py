"""Iteration eval: LOO cross-validation with feedback-based program improvement.

Usage:
    python -m harness.run_iteration --sample YAML --bootstrap JSON --output DIR [--model MODEL]

Requires all bootstrap queries to be annotated.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mirascope import llm, ops
from pydantic import BaseModel

from .models import (
    BootstrapResult,
    EvalSample,
    FoldResult,
    IterationResult,
    QueryResult,
)
from .program import get_schema, run_program, validate_program

DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"

# Initialize Mirascope tracing
ops.configure()
ops.instrument_llm()


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------


class ImprovedProgram(BaseModel):
    code: str


@ops.trace(tags=["eval", "iteration", "improve"])
@llm.call(DEFAULT_MODEL, format=ImprovedProgram)
def improve_program(
    original_code: str,
    training_examples: str,
    bootstrap_prompt: str,
) -> str:
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
    input_json: dict
    reasoning: str


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
# Main
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Iteration eval: LOO CV with feedback-based improvement"
    )
    parser.add_argument("--sample", required=True, help="Path to YAML eval sample")
    parser.add_argument("--bootstrap", required=True, help="Path to bootstrap results JSON (must be fully annotated)")
    parser.add_argument("--output", required=True, help="Output directory for results")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"LLM model (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

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

        # Build training examples (exclude held-out query)
        training = format_training_examples(bootstrap, sample, exclude_query_id=query.id)

        # Generate improved program
        with ops.session(id=f"eval-{sample.sample_id}-fold-{fold_idx}"):
            response = improve_program(
                original_code=bootstrap.program_code,
                training_examples=training,
                bootstrap_prompt=sample.bootstrap.prompt,
            )
            improved_code = response.parse().code

        # Write improved program
        program_path = fold_dir / "program.py"
        program_path.write_text(improved_code)
        print(f"  Improved program written to: {program_path}")

        # Validate
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

        # Get schema and orchestrate held-out query
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

        # Run held-out query
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

    # Save results
    result = IterationResult(sample_id=sample.sample_id, folds=folds)
    result_path = output_dir / "iteration_results.json"
    result.save(result_path)
    print(f"\nResults saved to: {result_path}")
    print(f"Folds completed: {len(folds)}")
    print(f"Errors: {sum(1 for f in folds if f.query_result.error)}")


if __name__ == "__main__":
    main()
