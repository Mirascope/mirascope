from mirascope import llm

models = [
    "openai/gpt-4o-mini",
    "anthropic/claude-3-5-haiku-latest",
    "google/gemini-2.0-flash",
]


def recommend_book(model: llm.Model, genre: str):
    return model.call(f"Recommend a {genre} book.")


def with_fallbacks(genre: str, max_retries: int = 3) -> llm.Response:
    errors: list[llm.APIError] = []
    for model_id in models:
        model = llm.model(model_id)
        for attempt in range(max_retries):
            try:
                return recommend_book(model, genre)
            except llm.APIError as e:
                errors.append(e)
                if attempt == max_retries - 1:
                    break  # Try next model
    # Re-raise last error (simple approach)
    raise errors[-1]


response = with_fallbacks("fantasy")
print(response.pretty())
