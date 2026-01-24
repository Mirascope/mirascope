from typing import Literal

from mirascope import llm, ops

# Connect to Mirascope Cloud for tracing and analytics
ops.configure()
ops.instrument_llm()


@llm.tool
@ops.trace
def calculate(
    operation: Literal["add", "subtract", "multiply", "divide"],
    a: float,
    b: float,
) -> str:
    """Perform a mathematical operation on two numbers."""
    match operation:
        case "add":
            return str(a + b)
        case "subtract":
            return str(a - b)
        case "multiply":
            return str(a * b)
        case "divide":
            return str(a / b) if b != 0 else "Cannot divide by zero"


@ops.version  # Automatically versions `math_agent` and traces it's execution
@llm.call("openai/gpt-4o-mini", tools=[calculate])
def math_agent(query: str) -> str:
    return f"Help the user with: {query}"


@ops.trace
def run_math_agent(query: str) -> str:
    response = math_agent(query)

    while response.tool_calls:
        tool_outputs = response.execute_tools()
        response = response.resume(tool_outputs)

    return response.text()


print(run_math_agent("What's 42 * 17?"))
