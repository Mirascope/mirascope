from mirascope import ops


@ops.trace
def process_data(data: dict) -> dict:
    return {"processed": data}


# Call returns Trace containing both result and span info
trace = process_data({"key": "value"})
print(trace.result)  # {"processed": {"key": "value"}}
print(trace.span_id)  # Access the span ID
