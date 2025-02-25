from mirascope.core import google, prompt_template


@google.call("gemini-2.0-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response: google.GoogleCallResponse = recommend_book("fantasy")
print(response.content)
