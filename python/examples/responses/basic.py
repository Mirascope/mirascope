from mirascope import llm

model = llm.model("openai/gpt-5-mini")
response: llm.Response = model.call("What is the capital of France?")

print(response.text())  # Prints the textual content of the response
