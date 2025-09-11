def extract_serialized_json(text: str) -> str:
    """Extract the serialized JSON string from text that may contain extra content.

    Handles cases where models output text before JSON like:
    "Sure thing! Here's the JSON:\n{...}"

    Or cases where the model wraps the JSON in code blocks like:
    "```json\n{...}\n```"

    Args:
        text: The raw text that may contain a JSON object

    Raises:
        ValueError: If no serialized json object string was found.

    Returns:
        The extracted serialized JSON string
    """
    code_block_start_marker = "```json"
    code_block_start = text.find(code_block_start_marker)
    if code_block_start > -1:
        # Discard text prior to code block; it takes precedence over brackets that
        # may be found before it.
        text = text[code_block_start:]

    json_start = text.find("{")
    if json_start == -1:
        raise ValueError("Could not extract json: no opening `{`")

    # Find the matching closing brace
    brace_count = 0
    in_string = False
    escaped = False

    for i, char in enumerate(text[json_start:], json_start):
        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char == '"' and not escaped:
            in_string = not in_string
            continue

        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    return text[json_start : i + 1]

    raise ValueError("Could not extract json: no closing `}`")
