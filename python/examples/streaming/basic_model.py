from mirascope import llm

model = llm.use_model("openai/gpt-5-mini")

response: llm.StreamResponse = model.stream("Recommend a fantasy book.")
for chunk in response.pretty_stream():
    print(chunk, end="", flush=True)
print()
