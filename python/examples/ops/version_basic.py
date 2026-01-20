from mirascope import ops


@ops.version
def process_data(data: str) -> str:
    """Process the input data."""
    return f"Processed: {data}"


# Access version info
if (info := process_data.version_info) is not None:
    print(f"Hash: {info.hash}")
    print(f"Version: {info.version}")
    print(f"Name: {info.name}")

# Call the function
result = process_data("example")
print(result)
