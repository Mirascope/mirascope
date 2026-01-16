import math

from mirascope import llm


@llm.tool
def sqrt_tool(number: float) -> float:
    """Computes the square root of a number"""
    return math.sqrt(number)


@llm.call("openai/gpt-5-mini", tools=[sqrt_tool])
def math_assistant(query: str):
    return query


response = math_assistant("What are the square roots of 3737, 4242, and 6464?")

tool_outputs = response.execute_tools()  # Execute all of the response's tool calls

answer = response.resume(tool_outputs)
print(answer.pretty())

# The square roots (approximate) are:
# - sqrt(3737) ≈ 61.1310068623117
# - sqrt(4242) ≈ 65.13063795173512
# - sqrt(6464) ≈ 80.39900496896712
