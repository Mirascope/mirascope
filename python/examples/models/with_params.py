from mirascope import llm

model = llm.use_model("openai/gpt-4o", temperature=0.7, max_tokens=500)
message = llm.messages.user("Write a haiku about programming.")
response = model.call(messages=[message])
print(response.pretty())
