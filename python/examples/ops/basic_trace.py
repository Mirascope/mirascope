from mirascope import ops


@ops.trace
def process_data(data: dict[str, str]) -> dict[str, dict[str, str]]:
    return {"processed": data}


# Use .wrapped() to get Trace containing both result and span info
trace = process_data.wrapped({"key": "value"})
print(trace.result)  # {"processed": {"key": "value"}}
print(trace.span_id)  # Access the span ID
