from mirascope import llm


@llm.call("mlx-community/Qwen3-8B-4bit-DWQ-053125")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    response: llm.Response = recommend_book("fantasy")
    print(response.pretty())


main()
