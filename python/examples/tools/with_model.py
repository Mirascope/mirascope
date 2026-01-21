import math

from mirascope import llm


@llm.tool
def sqrt_tool(number: float) -> float:
    """Computes the square root of a number"""
    return math.sqrt(number)


model = llm.Model("openai/gpt-5-mini")
response = model.call("What's the square root of 4242?", tools=[sqrt_tool])

while response.tool_calls:
    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

print(response.text())
