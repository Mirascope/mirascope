from mirascope import llm


@llm.tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b


@llm.call("openai/gpt-4o-mini", tools=[divide])
def calculator(query: str):
    return query


response = calculator("What is 10 divided by 0?")

while response.tool_calls:
    try:
        tool_outputs = response.execute_tools()
        response = response.resume(tool_outputs)
    except (llm.ToolNotFoundError, ZeroDivisionError) as e:
        response = response.resume(f"Your tool call failed: {e}")

print(response.text())
