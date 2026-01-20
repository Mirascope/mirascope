from mirascope import ops


@ops.version(
    name="data_processor",
    tags=["production", "v1"],
    metadata={"owner": "data-team", "ticket": "ENG-1234"},
)
def process_data(data: str) -> str:
    """Process the input data with validation."""
    return f"Processed: {data}"


# Access version info
if (info := process_data.version_info) is not None:
    print(f"Name: {info.name}")
    print(f"Tags: {info.tags}")
    print(f"Metadata: {info.metadata}")
    print(f"Description: {info.description}")

# Call the function
result = process_data("example")
print(result)
