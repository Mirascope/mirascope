from mirascope.core import bedrock, prompt_template


@bedrock.call("amazon.nova-lite-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response: bedrock.BedrockCallResponse = recommend_book("fantasy")
print(response.content)
