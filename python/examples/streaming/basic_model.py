from mirascope import llm

model = llm.use_model("openai/gpt-5-mini")
messages = [llm.messages.user("Recommend a fantasy book.")]

response: llm.StreamResponse = model.stream(messages=messages)
for chunk in response.pretty_stream():
    print(chunk, end="", flush=True)
print()
