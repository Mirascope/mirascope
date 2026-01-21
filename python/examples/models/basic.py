from mirascope import llm

model = llm.Model("openai/gpt-4o")
response = model.call("What is the capital of France?")
print(response.text())
