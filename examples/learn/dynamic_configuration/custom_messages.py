from mirascope.core import openai


@openai.call("gpt-4o-mini")
def recommend_book(genre: str, style: str) -> openai.OpenAIDynamicConfig:
    return {
        "messages": [
            {"role": "system", "content": "You are a helpful book recommender."},
            {
                "role": "user",
                "content": f"Recommend a {genre} book in the style of {style}.",
            },
        ]
    }


response = recommend_book("science fiction", "cyberpunk")
print(response.content)
