from mirascope import llm


@llm.call("openai/gpt-5")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


def main():
    response: llm.StreamResponse = recommend_book.stream("fantasy")
    for chunk in response.pretty_stream():
        print(chunk, flush=True, end="")


main()
