from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


def main():
    response: llm.Response = recommend_book("fantasy")
    print(response.content)


main()
