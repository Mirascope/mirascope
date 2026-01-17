import math

from mirascope import llm


@llm.tool
def sqrt_tool(number: float) -> float:
    """Computes the square root of a number"""
    return math.sqrt(number)


@llm.call(
    "anthropic/claude-sonnet-4-5",
    tools=[sqrt_tool],
    thinking={"level": "medium", "include_thoughts": True},
)
def math_assistant(query: str):
    return query


response = math_assistant.stream("What's the square root of 4242?")

# Create a loop for tool calling.
while True:
    # Stream text and thoughts; tool call streams complete silently
    for stream in response.streams():
        if stream.content_type == "text":
            for delta in stream:
                print(delta, end="", flush=True)
            print()
        elif stream.content_type == "thought":
            print("Thinking: ", end="")
            for delta in stream:
                print(delta, end="", flush=True)
            print()

    if response.tool_calls:
        response = response.resume(response.execute_tools())
    else:
        break
