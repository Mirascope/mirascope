from mirascope import llm

model = llm.retry_model("openai/gpt-4o-mini")
response = model.stream("Tell me a story about a wizard")

while True:
    try:
        for chunk in response.text_stream():
            print(chunk, end="", flush=True)
        break  # Stream completed successfully
    except llm.StreamRestarted:
        print("\n[Stream restarted due to error, retrying...]\n")
        # Loop continues with the restarted stream
