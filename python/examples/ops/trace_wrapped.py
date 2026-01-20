from mirascope import llm, ops


@ops.trace
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


# Use .wrapped() to get Trace[Response] with span info
trace = recommend_book.wrapped("fantasy")
print(trace.result.text())  # The LLM response
print(trace.span_id)  # The span ID for this trace
print(trace.trace_id)  # The trace ID
