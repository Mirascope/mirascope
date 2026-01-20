#!/usr/bin/env python
"""Search spans with various filters.

Usage:
    # Keyword search (span name)
    uv run python examples/misc/search_span.py "ask_question"

    # Search in input messages (gen_ai.input_messages)
    uv run python examples/misc/search_span.py --input-messages "favorite book"

    # Search in output messages (gen_ai.output_messages)
    uv run python examples/misc/search_span.py --output-messages "recommendation"

    # Filter by provider
    uv run python examples/misc/search_span.py --provider openai

    # Filter by model
    uv run python examples/misc/search_span.py --model gpt-4o-mini

    # Filter by error
    uv run python examples/misc/search_span.py --errors

    # Filter by duration (slow requests > 100ms)
    uv run python examples/misc/search_span.py --min-duration 100

    # Combine filters
    uv run python examples/misc/search_span.py --provider openai --input-messages "hello"

    # Fuzzy search for input/output messages (typo tolerant, uses ngramSearch)
    uv run python examples/misc/search_span.py --input-messages "prog" --fuzzy
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

from mirascope.api.client import Mirascope

BASE_URL = os.getenv("MIRASCOPE_BASE_URL", "http://localhost:3000/api/v2")
API_KEY = os.getenv("MIRASCOPE_API_KEY")

# ANSI colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def format_duration(ms: float | None) -> str:
    if ms is None:
        return "N/A"
    if ms < 1:
        return f"{ms * 1000:.0f}us"
    if ms < 1000:
        return f"{ms:.1f}ms"
    return f"{ms / 1000:.2f}s"


def format_time(iso_str: str | None) -> str:
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except Exception:
        return iso_str[:19] if iso_str else "N/A"


def truncate(text: str | None, max_len: int = 50) -> str:
    if not text:
        return "-"
    text = text.replace("\n", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def print_divider() -> None:
    print(f"  {DIM}{'─' * 90}{RESET}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search spans with filters")
    parser.add_argument("query", nargs="?", help="Keyword search (span name)")
    parser.add_argument(
        "--input-messages",
        "-i",
        dest="input_messages",
        help="Search in gen_ai.input_messages",
    )
    parser.add_argument(
        "--output-messages",
        "-o",
        dest="output_messages",
        help="Search in gen_ai.output_messages",
    )
    parser.add_argument("--provider", "-p", help="Filter by provider (e.g., openai)")
    parser.add_argument("--model", "-m", help="Filter by model (e.g., gpt-4o-mini)")
    parser.add_argument("--errors", "-e", action="store_true", help="Show only errors")
    parser.add_argument("--min-duration", type=float, help="Min duration in ms")
    parser.add_argument("--max-duration", type=float, help="Max duration in ms")
    parser.add_argument(
        "--fuzzy",
        "-f",
        action="store_true",
        help="Enable fuzzy search for input/output messages (typo tolerant, uses ngramSearch)",
    )
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max results")

    args = parser.parse_args()

    if not API_KEY:
        print(f"{RED}ERROR: MIRASCOPE_API_KEY required{RESET}")
        sys.exit(1)

    # At least one filter required
    if not any(
        [
            args.query,
            args.input_messages,
            args.output_messages,
            args.provider,
            args.model,
            args.errors,
            args.min_duration,
            args.max_duration,
        ]
    ):
        parser.print_help()
        sys.exit(1)

    client = Mirascope(base_url=BASE_URL, api_key=API_KEY)

    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(hours=1)).isoformat()
    end_time = (now + timedelta(minutes=5)).isoformat()

    # Build search params
    search_params = {
        "start_time": start_time,
        "end_time": end_time,
        "limit": args.limit,
        "sort_by": "start_time",
        "sort_order": "desc",
    }

    if args.query:
        search_params["query"] = args.query
    if args.input_messages:
        search_params["input_messages_query"] = args.input_messages
    if args.output_messages:
        search_params["output_messages_query"] = args.output_messages
    if args.fuzzy:
        search_params["fuzzy_search"] = True
    if args.provider:
        search_params["provider"] = [args.provider]
    if args.model:
        search_params["model"] = [args.model]
    if args.errors:
        search_params["has_error"] = True
    if args.min_duration:
        search_params["min_duration"] = args.min_duration
    if args.max_duration:
        search_params["max_duration"] = args.max_duration

    # Print search criteria
    print(f"\n{BOLD}Search Filters:{RESET}")
    if args.query:
        print(f"  {DIM}Query:{RESET} {YELLOW}'{args.query}'{RESET}")
    if args.input_messages:
        print(f"  {DIM}Input Messages:{RESET} {YELLOW}'{args.input_messages}'{RESET}")
    if args.output_messages:
        print(f"  {DIM}Output Messages:{RESET} {YELLOW}'{args.output_messages}'{RESET}")
    if args.fuzzy:
        print(f"  {DIM}Fuzzy Search:{RESET} {YELLOW}enabled{RESET}")
    if args.provider:
        print(f"  {DIM}Provider:{RESET} {YELLOW}{args.provider}{RESET}")
    if args.model:
        print(f"  {DIM}Model:{RESET} {YELLOW}{args.model}{RESET}")
    if args.errors:
        print(f"  {DIM}Errors only:{RESET} {YELLOW}yes{RESET}")
    if args.min_duration:
        print(f"  {DIM}Min duration:{RESET} {YELLOW}{args.min_duration}ms{RESET}")
    if args.max_duration:
        print(f"  {DIM}Max duration:{RESET} {YELLOW}{args.max_duration}ms{RESET}")
    print()

    result = client.traces.search(**search_params)

    if not result.total or result.total == 0:
        print(f"  {DIM}No spans found{RESET}")
        return

    total = int(result.total) if result.total else 0
    print(f"  {GREEN}Found {total} span(s){RESET}")
    print()

    # Get detailed info for each span
    for i, span in enumerate(result.spans or []):
        # Get trace detail to access attributes
        detail = client.traces.gettracedetail(span.trace_id)

        # Find matching span in detail
        span_detail = None
        if detail and detail.spans:
            for d in detail.spans:
                if d.span_id == span.span_id:
                    span_detail = d
                    break

        # Parse attributes
        input_text = "-"
        output_text = "-"
        if span_detail and span_detail.attributes:
            try:
                attrs = json.loads(span_detail.attributes)
                # Get input from arg_values
                if "mirascope.trace.arg_values" in attrs:
                    arg_values = json.loads(attrs["mirascope.trace.arg_values"])
                    if "prompt" in arg_values:
                        input_text = arg_values["prompt"]
                    elif arg_values:
                        input_text = str(list(arg_values.values())[0])
                # Get output
                if "mirascope.trace.output" in attrs:
                    output_text = attrs["mirascope.trace.output"]
            except (json.JSONDecodeError, KeyError):
                pass

        # Print span info
        print(f"  {BOLD}[{i + 1}] {CYAN}{span.name}{RESET}")
        print(
            f"      {DIM}Time:{RESET} {format_time(span.start_time)}  "
            f"{DIM}Duration:{RESET} {format_duration(span.duration_ms)}  "
            f"{DIM}Model:{RESET} {span.model or '-'}  "
            f"{DIM}Provider:{RESET} {span.provider or '-'}"
        )
        print(f"      {DIM}Input:{RESET}  {YELLOW}{truncate(input_text, 60)}{RESET}")
        print(f"      {DIM}Output:{RESET} {GREEN}{truncate(output_text, 60)}{RESET}")
        print_divider()

    print()


if __name__ == "__main__":
    main()
