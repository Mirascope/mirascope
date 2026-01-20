from mirascope import llm


@llm.tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b


@llm.call("openai/gpt-4o-mini", tools=[divide])
def calculator(query: str):
    return query


response = calculator("What is 10 divided by 0?")

# Mirascope automatically catches tool execution errors and includes them
# in the ToolOutput. The error message is passed to the LLM so it can adapt.
max_retries = 3
consecutive_errors = 0

while response.tool_calls:
    tool_outputs = response.execute_tools()

    # Check if any tools failed
    had_errors = any(output.error is not None for output in tool_outputs)
    if had_errors:
        consecutive_errors += 1
        if consecutive_errors >= max_retries:
            # Find the first error and raise it
            for output in tool_outputs:
                if output.error is not None:
                    raise output.error
    else:
        consecutive_errors = 0

    # Resume with tool outputs - errors are automatically passed to the LLM
    response = response.resume(tool_outputs)

print(response.text())
