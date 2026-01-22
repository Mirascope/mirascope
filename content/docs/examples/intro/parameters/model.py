from mirascope import llm


def recommend_book(genre: str) -> llm.Response:
    model = llm.use_model(
        "openai/gpt-5",
        temperature=1,  # [!code highlight]
    )
    message = llm.messages.user(f"Please recommend a book in {genre}.")
    return model.call(messages=[message])


def main():
    response: llm.Response = recommend_book("fantasy")
    print(response.pretty())


main()
