import math

from mirascope import llm


@llm.tool
def sqrt_tool(number: float) -> float:
    """Computes the square root of a number"""
    return math.sqrt(number)


@llm.tool
def sum_tool(numbers: list[float]) -> float:
    total = 0
    for number in numbers:
        total += number
    return total


@llm.call("openai/gpt-5-mini", tools=[sqrt_tool, sum_tool])
def math_assistant(query: str):
    return query


response = math_assistant("What's the sum of the square roots of 137, 4242, and 6900?")

while response.tool_calls:
    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

print(response.pretty())
# sqrt(137) + sqrt(4242) + sqrt(6900) ≈ 159.9015764916355
