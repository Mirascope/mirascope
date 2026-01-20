import math

from mirascope import llm


@llm.tool
def sqrt_tool(number: float) -> float:
    """Computes the square root of a number"""
    return math.sqrt(number)


@llm.prompt(tools=[sqrt_tool])
def math_assistant(query: str):
    return query


model = llm.Model("openai/gpt-5-mini")
response = math_assistant(model, "What's the square root of 4242?")

while response.tool_calls:
    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

print(response.text())
