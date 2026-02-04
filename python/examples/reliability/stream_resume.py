from mirascope import llm

# Use a `llm.Model` (not `llm.RetryModel`) for manual control when resuming the
# stream response.
model = llm.Model("openai/gpt-4o-mini")
response = model.stream("Tell me a story about a wizard")

max_retries = 3
for attempt in range(max_retries + 1):
    try:
        for chunk in response.text_stream():
            # Each chunk of text gets added to `response.content` as part
            # of the final final assistant message in `response.messages`.
            # This state accumulates even if the response is later interrupted.
            print(chunk, end="", flush=True)
        break  # Stream completed successfully
    except llm.Error:
        if attempt == max_retries:
            raise
        print("\n[Error occurred, continuing from where we left off...]\n")
        # Manually calling `response.resume` uses the partially-streamed text
        # content above, as well as any tool calls that fully streamed. (Partial
        # tool calls are discarded).
        # This differs from using a `RetryStreamResponse`, which would restart
        # the stream without persisting any partially streamed content.
        response = response.resume("Please continue from where you left off.")
