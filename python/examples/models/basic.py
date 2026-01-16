from mirascope import llm

model = llm.use_model("openai/gpt-4o")
response = model.call("What is the capital of France?")
print(response.pretty())
