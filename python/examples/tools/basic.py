import math

from mirascope import llm


@llm.tool
def sqrt_tool(number: float) -> float:
    """Computes the square root of a number"""
    return math.sqrt(number)


@llm.call("openai/gpt-5-mini", tools=[sqrt_tool])
def math_assistant(query: str):
    return query


response = math_assistant("What's the square root of 4242?")
tool_call = response.tool_calls[0]
print(tool_call)
# ToolCall(type='tool_call', id='...', name='sqrt_tool', args='{"number":4242}')

# Looks up sqrt_tool by name and calls sqrt_tool.execute(tool_call)
tool_output = response.toolkit.execute(tool_call)
print(tool_output)
# ToolOutput(type='tool_output', id='...', name='sqrt_tool', value=65.13063795173512)

answer = response.resume(tool_output)
print(answer.pretty())
# The square root of 4242 is approximately 65.13063795173512.
