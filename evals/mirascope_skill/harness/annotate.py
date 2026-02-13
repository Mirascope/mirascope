"""Interactive annotation of eval results via terminal.

Usage:
    python -m harness.annotate --results JSON
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import Annotation, BootstrapResult, IterationResult


def annotate_bootstrap(results_path: Path) -> None:
    result = BootstrapResult.load(results_path)
    annotated_ids = {a.query_id for a in result.annotations}

    unannotated = [qr for qr in result.query_results if qr.query_id not in annotated_ids]
    if not unannotated:
        print("All queries already annotated.")
        return

    print(f"\n{len(unannotated)} unannotated query result(s) out of {len(result.query_results)}\n")
    print("=" * 60)

    for qr in unannotated:
        print(f"\nQuery ID: {qr.query_id}")
        if qr.orchestrated_input:
            print(f"Orchestrated input: {qr.orchestrated_input}")
        if qr.error:
            print(f"ERROR: {qr.error}")
        print(f"\n--- Output ---\n{qr.raw_output}\n--- End Output ---\n")

        while True:
            answer = input("Acceptable? (y/n/s=skip/q=quit): ").strip().lower()
            if answer in ("y", "n", "s", "q"):
                break
            print("Please enter y, n, s, or q.")

        if answer == "q":
            break
        if answer == "s":
            continue

        feedback = input("Feedback (optional): ").strip()

        result.annotations.append(Annotation(
            query_id=qr.query_id,
            acceptable=answer == "y",
            feedback=feedback,
        ))
        result.save(results_path)
        print(f"  Saved annotation for {qr.query_id}")

    annotated_count = len(result.annotations)
    total = len(result.query_results)
    print(f"\nAnnotation progress: {annotated_count}/{total}")


def annotate_iteration(results_path: Path) -> None:
    result = IterationResult.load(results_path)
    unannotated = [f for f in result.folds if f.annotation is None]

    if not unannotated:
        print("All folds already annotated.")
        return

    print(f"\n{len(unannotated)} unannotated fold(s) out of {len(result.folds)}\n")
    print("=" * 60)

    for fold in unannotated:
        qr = fold.query_result
        print(f"\nFold {fold.fold_index} — Held-out query: {fold.held_out_query_id}")
        if qr.orchestrated_input:
            print(f"Orchestrated input: {qr.orchestrated_input}")
        if qr.error:
            print(f"ERROR: {qr.error}")
        print(f"\n--- Output ---\n{qr.raw_output}\n--- End Output ---\n")

        while True:
            answer = input("Acceptable? (y/n/s=skip/q=quit): ").strip().lower()
            if answer in ("y", "n", "s", "q"):
                break
            print("Please enter y, n, s, or q.")

        if answer == "q":
            break
        if answer == "s":
            continue

        feedback = input("Feedback (optional): ").strip()

        fold.annotation = Annotation(
            query_id=fold.held_out_query_id,
            acceptable=answer == "y",
            feedback=feedback,
        )
        result.save(results_path)
        print(f"  Saved annotation for fold {fold.fold_index}")

    annotated_count = sum(1 for f in result.folds if f.annotation is not None)
    print(f"\nAnnotation progress: {annotated_count}/{len(result.folds)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate eval results interactively")
    parser.add_argument("--results", required=True, help="Path to results JSON file")
    args = parser.parse_args()

    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Results file not found: {results_path}", file=sys.stderr)
        sys.exit(1)

    # Detect type by trying to load each
    text = results_path.read_text()
    if '"folds"' in text:
        annotate_iteration(results_path)
    else:
        annotate_bootstrap(results_path)


if __name__ == "__main__":
    main()
