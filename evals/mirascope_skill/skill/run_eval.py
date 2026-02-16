#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mirascope[all]>=2.0",
#     "pydantic>=2.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Eval pipeline with human-in-the-loop scoring via Mirascope trace annotations.

Subcommands:
    run       Generate program from sample + run all queries (creates traces)
    iterate   Read annotations from traces, run LKO improvement
    report    Compute pass rates from annotations

Workflow:
    1. ./run_eval.py run --sample samples/invoice_generator/sample_001.yaml --output results/eval_001/
    2. Review traces in Mirascope Cloud, annotate pass/fail with reasoning
    3. ./run_eval.py iterate --output results/eval_001/ [--k 1]
    4. Annotate new traces
    5. ./run_eval.py report --output results/eval_001/

Requires MIRASCOPE_API_KEY env var.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from mirascope import llm, ops
from mirascope.api.client import get_sync_client
from mirascope.llm import SystemMessage, UserMessage, Text
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class EvalQuery(BaseModel):
    id: str
    text: str


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
            raw = yaml.safe_load(f)
        # Strip expected fields from queries — scoring is human-only
        for q in raw.get("queries", []):
            q.pop("expected", None)
        return cls.model_validate(raw)

    @property
    def is_agent(self) -> bool:
        return "agent" in self.skill_type.lower() or "agent" in self.metadata.tags


@dataclass
class QueryRun:
    """Result of running a single query against the program."""
    query_id: str
    query_text: str
    input_json: dict
    raw_output: str = ""
    error: str | None = None
    run_start: str = ""
    run_end: str = ""
    # Filled after trace lookup
    trace_id: str | None = None
    span_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "input_json": self.input_json,
            "raw_output": self.raw_output,
            "error": self.error,
            "run_start": self.run_start,
            "run_end": self.run_end,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }


@dataclass
class EvalState:
    """Persistent state for an eval run, saved to state.json."""
    sample_path: str
    sample_id: str
    skill_type: str
    is_agent: bool
    program_path: str
    phase: str  # "generated", "ran", "iterated"
    run_start: str = ""
    run_end: str = ""
    initial_runs: list[dict] = field(default_factory=list)
    iteration_runs: list[dict] = field(default_factory=list)  # LKO results
    iteration_k: int = 1

    def save(self, output_dir: Path) -> None:
        (output_dir / "state.json").write_text(json.dumps(self.__dict__, indent=2))

    @classmethod
    def load(cls, output_dir: Path) -> "EvalState":
        data = json.loads((output_dir / "state.json").read_text())
        return cls(**data)


# ---------------------------------------------------------------------------
# Program helpers
# ---------------------------------------------------------------------------

