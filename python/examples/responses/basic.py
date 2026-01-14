from mirascope import llm

model: llm.Model = llm.use_model("openai/gpt-4o")
message: llm.Message = llm.messages.user("What is the capital of France?")
response: llm.Response = model.call(messages=[message])

# Access response content
print(response.pretty())  # Human-readable output
print(response.texts)  # List of Text objects
print(response.content)  # All content parts (Text, ToolCall, Thought)
print(response.messages)  # All of the messages in the response.
