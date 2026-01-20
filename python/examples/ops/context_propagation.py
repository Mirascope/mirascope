from mirascope import ops


# Client side: inject context into outgoing request headers
def make_request():
    headers: dict[str, str] = {}
    ops.inject_context(headers)
    # headers now contains trace context like:
    # {"traceparent": "00-...", "tracestate": "..."}
    print(f"Injected headers: {headers}")
    return headers


# Server side: extract context from incoming request headers
def handle_request(headers: dict[str, str]):
    with ops.propagated_context(extract_from=headers):
        # All traces within this block are linked to the parent trace
        process_request()


@ops.trace
def process_request() -> str:
    return "Request processed"


# Example usage
with ops.session(id="demo-session"):
    with ops.span("client_request"):
        headers = make_request()

    # Simulate server receiving the request
    handle_request(headers)
