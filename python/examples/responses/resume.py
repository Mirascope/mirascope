from mirascope import llm

model = llm.Model("openai/gpt-4o")
response = model.call("What's the capital of France?")
print(response.text())

# Continue the conversation with the same model and message history
followup = response.resume("What's the population of that city?")
print(followup.text())

# Chain multiple turns
another = followup.resume("What famous landmarks are there?")
print(another.text())
