from mirascope.core import Messages, openai


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response: openai.OpenAICallResponse = recommend_book("fantasy")
print(response.content)
