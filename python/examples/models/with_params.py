from mirascope import llm

model = llm.use_model("openai/gpt-4o", temperature=0.7, max_tokens=500)
response = model.call("Write a haiku about programming.")
print(response.pretty())
