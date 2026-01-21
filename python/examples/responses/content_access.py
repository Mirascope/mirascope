from mirascope import llm

model = llm.model("openai/gpt-5")
response = model.call("Tell me a joke.")

# response.content contains all content parts: Text, ToolCall, Thought
for part in response.content:
    print(f"{type(part).__name__}: {part}")

# Filtered accessors for specific content types
for text in response.texts:
    print(f"Text: {text.text}")

for thought in response.thoughts:
    print(f"Thought: {thought.thought}")

for tool_call in response.tool_calls:
    print(f"Tool call: {tool_call.name}({tool_call.args})")
