from mirascope.core import prompt_template, xai

# [!code highlight:4]
@xai.call("grok-3")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response: xai.XAICallResponse = recommend_book("fantasy")
print(response.content)
