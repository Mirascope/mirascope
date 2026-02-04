from mirascope import llm


@llm.retry(
    max_retries=5,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    jitter=0.1,
    retry_on=(llm.RateLimitError, llm.ServerError),
)
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.text())
# > The Name of the Wind by Patrick Rothfuss
