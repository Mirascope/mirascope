from mirascope import llm

model = llm.use_model("openai/gpt-4o")
message = llm.messages.user("What is the capital of France?")
response = model.call(messages=[message])
print(response.pretty())
