"""Example: tracing against local Mirascope Cloud server.

Prerequisites:
1. Start cloud server: `bun run cloud:dev` (from repo root)
2. Run migrations: `cd cloud && bun run db:migrate`
3. Create API key via UI or set MIRASCOPE_API_KEY env var

Usage:
    MIRASCOPE_API_KEY=mk_xxx MIRASCOPE_BASE_URL=http://localhost:3000/api/v0 uv run python examples/misc/local_traces_example.py
"""

from __future__ import annotations

import os

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from mirascope import llm, ops
from mirascope.api.client import create_export_client
from mirascope.ops._internal.exporters import MirascopeOTLPExporter

# Configuration
BASE_URL = os.getenv("MIRASCOPE_BASE_URL", "http://localhost:3000/api/v0")
API_KEY = os.getenv("MIRASCOPE_API_KEY")

if not API_KEY:
    print("ERROR: MIRASCOPE_API_KEY environment variable is required")
    print("Create an API key in the Mirascope Cloud UI: http://localhost:3000")
    exit(1)

print(f"Using base URL: {BASE_URL}")
print(f"Using API key: {API_KEY[:10]}...")

# Create Mirascope client for export
client = create_export_client(base_url=BASE_URL, api_key=API_KEY)

# Configure tracer with Mirascope exporter
provider = TracerProvider()
exporter = MirascopeOTLPExporter(client=client)
provider.add_span_processor(BatchSpanProcessor(exporter))

# Enable GenAI instrumentation
ops.configure(tracer_provider=provider)
ops.instrument_llm()


@ops.trace
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    """Test traced LLM call."""
    return [
        llm.messages.system("Always recommend kid-friendly books."),
        llm.messages.user(f"Please recommend a book in {genre}."),
    ]


print("\n=== Testing traced LLM call ===")
try:
    response = recommend_book("fantasy")
    print(f"Response: {response.content[:100]}...")
    print("\nTrace sent successfully! Check your Mirascope Cloud dashboard.")
except Exception as e:
    print(f"Error: {e}")

# Shutdown to flush spans
provider.shutdown()
