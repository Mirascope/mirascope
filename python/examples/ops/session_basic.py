from mirascope import ops


@ops.trace
def process_request(data: str) -> str:
    return f"Processed: {data}"


# Group related traces in a session
with ops.session(id="user-123"):
    # All traces within this block share the session ID
    trace1 = process_request.wrapped("first request")
    trace2 = process_request.wrapped("second request")

print(trace1.span_id)
print(trace2.span_id)
