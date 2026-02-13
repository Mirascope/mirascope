"""Compute and print eval metrics.

Usage:
    python -m harness.report --bootstrap JSON [--iteration JSON] [--sample YAML]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import BootstrapResult, EvalSample, IterationResult


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

    # Breakdown by specificity x professionalism (requires sample)
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

    # Per-query table
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
