#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pydantic>=2.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Compute and print eval metrics.

Usage:
    ./report.py --bootstrap RESULTS.json [--iteration RESULTS.json] [--sample SAMPLE.yaml]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
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
# Report functions
# ---------------------------------------------------------------------------


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "N/A"
    return f"{numerator / denominator * 100:.1f}%"


def print_bootstrap_metrics(bootstrap: BootstrapResult, sample: EvalSample | None) -> None:
    annotations = {a.query_id: a for a in bootstrap.annotations}
    if not annotations:
        print("No annotations found in bootstrap results.")
        return

    total = len(annotations)
    acceptable = sum(1 for a in annotations.values() if a.acceptable)

    print("Bootstrap Results")
    print("=" * 50)
    print(f"  Total annotated:  {total}")
    print(f"  Acceptable:       {acceptable}")
    print(f"  % Acceptable:     {pct(acceptable, total)}")
    print()

    if sample:
        queries_by_id = {q.id: q for q in sample.queries}
        breakdown: dict[tuple[str, str], list[bool]] = {}

        for qid, ann in annotations.items():
            query = queries_by_id.get(qid)
            if query:
                key = (query.specificity, query.professionalism)
                breakdown.setdefault(key, []).append(ann.acceptable)

        if breakdown:
            print("Breakdown by Specificity x Professionalism")
            print("-" * 50)
            print(f"  {'Specificity':<15} {'Professionalism':<15} {'Acceptable':<12} {'Total':<8} {'%':<8}")
            for (spec, prof), results in sorted(breakdown.items()):
                acc = sum(results)
                tot = len(results)
                print(f"  {spec:<15} {prof:<15} {acc:<12} {tot:<8} {pct(acc, tot):<8}")
            print()


def print_iteration_metrics(iteration: IterationResult) -> None:
    annotated_folds = [f for f in iteration.folds if f.annotation is not None]
    if not annotated_folds:
        print("No annotations found in iteration results.")
        return

    total = len(annotated_folds)
    acceptable = sum(1 for f in annotated_folds if f.annotation and f.annotation.acceptable)

    print("Iteration Results (LOO CV)")
    print("=" * 50)
    print(f"  Total annotated:  {total}")
    print(f"  Acceptable:       {acceptable}")
    print(f"  % Acceptable:     {pct(acceptable, total)}")
    print()


def print_comparison(bootstrap: BootstrapResult, iteration: IterationResult) -> None:
    b_annotations = {a.query_id: a for a in bootstrap.annotations}
    i_annotations = {f.held_out_query_id: f.annotation for f in iteration.folds if f.annotation}

    common_ids = sorted(set(b_annotations.keys()) & set(i_annotations.keys()))
    if not common_ids:
        print("No common query IDs for comparison.")
        return

    b_acc = sum(1 for qid in common_ids if b_annotations[qid].acceptable)
    i_acc = sum(1 for qid in common_ids if i_annotations[qid] and i_annotations[qid].acceptable)
    n = len(common_ids)
    delta = (i_acc - b_acc) / n * 100 if n > 0 else 0

    print("Comparison: Bootstrap vs Iteration")
    print("=" * 50)
    print(f"  Bootstrap % acceptable:  {pct(b_acc, n)}")
    print(f"  Iteration % acceptable:  {pct(i_acc, n)}")
    print(f"  Delta:                   {delta:+.1f}pp")
    print()

    print("Per-Query Before/After")
    print("-" * 60)
    print(f"  {'Query ID':<12} {'Bootstrap':<12} {'Iteration':<12} {'Change':<10}")
    for qid in common_ids:
        b = "pass" if b_annotations[qid].acceptable else "FAIL"
        i_ann = i_annotations[qid]
        i = "pass" if (i_ann and i_ann.acceptable) else "FAIL"
        if b == i:
            change = "-"
        elif i == "pass":
            change = "improved"
        else:
            change = "regressed"
        print(f"  {qid:<12} {b:<12} {i:<12} {change:<10}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute and print eval metrics")
    parser.add_argument("--bootstrap", required=True, help="Path to bootstrap results JSON")
    parser.add_argument("--iteration", required=False, help="Path to iteration results JSON")
    parser.add_argument("--sample", required=False, help="Path to YAML sample (for breakdown)")
    args = parser.parse_args()

    bootstrap = BootstrapResult.load(args.bootstrap)
    sample = EvalSample.from_yaml(args.sample) if args.sample else None

    print_bootstrap_metrics(bootstrap, sample)

    if args.iteration:
        iteration = IterationResult.load(args.iteration)
        print_iteration_metrics(iteration)
        print_comparison(bootstrap, iteration)


if __name__ == "__main__":
    main()
