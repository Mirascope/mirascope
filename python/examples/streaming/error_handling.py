from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book.stream("fantasy")

try:
    for chunk in response.text_stream():
        print(chunk, end="", flush=True)
except llm.RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except llm.ConnectionError as e:
    print(f"Connection error: {e}")
except llm.Error as e:
    print(f"Error during streaming: {e}")
