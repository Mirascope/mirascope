from mirascope import ops


@ops.trace
def handle_request(query: str) -> str:
    return f"Response to: {query}"


# Session with custom attributes
with ops.session(
    id="conversation-456",
    attributes={"user_tier": "premium", "channel": "web"},
) as session_ctx:
    print(f"Session ID: {session_ctx.id}")
    print(f"Attributes: {session_ctx.attributes}")

    trace = handle_request.wrapped("What's the weather?")
    print(trace.result)
