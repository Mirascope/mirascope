from mirascope import llm

llm.register_provider(
    "openai:completions",
    scope="ollama/",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


@llm.call("ollama/gpt-oss:20b")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    response: llm.Response = recommend_book("fantasy")
    print(response.pretty())


main()
