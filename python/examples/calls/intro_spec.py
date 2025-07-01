from mirascope import llm


@llm.call("openai:gpt-4o-mini")
@llm.prompt_template("Recommend a {{ genre }} book")
def recommend_book(genre: str): ...


response: llm.SimpleResponse = recommend_book("fantasy")
print(response.text)
# "Here are a few highly recommended fantasy books..."
