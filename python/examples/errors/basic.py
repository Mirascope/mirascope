from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


try:
    response = recommend_book("fantasy")
    print(response.pretty())
except llm.AuthenticationError as e:
    print(f"Invalid API key: {e}")
except llm.RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except llm.Error as e:
    print(f"LLM error: {e}")
