from mirascope import llm


@llm.call("openai/gpt-5")
def recommend_book(genre: str):
    return [
        # [!code highlight]
        llm.messages.system("Always recommend kid-friendly books."),
        llm.messages.user(f"Please recommend a book in {genre}."),
    ]


def main():
    response: llm.Response = recommend_book("fantasy")
    print(response.pretty())


main()
