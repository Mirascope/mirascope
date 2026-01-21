from cohere import Client

client = Client()


def recommend_book(genre: str) -> str:
    # [!code highlight:6]
    response = client.chat(
        model="command-r-plus",
        message=f"Recommend a {genre} book",
    )
    return response.text


output = recommend_book("fantasy")
print(output)
