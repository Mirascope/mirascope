"""Example: function versioning and annotation against local Mirascope Cloud server.

Prerequisites:
1. Start cloud server: `bun run cloud:dev` (from repo root)
2. Run migrations: `cd cloud && bun run db:migrate`
3. Create API key via UI or set MIRASCOPE_API_KEY env var

Usage:
    MIRASCOPE_API_KEY=mk_xxx MIRASCOPE_BASE_URL=http://localhost:3000/api/v2 uv run python examples/misc/local_versioning_example.py
"""

from __future__ import annotations

import os

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from mirascope import llm, ops
from mirascope.api.client import create_export_client
from mirascope.ops._internal.exporters import MirascopeOTLPExporter

BASE_URL = os.getenv("MIRASCOPE_BASE_URL", "http://localhost:3000/api/v2")
API_KEY = os.getenv("MIRASCOPE_API_KEY")

if not API_KEY:
    print("ERROR: MIRASCOPE_API_KEY environment variable is required")
    print("Create an API key in the Mirascope Cloud UI: http://localhost:3000")
    exit(1)

print(f"Using base URL: {BASE_URL}")
print(f"Using API key: {API_KEY[:10]}...")

llm.register_provider(
    "mirascope",
    scope=["openai", "anthropic", "google"],
    base_url="http://localhost:3000/router/v2",
    api_key=API_KEY,
)

client = create_export_client(base_url=BASE_URL, api_key=API_KEY)

provider = TracerProvider()
exporter = MirascopeOTLPExporter(
    client=client,
)
provider.add_span_processor(BatchSpanProcessor(exporter))

ops.configure(tracer_provider=provider)
ops.instrument_llm()


@ops.version(tags=["example", "books"])
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    """Recommend a book based on genre."""
    return [
        llm.messages.system("Always recommend kid-friendly books."),
        llm.messages.user(f"Please recommend a book in {genre}."),
    ]


@ops.trace
def judge_recommendation(recommendation: str) -> str:
    """Judge if a book recommendation is appropriate."""
    keywords = ["kid", "child", "young", "family", "adventure", "magic"]
    return (
        "appropriate"
        if any(kw in recommendation.lower() for kw in keywords)
        else "needs_review"
    )


response = recommend_book("fantasy")
print(f"Response: {response.content[:100]}...")
if recommend_book.version_info:
    print(f"Version: {recommend_book.version_info.version}")
else:
    print("Version: (not available)")

trace = judge_recommendation.wrapped("The Hobbit - a magical adventure")
print(f"Judgment: {trace.result}")

provider.force_flush()
trace.annotate(
    label="pass",
    reasoning="Includes kid-friendly adventure themes",
    metadata={"confidence": 0.95, "reviewer": "automated"},
)
print("Annotation sent!")

provider.shutdown()
