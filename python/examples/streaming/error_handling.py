from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book.stream("fantasy")

try:
    for chunk in response.pretty_stream():
        print(chunk, end="", flush=True)
    print()
except llm.RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except llm.ConnectionError as e:
    print(f"Connection error: {e}")
except llm.APIError as e:
    print(f"API error during streaming: {e}")
