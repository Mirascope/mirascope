from mirascope import llm


def recommend_book(genre: str) -> llm.Response:
    # [!code highlight:2]
    model = llm.use_model(provider="openai", model_id="gpt-4o-mini")
    message = llm.messages.user(f"Please recommend a book in {genre}.")
    return model.call(messages=[message])


def main():
    # [!code highlight:2]
    with llm.model(provider="anthropic", model_id="claude-sonnet-4-0", temperature=1):
        response: llm.Response = recommend_book("fantasy")
        print(response.pretty())


main()
