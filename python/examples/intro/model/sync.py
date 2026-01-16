from mirascope import llm


def recommend_book(genre: str) -> llm.Response:
    model: llm.Model = llm.use_model("openai/gpt-5")
    return model.call(f"Please recommend a book in {genre}.")


def main():
    response: llm.Response = recommend_book("fantasy")
    print(response.pretty())


main()
