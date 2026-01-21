import math

from mirascope import llm


@llm.tool
def sqrt_tool(number: float) -> float:
    """Computes the square root of a number."""
    return math.sqrt(number)


@llm.call("openai/gpt-5-mini", tools=[sqrt_tool])
def math_assistant(query: str):
    return query


response = math_assistant.stream("What's the square root of 4242?")

while True:  # Loop to ensure we execute all tool calls
    for chunk in response.pretty_stream():
        print(chunk, end="", flush=True)
    print()

    if not response.tool_calls:
        break

    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)
