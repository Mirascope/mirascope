from mirascope.core import openai

# [!code highlight:4]
@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: openai.OpenAICallResponse = recommend_book("fantasy")
print(response.content)
