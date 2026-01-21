"""Example showing how to use @ops.trace with @llm.call for tracing."""

from __future__ import annotations

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from mirascope import llm, ops

# Configure an SDK tracer provider with a simple console exporter.
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

# Enable GenAI 1.38 instrumentation.
ops.configure(tracer_provider=provider)
ops.instrument_llm()


@ops.trace
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    """Traced LLM call using @ops.trace decorator.

    This creates a TracedCall where:
    - recommend_book("fantasy") returns Response directly (but execution is traced)
    - recommend_book.call("fantasy") returns Response directly (same as __call__)
    - recommend_book.stream("fantasy") returns StreamResponse directly
    - recommend_book.wrapped("fantasy") returns Trace[Response] with span info
    - recommend_book.wrapped.call("fantasy") returns Response directly
    - recommend_book.wrapped_stream("fantasy") returns Trace[StreamResponse]
    """
    return [
        llm.messages.system("Always recommend kid-friendly books."),
        llm.messages.user(f"Please recommend a book in {genre}."),
    ]


@ops.trace(tags=["production", "recommendations"])
@llm.call("openai/gpt-4o-mini")
def recommend_book_with_tags(genre: str):
    """Traced LLM call with custom tags."""
    return [
        llm.messages.system("Always recommend kid-friendly books."),
        llm.messages.user(f"Please recommend a book in {genre}."),
    ]


print("=== TracedCall: recommend_book('fantasy') returns Response directly ===")
response = recommend_book("fantasy")
print(f"Content: {response.content}")

print(
    "\n=== TracedCall.wrapped: recommend_book.wrapped('fantasy') returns Trace[Response] ==="
)
trace = recommend_book.wrapped("fantasy")
print(f"Span ID: {trace.span_id}")
print(f"Content: {trace.result.content}")

print(
    "\n=== TracedCall.wrapped.call: recommend_book.wrapped.call('fantasy') returns Response directly ==="
)
response = recommend_book.call("fantasy")
print(f"Content: {response.content}")

print("\n=== TracedCall with custom tags (returns Response directly) ===")
response = recommend_book_with_tags("science fiction")
print(f"Content: {response.content}")

print(
    "\n=== TracedCall.wrapped_stream: recommend_book.wrapped_stream('adventure') returns Trace[StreamResponse] ==="
)
traced_stream = recommend_book.wrapped_stream("adventure")
print(f"Span ID: {traced_stream.span_id}")
for chunk in traced_stream.result.pretty_stream():
    print(chunk, end="", flush=True)
print()

print(
    "\n=== TracedCall.stream: recommend_book.stream('mystery') returns StreamResponse directly ==="
)
stream_response = recommend_book.stream("mystery")
for chunk in stream_response.pretty_stream():
    print(chunk, end="", flush=True)
print()
