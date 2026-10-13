from mirascope.core import mistral, prompt_template

# [!code highlight:4]
@mistral.call("mistral-large-latest")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response: mistral.MistralCallResponse = recommend_book("fantasy")
print(response.content)
