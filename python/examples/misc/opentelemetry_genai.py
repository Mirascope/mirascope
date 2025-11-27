"""Example showing how to export GenAI spans with OpenTelemetry."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from mirascope import llm, ops

# Configure an SDK tracer provider with a simple console exporter.
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

# Enable GenAI 1.38 instrumentation.
ops.configure(tracer_provider=provider)
ops.instrument_llm()


@llm.call("openai/gpt-5")
def recommend_book(genre: str):
    return [
        llm.messages.system("Always recommend kid-friendly books."),
        llm.messages.user(f"Please recommend a book in {genre}."),
    ]


response = recommend_book("fantasy")
print(response.pretty())