def run_uv(program_path: str | Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
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
            return False, "Missing input/output in schema"
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
7. CRITICAL: Use model="anthropic/claude-sonnet-4-20250514" (exact string)
8. CRITICAL: Include ops.configure() and @ops.trace on the main function"""
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
8. CRITICAL: Input is ALWAYS natural language via prompt field, NOT pre-structured data
9. CRITICAL: Include ops.configure() and @ops.trace on the main function"""

    return [
        SystemMessage(content=Text(text=f"You are a Mirascope program generator.\n\n<skill_instructions>\n{skill_instructions}\n</skill_instructions>")),
        UserMessage(content=[Text(text=user_content)]),
    ]


class ImprovedProgram(BaseModel):
    code: str = Field(description="Improved Python source code")
    changes: str = Field(description="What was changed and why")


@llm.call(DEFAULT_MODEL, format=ImprovedProgram)
def improve_program(
    skill_instructions: str,
    current_code: str,
    annotations: list[dict],
    is_agent: bool = False,
) -> list:
    """Improve a program based on human annotations from traces."""
    feedback_text = ""
    for a in annotations:
        label = a.get("label", "unknown")
        reasoning = a.get("reasoning", "")
        query = a.get("query", "")
        output = a.get("output", "")
        feedback_text += f"\n### Query: {query}\n"
        feedback_text += f"**Label:** {label}\n"
        if reasoning:
            feedback_text += f"**Feedback:** {reasoning}\n"
        feedback_text += f"**Program output:**\n```\n{output}\n```\n"

    return [
        SystemMessage(content=Text(text=f"You improve Mirascope programs based on human feedback.\n\n<skill_instructions>\n{skill_instructions}\n</skill_instructions>")),
        UserMessage(content=[Text(text=f"""Here is a Mirascope program that needs improvement:

```python
{current_code}
```

## Human Annotations
Reviewers tested this program and provided feedback on each query's output.
Study the feedback carefully — "fail" annotations explain what's wrong.
"pass" annotations show correct behavior to preserve.
{feedback_text}

## Instructions
1. **Diagnose first:** For each failure, identify the root cause (prompt wording? missing field? wrong logic?)
2. **Make targeted fixes:** Change only what's needed to fix failures. Do not restructure working code.
3. **Verify mentally:** For each passing query, confirm your changes won't break it.
4. **Return the complete improved program** (full file, not a diff).""")]),
    ]


# ---------------------------------------------------------------------------
# Trace helpers
# ---------------------------------------------------------------------------

def find_traces_for_runs(
    runs: list[QueryRun],
    start_time: str,
    end_time: str,
) -> list[QueryRun]:
    """Match query runs to their traces via the Mirascope API."""
    client = get_sync_client()

    # Search for all traces in the time window
    response = client.traces.search(
        start_time=start_time,
        end_time=end_time,
        limit=len(runs) * 3,  # buffer for extra traces
        root_spans_only=True,
    )

    # For each trace, get detail and try to match to a run by input content
    matched = set()
    for span in response.spans:
        try:
            detail = client.traces.gettracedetail(trace_id=span.trace_id)
            for detail_span in detail.spans:
                attrs = json.loads(detail_span.attributes) if detail_span.attributes else {}
                # Look for input content in attributes
                input_str = json.dumps(attrs)

                for run in runs:
                    if run.query_id in matched:
                        continue
                    # Match by checking if the query text appears in the trace input
                    if run.query_text[:50] in input_str:
                        run.trace_id = span.trace_id
                        run.span_id = span.span_id
                        matched.add(run.query_id)
                        break
        except Exception:
            continue

    return runs


def get_annotations_for_run(run: QueryRun, local_annotations: dict[str, dict] | None = None) -> dict | None:
    """Get the annotation for a specific trace. Falls back to local annotations."""
    # Try API first
    if run.trace_id and run.span_id:
        try:
            client = get_sync_client()
            response = client.annotations.list(
                otel_trace_id=run.trace_id,
                otel_span_id=run.span_id,
                limit=1,
            )
            annotations = response if isinstance(response, list) else getattr(response, "items", [])
            if annotations:
                ann = annotations[0]
                return {
                    "label": getattr(ann, "label", None),
                    "reasoning": getattr(ann, "reasoning", None),
                    "query": run.query_text,
                    "output": run.raw_output,
                }
        except Exception:
            pass

    # Fall back to local annotations
    if local_annotations and run.query_id in local_annotations:
        local = local_annotations[run.query_id]
        return {
            "label": local["label"],
            "reasoning": local.get("reasoning"),
            "query": run.query_text,
            "output": run.raw_output,
        }

    return None


def load_local_annotations(output_dir: Path, phase: str) -> dict[str, dict]:
    """Load local annotation file as {query_id: annotation} map."""
    ann_file = output_dir / f"annotations_{phase}.json"
    if ann_file.exists():
        annotations = json.loads(ann_file.read_text())
        return {a["query_id"]: a for a in annotations}
    return {}


# ---------------------------------------------------------------------------
# Subcommand: run
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> None:
    """Generate program + run all queries."""
    sample_path = Path(args.sample)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    sample = EvalSample.from_yaml(sample_path)
    skill_instructions = SKILL_MD.read_text()

    print(f"{'='*60}")
    print(f"EVAL: {sample.sample_id} ({sample.skill_type})")
    print(f"{'='*60}")

    # Phase 1: Generate program
    print("\n[Phase 1] Generating program...")
    try:
        response = generate_program(skill_instructions, sample.bootstrap.prompt, sample.is_agent)
        program_code = response.parse().code
    except Exception as e:
        print(f"  ✗ Generation failed: {e}")
        sys.exit(1)

    program_path = output_dir / "program.py"
    program_path.write_text(program_code)
    print(f"  ✓ Program written to {program_path}")

    valid, error = validate_program(program_path)
    if not valid:
        print(f"  ✗ Validation failed: {error}")
        sys.exit(1)
    print("  ✓ Program validated")

    schema = get_schema(program_path)

    # Phase 2: Run all queries
    print(f"\n[Phase 2] Running {len(sample.queries)} queries...")

    # Determine the natural language input field name
    input_props = schema.get("input", {}).get("properties", {})
    if "query" in input_props:
        nl_field = "query"
    elif "prompt" in input_props:
        nl_field = "prompt"
    else:
        nl_field = next(
            (k for k, v in input_props.items() if v.get("type") == "string"),
            "prompt",
        )

    batch_start = datetime.now(timezone.utc).isoformat()

    def _run_query(query: EvalQuery) -> QueryRun:
        input_data: dict[str, Any] = {nl_field: query.text}
        # For agent samples, add context if schema expects it
        if sample.is_agent and "context" in input_props:
            input_data["context"] = {
                "today": sample.test_state.today or "2025-02-15",
                "existing_appointments": sample.test_state.existing_appointments,
            }

        run_start = datetime.now(timezone.utc).isoformat()
        try:
            input_str = json.dumps(input_data)
            stdout, stderr = run_program(program_path, input_str)
            run_end = datetime.now(timezone.utc).isoformat()

            if stderr and not stdout.strip():
                return QueryRun(
                    query_id=query.id,
                    query_text=query.text,
                    input_json=input_data,
                    raw_output=stderr,
                    error=f"Program error: {stderr[:300]}",
                    run_start=run_start,
                    run_end=run_end,
                )

            return QueryRun(
                query_id=query.id,
                query_text=query.text,
                input_json=input_data,
                raw_output=stdout,
                run_start=run_start,
                run_end=run_end,
            )
        except Exception as e:
            return QueryRun(
                query_id=query.id,
                query_text=query.text,
                input_json=input_data,
                error=f"Execution failed: {e}",
                run_start=run_start,
                run_end=datetime.now(timezone.utc).isoformat(),
            )

    # Run in parallel
    max_workers = min(len(sample.queries), 10)
    runs: list[QueryRun] = [None] * len(sample.queries)  # type: ignore

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(_run_query, q): i
            for i, q in enumerate(sample.queries)
        }
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            run = future.result()
            runs[idx] = run
            status = "✗" if run.error else "✓"
            print(f"  {status} {run.query_id}: {run.query_text[:50]}...")

    batch_end = datetime.now(timezone.utc).isoformat()

    # Wait for traces to be exported (batch processor flushes async)
    print("\n  Waiting for traces to export...")
    time.sleep(5)

    # Match runs to traces
    print("  Matching runs to traces...")
    runs = find_traces_for_runs(runs, batch_start, batch_end)
    matched = sum(1 for r in runs if r.trace_id)
    print(f"  Matched {matched}/{len(runs)} runs to traces")

    # Save state
    state = EvalState(
        sample_path=str(sample_path),
        sample_id=sample.sample_id,
        skill_type=sample.skill_type,
        is_agent=sample.is_agent,
        program_path=str(program_path),
        phase="ran",
        run_start=batch_start,
        run_end=batch_end,
        initial_runs=[r.to_dict() for r in runs],
    )
    state.save(output_dir)

    # Print summary
    print(f"\n{'='*60}")
    print(f"QUERIES RUN: {len(runs)}")
    print(f"TRACES MATCHED: {matched}")
    print(f"{'='*60}")
    print(f"\nOutputs saved to {output_dir}/state.json")
    print(f"Next: ./run_eval.py annotate --output {output_dir} --phase initial [--file annotations.json]")
    print(f"Then: ./run_eval.py iterate --output {output_dir}")


