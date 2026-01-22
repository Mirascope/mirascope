from mirascope import llm


@llm.call("openai/gpt-5")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


def main():
    response: llm.Response = recommend_book("fantasy")
    print(response.pretty())


main()
