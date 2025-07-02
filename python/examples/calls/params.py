from mirascope import llm


@llm.call(
    "openai:gpt-4o-mini",
    temperature=0.7,
    max_tokens=512,
)
def recommend_book(genre: str):
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.text)
# "Here's a great fantasy book recommendation: 'The Name of the Wind' by Patrick Rothfuss..."
