from mirascope.core import Messages, groq


@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response: groq.GroqCallResponse = recommend_book("fantasy")
print(response.content)