# ---------------------------------------------------------------------------
# Subcommand: iterate
# ---------------------------------------------------------------------------

def cmd_iterate(args: argparse.Namespace) -> None:
    """Read annotations, run LKO improvement."""
    output_dir = Path(args.output)
    state = EvalState.load(output_dir)
    k = args.k

    sample = EvalSample.from_yaml(state.sample_path)
    skill_instructions = SKILL_MD.read_text()
    program_code = Path(state.program_path).read_text()

    print(f"{'='*60}")
    print(f"LKO ITERATION (k={k}): {state.sample_id}")
    print(f"{'='*60}")

    # Reconstruct runs and get annotations
    runs = [QueryRun(**r) for r in state.initial_runs]

    print("\n[1] Reading annotations...")
    local_anns = load_local_annotations(output_dir, "initial")
    annotations = {}
    for run in runs:
        ann = get_annotations_for_run(run, local_anns)
        if ann:
            annotations[run.query_id] = ann
            label = ann["label"]
            print(f"  {run.query_id}: {label}")
        else:
            print(f"  {run.query_id}: (no annotation)")

    if not annotations:
        print("\n  ✗ No annotations found. Annotate traces first.")
        sys.exit(1)

    annotated_count = len(annotations)
    print(f"\n  Found {annotated_count}/{len(runs)} annotations")

    # Check all runs are annotated
    unannotated = [r.query_id for r in runs if r.query_id not in annotations]
    if unannotated:
        print(f"  ⚠ Unannotated queries: {', '.join(unannotated)}")
        print("  Continuing with available annotations...")

    # Build LKO groups
    query_ids = [r.query_id for r in runs if r.query_id in annotations]
    groups = [query_ids[i:i + k] for i in range(0, len(query_ids), k)]

    print(f"\n[2] Running {len(groups)} LKO iterations (k={k})...")

    schema = get_schema(Path(state.program_path))
    input_props = schema.get("input", {}).get("properties", {})
    if "query" in input_props:
        nl_field = "query"
    elif "prompt" in input_props:
        nl_field = "prompt"
    else:
        nl_field = next(
            (k_name for k_name, v in input_props.items() if v.get("type") == "string"),
            "prompt",
        )

    iteration_batch_start = datetime.now(timezone.utc).isoformat()

    def _run_lko_group(group_idx: int, held_out_ids: list[str]) -> list[QueryRun]:
        """Run a single LKO iteration for held-out group."""
        # Build feedback from N-K annotations
        train_annotations = [
            annotations[qid] for qid in query_ids if qid not in held_out_ids
        ]

        # Improve program
        try:
            response = improve_program(
                skill_instructions, program_code, train_annotations, state.is_agent
            )
            improved_code = response.parse().code
        except Exception as e:
            print(f"  Group {group_idx}: improvement failed: {e}")
            return [
                QueryRun(
                    query_id=qid,
                    query_text=next(r.query_text for r in runs if r.query_id == qid),
                    input_json={},
                    error=f"Improvement failed: {e}",
                )
                for qid in held_out_ids
            ]

        # Save improved program
        improved_path = output_dir / f"program_lko_{group_idx}.py"
        improved_path.write_text(improved_code)

        # Validate
        valid, error = validate_program(improved_path)
        if not valid:
            print(f"  Group {group_idx}: improved program invalid: {error}")
            return [
                QueryRun(
                    query_id=qid,
                    query_text=next(r.query_text for r in runs if r.query_id == qid),
                    input_json={},
                    error=f"Invalid program: {error}",
                )
                for qid in held_out_ids
            ]

        improved_schema = get_schema(improved_path)
        improved_input_props = improved_schema.get("input", {}).get("properties", {})
        if "query" in improved_input_props:
            improved_nl_field = "query"
        elif "prompt" in improved_input_props:
            improved_nl_field = "prompt"
        else:
            improved_nl_field = next(
                (k_name for k_name, v in improved_input_props.items() if v.get("type") == "string"),
                "prompt",
            )

        # Run held-out queries
        results = []
        for qid in held_out_ids:
            query = next(q for q in sample.queries if q.id == qid)
            input_data: dict[str, Any] = {improved_nl_field: query.text}
            if sample.is_agent and "context" in improved_input_props:
                input_data["context"] = {
                    "today": sample.test_state.today or "2025-02-15",
                    "existing_appointments": sample.test_state.existing_appointments,
                }

            run_start = datetime.now(timezone.utc).isoformat()
            try:
                stdout, stderr = run_program(improved_path, json.dumps(input_data))
                run_end = datetime.now(timezone.utc).isoformat()
                if stderr and not stdout.strip():
                    results.append(QueryRun(
                        query_id=qid,
                        query_text=query.text,
                        input_json=input_data,
                        raw_output=stderr,
                        error=f"Program error: {stderr[:300]}",
                        run_start=run_start,
                        run_end=run_end,
                    ))
                else:
                    results.append(QueryRun(
                        query_id=qid,
                        query_text=query.text,
                        input_json=input_data,
                        raw_output=stdout,
                        run_start=run_start,
                        run_end=run_end,
                    ))
            except Exception as e:
                results.append(QueryRun(
                    query_id=qid,
                    query_text=query.text,
                    input_json=input_data,
                    error=f"Execution failed: {e}",
                    run_start=run_start,
                    run_end=datetime.now(timezone.utc).isoformat(),
                ))

        print(f"  Group {group_idx} ({', '.join(held_out_ids)}): done")
        return results

    # Run all LKO groups in parallel
    max_workers = min(len(groups), 10)
    all_iteration_runs: list[QueryRun] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_group = {
            executor.submit(_run_lko_group, i, group): i
            for i, group in enumerate(groups)
        }
        group_results: dict[int, list[QueryRun]] = {}
        for future in concurrent.futures.as_completed(future_to_group):
            idx = future_to_group[future]
            group_results[idx] = future.result()

    # Flatten in order
    for i in range(len(groups)):
        all_iteration_runs.extend(group_results[i])

    iteration_batch_end = datetime.now(timezone.utc).isoformat()

    # Wait and match traces
    print("\n  Waiting for traces to export...")
    time.sleep(5)
    print("  Matching iteration runs to traces...")
    all_iteration_runs = find_traces_for_runs(
        all_iteration_runs, iteration_batch_start, iteration_batch_end
    )
    matched = sum(1 for r in all_iteration_runs if r.trace_id)
    print(f"  Matched {matched}/{len(all_iteration_runs)} runs to traces")

    # Update state
    state.iteration_runs = [r.to_dict() for r in all_iteration_runs]
    state.iteration_k = k
    state.phase = "iterated"
    state.save(output_dir)

    print(f"\n{'='*60}")
    print(f"LKO COMPLETE: {len(all_iteration_runs)} held-out queries run")
    print(f"{'='*60}")
    print(f"\nNext: ./run_eval.py annotate --output {output_dir} --phase iteration [--file annotations.json]")
    print(f"Then: ./run_eval.py report --output {output_dir}")


