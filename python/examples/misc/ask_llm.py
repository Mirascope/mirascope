#!/usr/bin/env python
"""Send a prompt to LLM and trace it.

Usage:
    OPENAI_API_KEY=sk-xxx \
    MIRASCOPE_API_KEY=mk_xxx \
    MIRASCOPE_BASE_URL="http://localhost:3000/api/v2" \
        uv run python examples/misc/ask_llm.py "What is your favorite book?"

After running, trigger sync:
    cd cloud && bun run cron:trigger
"""

from __future__ import annotations

import os
import sys

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from mirascope import llm, ops
from mirascope.api.client import create_export_client
from mirascope.ops._internal.exporters import MirascopeOTLPExporter

BASE_URL = os.getenv("MIRASCOPE_BASE_URL", "http://localhost:3000/api/v2")
API_KEY = os.getenv("MIRASCOPE_API_KEY")

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


@ops.trace
def ask_question(prompt: str) -> llm.Response:
    """Ask a question to the LLM."""
    model: llm.Model = llm.use_model("openai/gpt-4o-mini")
    return model.call(prompt)


def main() -> None:
    if not API_KEY:
        print(f"{RED}ERROR: MIRASCOPE_API_KEY required{RESET}")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print(f"{RED}ERROR: OPENAI_API_KEY required{RESET}")
        sys.exit(1)

    if len(sys.argv) < 2:
        print(f'{RED}Usage: python ask_llm.py "your question here"{RESET}')
        sys.exit(1)

    prompt = sys.argv[1]

    # Setup tracing
    export_client = create_export_client(base_url=BASE_URL, api_key=API_KEY)
    provider = TracerProvider()
    exporter = MirascopeOTLPExporter(client=export_client)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    ops.configure(tracer_provider=provider)
    ops.instrument_llm()

    print(f"{BOLD}Sending prompt to LLM...{RESET}")
    print(f"{DIM}Prompt: {prompt}{RESET}")

    # Call LLM
    response = ask_question(prompt)

    print(f"\n{GREEN}Response:{RESET}")
    print(f"  {response.content}")

    # Flush spans
    provider.force_flush()
    provider.shutdown()

    print(f"\n{DIM}Span sent! Run 'cd cloud && bun run cron:trigger' to sync.{RESET}")
    print(f'{DIM}Then search with: python search_span.py "ask_question"{RESET}')


if __name__ == "__main__":
    main()
