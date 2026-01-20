from mirascope import llm


@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


max_retries = 3
response = recommend_book.stream("fantasy")
for attempt in range(max_retries):
    try:
        for chunk in response.text_stream():
            print(chunk, end="", flush=True)
        break
    except llm.Error:
        if attempt == max_retries - 1:
            raise
        # Stream failed mid-way. Resume from where we left off.
        response = response.resume("Please continue.")
