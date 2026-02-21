#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mirascope[all]>=2.0",
#     "pydantic>=2.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Eval pipeline for mirascope_skill — atomic subcommands for agent orchestration.

Subcommands:
    generate    Generate program from sample YAML + validate
    run         Run all queries against program (creates traces)
    annotate    Write annotations to traces from JSON file
    iterate     Read annotations, run LKO improvement (creates new traces)
    report      Compute pass rates from local annotations

Designed to be called step-by-step by an orchestrating agent that presents
outputs to a human reviewer and collects feedback between steps.

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
        for q in raw.get("queries", []):
            q.pop("expected", None)
        return cls.model_validate(raw)

    @property
    def is_agent(self) -> bool:
        return "agent" in self.skill_type.lower() or "agent" in self.metadata.tags


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


@dataclass
class EvalState:
    """Persistent state saved to state.json between subcommands."""
    sample_path: str
    sample_id: str
    skill_type: str
    is_agent: bool
    program_path: str
    phase: str  # "generated", "ran", "annotated", "iterated"
    run_start: str = ""
    run_end: str = ""
    initial_runs: list[dict] = field(default_factory=list)
    iteration_runs: list[dict] = field(default_factory=list)
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
        capture_output=True, text=True, timeout=timeout, env=env,
    )


def validate_program(program_path: Path) -> tuple[bool, str]:
    if not program_path.exists():
        return False, f"Not found: {program_path}"
    try:
        r = run_uv(program_path, "--help")
        if r.returncode != 0:
            return False, f"--help failed: {r.stderr}"
    except subprocess.TimeoutExpired:
        return False, "--help timed out"
    try:
        r = run_uv(program_path, "--schema")
        if r.returncode != 0:
            return False, f"--schema failed: {r.stderr}"
        schema = json.loads(r.stdout)
        if "input" not in schema or "output" not in schema:
            return False, "Missing input/output in schema"
    except subprocess.TimeoutExpired:
        return False, "--schema timed out"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON from --schema: {e}"
    return True, ""


def get_schema(program_path: Path) -> dict:
    return json.loads(run_uv(program_path, "--schema").stdout)


def get_nl_field(schema: dict) -> str:
    props = schema.get("input", {}).get("properties", {})
    if "query" in props:
        return "query"
    if "prompt" in props:
        return "prompt"
    return next(
        (k for k, v in props.items() if v.get("type") == "string"), "prompt"
    )


# ---------------------------------------------------------------------------
# LLM Calls
# ---------------------------------------------------------------------------

SKILL_MD = Path(__file__).resolve().parent / "SKILL.md"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-20250514"


class GeneratedProgram(BaseModel):
    code: str = Field(description="Complete Python source code")


