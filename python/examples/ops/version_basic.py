from mirascope import ops


@ops.version
def process_data(data: str) -> str:
    """Process the input data."""
    return f"Processed: {data}"


# Access version info
print(f"Hash: {process_data.version_info.hash}")
print(f"Version: {process_data.version_info.version}")
print(f"Name: {process_data.version_info.name}")

# Call the function
result = process_data("example")
print(result)
