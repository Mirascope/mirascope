from mirascope import llm

model = llm.Model("openai/gpt-5-mini")

response: llm.StreamResponse = model.stream("Recommend a fantasy book.")
for chunk in response.text_stream():
    print(chunk, end="", flush=True)
