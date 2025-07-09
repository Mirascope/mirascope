from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


recommendation: llm.Response = recommend_book("fantasy")

# For a response with a single piece of text content, you can get the text by casting
# the response to string:
representation = str(recommendation)  # [!code highlight]

# Or you can retrieve the wrapped Text via the `.text` property:
text: str | None = recommendation.text  # [!code highlight]

assert representation == text
print(text)
# "Here are some fantasy books you may enjoy..."