# ---------------------------------------------------------------------------
# Subcommand: annotate
# ---------------------------------------------------------------------------

def cmd_annotate(args: argparse.Namespace) -> None:
    """Annotate query runs with pass/fail + reasoning.

    Modes:
      --interactive: prompt for each query via stdin
      --file FILE:   read annotations from JSON file

    Annotation file format:
    [
      {"query_id": "q01", "label": "pass"},
      {"query_id": "q02", "label": "fail", "reasoning": "Missing tax calculation"}
    ]
    """
    output_dir = Path(args.output)
    state = EvalState.load(output_dir)
    phase = args.phase

    if phase == "initial":
        runs = [QueryRun(**r) for r in state.initial_runs]
    elif phase == "iteration":
        if not state.iteration_runs:
            print("No iteration runs found. Run 'iterate' first.")
            sys.exit(1)
        runs = [QueryRun(**r) for r in state.iteration_runs]
    else:
        print(f"Unknown phase: {phase}")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"ANNOTATE: {state.sample_id} ({phase})")
    print(f"{'='*60}")

    # Build annotations
    annotations: list[dict] = []

    if args.file:
        # Read from file
        file_annotations = json.loads(Path(args.file).read_text())
        ann_map = {a["query_id"]: a for a in file_annotations}
        for run in runs:
            if run.query_id in ann_map:
                a = ann_map[run.query_id]
                annotations.append({
                    "run": run,
                    "label": a["label"],
                    "reasoning": a.get("reasoning"),
                })
    else:
        # Interactive mode
        for run in runs:
            print(f"\n{'─'*50}")
            print(f"Query [{run.query_id}]: {run.query_text}")
            print(f"{'─'*50}")
            if run.error:
                print(f"ERROR: {run.error}")
            else:
                print(f"Output:\n{run.raw_output}")
            print()

            while True:
                verdict = input("  pass/fail (p/f)? ").strip().lower()
                if verdict in ("p", "pass"):
                    label = "pass"
                    break
                elif verdict in ("f", "fail"):
                    label = "fail"
                    break
                print("  Enter 'p' or 'f'")

            reasoning = None
            if label == "fail":
                reasoning = input("  Reasoning: ").strip() or None

            annotations.append({
                "run": run,
                "label": label,
                "reasoning": reasoning,
            })

    # Write annotations to API
    client = get_sync_client()
    written = 0
    skipped = 0

    for ann in annotations:
        run: QueryRun = ann["run"]
        if not run.trace_id or not run.span_id:
            print(f"  ⚠ {run.query_id}: no trace linked, skipping API write")
            skipped += 1
            continue

        try:
            client.annotations.create(
                otel_span_id=run.span_id,
                otel_trace_id=run.trace_id,
                label=ann["label"],
                reasoning=ann.get("reasoning"),
            )
            symbol = "✓" if ann["label"] == "pass" else "✗"
            print(f"  {symbol} {run.query_id}: {ann['label']}")
            written += 1
        except Exception as e:
            print(f"  ⚠ {run.query_id}: API error: {e}")
            skipped += 1

    # Also save annotations locally as backup
    local_annotations = [
        {
            "query_id": ann["run"].query_id,
            "label": ann["label"],
            "reasoning": ann.get("reasoning"),
        }
        for ann in annotations
    ]
    ann_file = output_dir / f"annotations_{phase}.json"
    ann_file.write_text(json.dumps(local_annotations, indent=2))

    print(f"\n  Written: {written}, Skipped: {skipped}")
    print(f"  Saved locally: {ann_file}")


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    """Compute pass rates from annotations."""
    output_dir = Path(args.output)
    state = EvalState.load(output_dir)

    print(f"{'='*60}")
    print(f"REPORT: {state.sample_id}")
    print(f"{'='*60}")

    # Get initial annotations
    print("\n[Initial Run]")
    initial_runs = [QueryRun(**r) for r in state.initial_runs]
    local_initial = load_local_annotations(output_dir, "initial")
    initial_pass = 0
    initial_fail = 0
    initial_unannotated = 0

    for run in initial_runs:
        ann = get_annotations_for_run(run, local_initial)
        if ann:
            label = ann["label"]
            if label == "pass":
                initial_pass += 1
                print(f"  ✓ {run.query_id}: pass")
            else:
                initial_fail += 1
                reason = ann.get("reasoning", "")
                print(f"  ✗ {run.query_id}: fail — {reason[:60]}")
        else:
            initial_unannotated += 1
            print(f"  ? {run.query_id}: (no annotation)")

    initial_total = initial_pass + initial_fail
    initial_rate = initial_pass / initial_total if initial_total else 0

    # Get iteration annotations
    iter_pass = 0
    iter_fail = 0
    iter_unannotated = 0

    if state.iteration_runs:
        print(f"\n[Post-LKO (k={state.iteration_k})]")
        iteration_runs = [QueryRun(**r) for r in state.iteration_runs]
        local_iter = load_local_annotations(output_dir, "iteration")

        for run in iteration_runs:
            ann = get_annotations_for_run(run, local_iter)
            if ann:
                label = ann["label"]
                if label == "pass":
                    iter_pass += 1
                    print(f"  ✓ {run.query_id}: pass")
                else:
                    iter_fail += 1
                    reason = ann.get("reasoning", "")
                    print(f"  ✗ {run.query_id}: fail — {reason[:60]}")
            else:
                iter_unannotated += 1
                print(f"  ? {run.query_id}: (no annotation)")

    iter_total = iter_pass + iter_fail
    iter_rate = iter_pass / iter_total if iter_total else 0

    # Compute improvements
    initial_ann_map = {}
    for run in initial_runs:
        ann = get_annotations_for_run(run, local_initial)
        if ann:
            initial_ann_map[run.query_id] = ann["label"]

    fixed = 0
    regressed = 0
    if state.iteration_runs:
        iteration_runs = [QueryRun(**r) for r in state.iteration_runs]
        for run in iteration_runs:
            ann = get_annotations_for_run(run, local_iter if state.iteration_runs else {})
            if not ann or run.query_id not in initial_ann_map:
                continue
            initial_label = initial_ann_map[run.query_id]
            iter_label = ann["label"]
            if initial_label == "fail" and iter_label == "pass":
                fixed += 1
            elif initial_label == "pass" and iter_label == "fail":
                regressed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS: {state.sample_id}")
    print(f"{'='*60}")
    print(f"  Initial:        {initial_pass}/{initial_total} ({initial_rate:.0%})")
    if state.iteration_runs:
        print(f"  Post-LKO:       {iter_pass}/{iter_total} ({iter_rate:.0%})")
        print(f"  Fixed:          {fixed}")
        print(f"  Regressed:      {regressed}")
    if initial_unannotated or iter_unannotated:
        print(f"  Unannotated:    {initial_unannotated} initial, {iter_unannotated} iteration")

    # Save report
    report = {
        "sample_id": state.sample_id,
        "skill_type": state.skill_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "initial_pass_rate": initial_rate,
        "initial_pass": initial_pass,
        "initial_total": initial_total,
        "post_lko_pass_rate": iter_rate if state.iteration_runs else None,
        "post_lko_pass": iter_pass,
        "post_lko_total": iter_total,
        "fixed": fixed,
        "regressed": regressed,
        "k": state.iteration_k,
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2))
    print(f"\n  Report: {output_dir / 'report.json'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Eval pipeline with human-in-the-loop scoring via Mirascope trace annotations. "
                    "Requires MIRASCOPE_API_KEY env var.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run
    run_parser = subparsers.add_parser("run", help="Generate program + run all queries")
    run_parser.add_argument("--sample", required=True, help="Path to sample YAML")
    run_parser.add_argument("--output", required=True, help="Output directory")

    # iterate
    iter_parser = subparsers.add_parser("iterate", help="Read annotations, run LKO improvement")
    iter_parser.add_argument("--output", required=True, help="Output directory (from run)")
    iter_parser.add_argument("--k", type=int, default=1, help="Leave-K-out (default: 1)")

    # annotate
    ann_parser = subparsers.add_parser("annotate", help="Annotate runs with pass/fail + reasoning")
    ann_parser.add_argument("--output", required=True, help="Output directory")
    ann_parser.add_argument("--phase", required=True, choices=["initial", "iteration"],
                           help="Which phase to annotate")
    ann_parser.add_argument("--file", help="JSON file with annotations (otherwise interactive)")

    # report
    report_parser = subparsers.add_parser("report", help="Compute pass rates from annotations")
    report_parser.add_argument("--output", required=True, help="Output directory")

    args = parser.parse_args()

    if not os.environ.get("MIRASCOPE_API_KEY"):
        parser.error("MIRASCOPE_API_KEY env var is required")

    ops.configure()
    ops.instrument_llm()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "annotate":
        cmd_annotate(args)
    elif args.command == "iterate":
        cmd_iterate(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