@llm.call(DEFAULT_MODEL, format=GeneratedProgram)
def generate_program(skill_instructions: str, bootstrap_prompt: str, is_agent: bool = False) -> list:
    agent_reqs = """
1. PEP 723 inline deps with mirascope[all]
2. AgentInput (query field) and AgentOutput (response + tool_calls fields)
3. Tools with @llm.tool decorator
4. Agentic loop with execute_tools/resume
5. --help, --schema, --input CLI
6. Follow "Tool-Based Agent Programs" section
7. CRITICAL: Use model="anthropic/claude-sonnet-4-20250514" (exact string)
8. CRITICAL: Include ops.configure() and @ops.trace on the main function"""

    program_reqs = """
1. PEP 723 inline deps with mirascope[all]
2. ProgramInput with a `prompt` field (natural language input from user)
3. ProgramOutput with structured fields for the result
4. @llm.call with format=ProgramOutput — the LLM extracts data from natural language
5. --help, --schema, --input CLI
6. Follow robustness patterns
7. CRITICAL: Use model="anthropic/claude-sonnet-4-20250514" (exact string)
8. CRITICAL: Input is ALWAYS natural language via prompt field, NOT pre-structured data
9. CRITICAL: Include ops.configure() and @ops.trace on the main function"""

    kind = "TOOL-BASED AGENT" if is_agent else ""
    reqs = agent_reqs if is_agent else program_reqs

    return [
        SystemMessage(content=Text(text=f"You are a Mirascope program generator.\n\n<skill_instructions>\n{skill_instructions}\n</skill_instructions>")),
        UserMessage(content=[Text(text=f"Create a complete, self-contained Mirascope {kind} program for:\n\n<request>\n{bootstrap_prompt}\n</request>\n\nRequirements:{reqs}")]),
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
    feedback_text = ""
    for a in annotations:
        feedback_text += f"\n### Query: {a['query']}\n"
        feedback_text += f"**Label:** {a['label']}\n"
        if a.get("reasoning"):
            feedback_text += f"**Feedback:** {a['reasoning']}\n"
        feedback_text += f"**Program output:**\n```\n{a['output']}\n```\n"

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
1. **Diagnose first:** For each failure, identify the root cause
2. **Make targeted fixes:** Change only what's needed. Do not restructure working code.
3. **Verify mentally:** For each passing query, confirm your changes won't break it.
4. **Return the complete improved program** (full file, not a diff).""")]),
    ]


# ---------------------------------------------------------------------------
# Trace helpers
# ---------------------------------------------------------------------------

def find_traces_for_runs(
    runs: list[dict], start_time: str, end_time: str,
) -> list[dict]:
    """Match query runs to their traces via the Mirascope API. Mutates runs in place."""
    client = get_sync_client()
    try:
        response = client.traces.search(
            start_time=start_time, end_time=end_time,
            limit=len(runs) * 3, root_spans_only=True,
        )
    except Exception:
        return runs

    matched: set[str] = set()
    for span in response.spans:
        try:
            detail = client.traces.gettracedetail(trace_id=span.trace_id)
            attrs_str = ""
            for ds in detail.spans:
                if ds.attributes:
                    attrs_str += ds.attributes

            for run in runs:
                qid = run["query_id"]
                if qid in matched:
                    continue
                if run["query_text"][:50] in attrs_str:
                    run["trace_id"] = span.trace_id
                    run["span_id"] = span.span_id
                    matched.add(qid)
                    break
        except Exception:
            continue
    return runs


def load_local_annotations(output_dir: Path, phase: str) -> dict[str, dict]:
    ann_file = output_dir / f"annotations_{phase}.json"
    if ann_file.exists():
        return {a["query_id"]: a for a in json.loads(ann_file.read_text())}
    return {}


# ---------------------------------------------------------------------------
# Subcommand: generate
# ---------------------------------------------------------------------------

def cmd_generate(args: argparse.Namespace) -> None:
    sample_path = Path(args.sample)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    sample = EvalSample.from_yaml(sample_path)
    skill_instructions = SKILL_MD.read_text()

    print(f"Generating program for {sample.sample_id}...")

    response = generate_program(skill_instructions, sample.bootstrap.prompt, sample.is_agent)
    program_code = response.parse().code

    program_path = output_dir / "program.py"
    program_path.write_text(program_code)

    valid, error = validate_program(program_path)
    if not valid:
        print(json.dumps({"ok": False, "error": error}))
        sys.exit(1)

    state = EvalState(
        sample_path=str(sample_path),
        sample_id=sample.sample_id,
        skill_type=sample.skill_type,
        is_agent=sample.is_agent,
        program_path=str(program_path),
        phase="generated",
    )
    state.save(output_dir)
    print(json.dumps({"ok": True, "program": str(program_path)}))


# ---------------------------------------------------------------------------
# Subcommand: run
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    state = EvalState.load(output_dir)
    sample = EvalSample.from_yaml(state.sample_path)
    program_path = Path(state.program_path)
    schema = get_schema(program_path)
    nl_field = get_nl_field(schema)
    input_props = schema.get("input", {}).get("properties", {})

    batch_start = datetime.now(timezone.utc).isoformat()

    def _run_query(query: EvalQuery) -> dict:
        input_data: dict[str, Any] = {nl_field: query.text}
        if sample.is_agent and "context" in input_props:
            input_data["context"] = {
                "today": sample.test_state.today or "2025-02-15",
                "existing_appointments": sample.test_state.existing_appointments,
            }

        run_start = datetime.now(timezone.utc).isoformat()
        try:
            input_str = json.dumps(input_data)
            result = run_uv(program_path, "--input", input_str, timeout=180)
            stdout, stderr = result.stdout, result.stderr
            run_end = datetime.now(timezone.utc).isoformat()

            error = None
            raw_output = stdout
            if stderr and not stdout.strip():
                error = stderr[:500]
                raw_output = stderr

            return {
                "query_id": query.id,
                "query_text": query.text,
                "input_json": input_data,
                "raw_output": raw_output,
                "error": error,
                "run_start": run_start,
                "run_end": run_end,
                "trace_id": None,
                "span_id": None,
            }
        except Exception as e:
            return {
                "query_id": query.id,
                "query_text": query.text,
                "input_json": input_data,
                "raw_output": "",
                "error": str(e),
                "run_start": run_start,
                "run_end": datetime.now(timezone.utc).isoformat(),
                "trace_id": None,
                "span_id": None,
            }

    max_workers = min(len(sample.queries), 10)
    runs: list[dict] = [None] * len(sample.queries)  # type: ignore

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(_run_query, q): i for i, q in enumerate(sample.queries)
        }
        for future in concurrent.futures.as_completed(future_to_idx):
            runs[future_to_idx[future]] = future.result()

    batch_end = datetime.now(timezone.utc).isoformat()

    # Wait for trace export + match
    time.sleep(5)
    runs = find_traces_for_runs(runs, batch_start, batch_end)

    state.initial_runs = runs
    state.run_start = batch_start
    state.run_end = batch_end
    state.phase = "ran"
    state.save(output_dir)

    # Output results as JSON for the orchestrating agent
    results = []
    for r in runs:
        results.append({
            "query_id": r["query_id"],
            "query_text": r["query_text"],
            "output": r["raw_output"],
            "error": r["error"],
            "has_trace": r["trace_id"] is not None,
        })
    print(json.dumps({"ok": True, "results": results}, indent=2))


# ---------------------------------------------------------------------------
# Subcommand: annotate
# ---------------------------------------------------------------------------

def cmd_annotate(args: argparse.Namespace) -> None:
    """Write annotations from a JSON file to traces + local backup.

    File format:
    [
      {"query_id": "q01", "label": "pass"},
      {"query_id": "q02", "label": "fail", "reasoning": "Missing tax line"}
    ]
    """
    output_dir = Path(args.output)
    state = EvalState.load(output_dir)
    phase = args.phase

    if phase == "initial":
        runs_data = state.initial_runs
    elif phase == "iteration":
        runs_data = state.iteration_runs
    else:
        print(json.dumps({"ok": False, "error": f"Unknown phase: {phase}"}))
        sys.exit(1)

    run_map = {r["query_id"]: r for r in runs_data}
    file_annotations = json.loads(Path(args.file).read_text())

    client = get_sync_client()
    results = []

    for ann in file_annotations:
        qid = ann["query_id"]
        run = run_map.get(qid)
        if not run:
            results.append({"query_id": qid, "status": "not_found"})
            continue

        # Write to API if trace is linked
        api_written = False
        if run.get("trace_id") and run.get("span_id"):
            try:
                client.annotations.create(
                    otel_span_id=run["span_id"],
                    otel_trace_id=run["trace_id"],
                    label=ann["label"],
                    reasoning=ann.get("reasoning"),
                )
                api_written = True
            except Exception as e:
                results.append({"query_id": qid, "status": "api_error", "error": str(e)})

        results.append({
            "query_id": qid,
            "label": ann["label"],
            "status": "ok",
            "api_written": api_written,
        })

    # Save local backup
    ann_file = output_dir / f"annotations_{phase}.json"
    ann_file.write_text(json.dumps(file_annotations, indent=2))

    if phase == "initial":
        state.phase = "annotated"
    state.save(output_dir)

    print(json.dumps({"ok": True, "results": results}, indent=2))


# ---------------------------------------------------------------------------
# Subcommand: iterate
# ---------------------------------------------------------------------------

def cmd_iterate(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    state = EvalState.load(output_dir)
    k = args.k

    sample = EvalSample.from_yaml(state.sample_path)
    skill_instructions = SKILL_MD.read_text()
    program_code = Path(state.program_path).read_text()
    program_path = Path(state.program_path)

    # Load annotations
    local_anns = load_local_annotations(output_dir, "initial")
    if not local_anns:
        print(json.dumps({"ok": False, "error": "No initial annotations found"}))
        sys.exit(1)

    schema = get_schema(program_path)
    nl_field = get_nl_field(schema)
    input_props = schema.get("input", {}).get("properties", {})

    # Build annotated query list
    annotated_ids = [r["query_id"] for r in state.initial_runs if r["query_id"] in local_anns]
    groups = [annotated_ids[i:i + k] for i in range(0, len(annotated_ids), k)]

    iteration_start = datetime.now(timezone.utc).isoformat()

    def _run_lko_group(group_idx: int, held_out_ids: list[str]) -> list[dict]:
        # Build N-K feedback
        train_anns = []
        for qid in annotated_ids:
            if qid in held_out_ids:
                continue
            ann = local_anns[qid]
            run = next(r for r in state.initial_runs if r["query_id"] == qid)
            train_anns.append({
                "query": run["query_text"],
                "output": run["raw_output"],
                "label": ann["label"],
                "reasoning": ann.get("reasoning"),
            })

        # Improve
        try:
            response = improve_program(
                skill_instructions, program_code, train_anns, state.is_agent
            )
            improved_code = response.parse().code
        except Exception as e:
            return [{
                "query_id": qid, "query_text": "", "input_json": {},
                "raw_output": "", "error": f"Improvement failed: {e}",
                "run_start": "", "run_end": "",
                "trace_id": None, "span_id": None,
            } for qid in held_out_ids]

        improved_path = output_dir / f"program_lko_{group_idx}.py"
        improved_path.write_text(improved_code)

        valid, error = validate_program(improved_path)
        if not valid:
            return [{
                "query_id": qid, "query_text": "", "input_json": {},
                "raw_output": "", "error": f"Invalid program: {error}",
                "run_start": "", "run_end": "",
                "trace_id": None, "span_id": None,
            } for qid in held_out_ids]

        improved_schema = get_schema(improved_path)
        improved_nl_field = get_nl_field(improved_schema)
        improved_input_props = improved_schema.get("input", {}).get("properties", {})

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
                result = run_uv(improved_path, "--input", json.dumps(input_data), timeout=180)
                run_end = datetime.now(timezone.utc).isoformat()
                error_msg = None
                raw = result.stdout
                if result.stderr and not result.stdout.strip():
                    error_msg = result.stderr[:500]
                    raw = result.stderr

                results.append({
                    "query_id": qid, "query_text": query.text,
                    "input_json": input_data, "raw_output": raw,
                    "error": error_msg,
                    "run_start": run_start, "run_end": run_end,
                    "trace_id": None, "span_id": None,
                })
            except Exception as e:
                results.append({
                    "query_id": qid, "query_text": query.text,
                    "input_json": input_data, "raw_output": "",
                    "error": str(e),
                    "run_start": run_start,
                    "run_end": datetime.now(timezone.utc).isoformat(),
                    "trace_id": None, "span_id": None,
                })
        return results

    max_workers = min(len(groups), 10)
    group_results: dict[int, list[dict]] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(_run_lko_group, i, g): i for i, g in enumerate(groups)
        }
        for future in concurrent.futures.as_completed(future_to_idx):
            group_results[future_to_idx[future]] = future.result()

    all_runs: list[dict] = []
    for i in range(len(groups)):
        all_runs.extend(group_results[i])

    iteration_end = datetime.now(timezone.utc).isoformat()

    time.sleep(5)
    all_runs = find_traces_for_runs(all_runs, iteration_start, iteration_end)

    state.iteration_runs = all_runs
    state.iteration_k = k
    state.phase = "iterated"
    state.save(output_dir)

    results = [{
        "query_id": r["query_id"],
        "query_text": r["query_text"],
        "output": r["raw_output"],
        "error": r["error"],
        "has_trace": r["trace_id"] is not None,
    } for r in all_runs]
    print(json.dumps({"ok": True, "results": results}, indent=2))


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    state = EvalState.load(output_dir)

    initial_anns = load_local_annotations(output_dir, "initial")
    iter_anns = load_local_annotations(output_dir, "iteration")

    initial_pass = sum(1 for a in initial_anns.values() if a["label"] == "pass")
    initial_total = len(initial_anns)
    initial_rate = initial_pass / initial_total if initial_total else 0

    iter_pass = sum(1 for a in iter_anns.values() if a["label"] == "pass")
    iter_total = len(iter_anns)
    iter_rate = iter_pass / iter_total if iter_total else 0

    fixed = 0
    regressed = 0
    for qid in iter_anns:
        if qid in initial_anns:
            if initial_anns[qid]["label"] == "fail" and iter_anns[qid]["label"] == "pass":
                fixed += 1
            elif initial_anns[qid]["label"] == "pass" and iter_anns[qid]["label"] == "fail":
                regressed += 1

    report = {
        "sample_id": state.sample_id,
        "skill_type": state.skill_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "initial_pass_rate": initial_rate,
        "initial_pass": initial_pass,
        "initial_total": initial_total,
        "post_lko_pass_rate": iter_rate if iter_total else None,
        "post_lko_pass": iter_pass,
        "post_lko_total": iter_total,
        "fixed": fixed,
        "regressed": regressed,
        "k": state.iteration_k,
    }

    (output_dir / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Eval pipeline — atomic subcommands for agent orchestration. "
                    "Requires MIRASCOPE_API_KEY env var.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="Generate program from sample")
    p.add_argument("--sample", required=True)
    p.add_argument("--output", required=True)

    p = sub.add_parser("run", help="Run all queries against program")
    p.add_argument("--output", required=True)

    p = sub.add_parser("annotate", help="Write annotations from JSON file")
    p.add_argument("--output", required=True)
    p.add_argument("--phase", required=True, choices=["initial", "iteration"])
    p.add_argument("--file", required=True, help="JSON annotation file")

    p = sub.add_parser("iterate", help="LKO improvement using annotations")
    p.add_argument("--output", required=True)
    p.add_argument("--k", type=int, default=1)

    p = sub.add_parser("report", help="Compute pass rates")
    p.add_argument("--output", required=True)

    args = parser.parse_args()

    if not os.environ.get("MIRASCOPE_API_KEY"):
        parser.error("MIRASCOPE_API_KEY env var is required")

    ops.configure()
    ops.instrument_llm()

    {"generate": cmd_generate, "run": cmd_run, "annotate": cmd_annotate,
     "iterate": cmd_iterate, "report": cmd_report}[args.command](args)


if __name__ == "__main__":
    main()
