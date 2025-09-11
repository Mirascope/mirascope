def extract_json_object(text: str) -> str:
    """Extract JSON object from text that may contain extra content before/after.

    Handles cases where models output text before JSON like:
    "Sure thing! Here's the JSON:\n{...}"

    Or wrap JSON in code blocks like:
    "```json\n{...}\n```"

    Args:
        text: The raw text that may contain a JSON object

    Returns:
        The extracted JSON object string
    """
    # First check for code block format
    if "```json" in text:
        start_idx = text.find("```json")
        if start_idx != -1:
            # Find the start of JSON content after ```json
            json_start = start_idx + 7  # len("```json")

            # Find the closing ```
            end_idx = text.find("```", json_start)
            if end_idx != -1:
                return text[json_start:end_idx].strip()

    # Look for the first { character (start of JSON object)
    json_start = -1
    for i, char in enumerate(text):
        if char == "{":
            json_start = i
            break

    if json_start == -1:
        # No JSON object found, return original text
        return text

    # Find the matching closing brace
    depth = 0
    json_end = json_start

    for i in range(json_start, len(text)):
        char = text[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                json_end = i + 1
                break

    return text[json_start:json_end]
