from mirascope import llm

llm.register_provider(
    "openai:completions",
    scope="ollama/",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


def recommend_book(genre: str) -> llm.Response:
    model: llm.Model = llm.use_model("ollama/gpt-oss:20b")
    message = llm.messages.user(f"Recommend a {genre} book.")
    return model.call(messages=[message])


response = recommend_book("fantasy")
print(response.pretty())
