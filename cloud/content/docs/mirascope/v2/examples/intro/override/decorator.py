from mirascope import llm


@llm.call(provider="openai", model_id="gpt-5")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


def main():
    # [!code highlight:2]
    with llm.model(provider="anthropic", model_id="claude-sonnet-4-0", temperature=1):
        response: llm.Response = recommend_book("fantasy")
        print(response.pretty())


main()
