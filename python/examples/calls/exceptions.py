from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    response = recommend_book("fantasy")
    print(response.text)
except llm.RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print(f"Original provider error: {e.original_exception}")
except llm.AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print(f"Original provider error: {e.original_exception}")
except llm.ConnectionError as e:
    print(f"Connection error: {e}")
    print(f"Original provider error: {e.original_exception}")
except llm.APIError as e:
    print(f"API error ({e.status_code}): {e}")
    print(f"Provider: {e.provider}")
    print(f"Original provider error: {e.original_exception}")
except Exception as e:
    print(f"Unexpected error: {e}")
