from mirascope.core.base.types import Usage


def get_common_usage(
    input_tokens: int | float | None, output_tokens: int | float | None
) -> Usage | None:
    """Get common usage from input and output tokens."""
    if input_tokens is None and output_tokens is None:
        return None
    input_tokens = int(input_tokens or 0)
    output_tokens = int(output_tokens or 0)
    return Usage(
        prompt_tokens=input_tokens,
        completion_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
    )
