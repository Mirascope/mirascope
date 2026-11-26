from mirascope import llm

model = llm.model("openai/gpt-6.1-terra")
response: llm.Response = model.call("What is the capital of France?")

print(response.text())  # Prints the textual content of the response
