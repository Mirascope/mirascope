from cohere import Client

client = Client()


def recommend_book(genre: str) -> str:
    response = client.chat(
        model="command-r-plus",
        message=f"Recommend a {genre} book",
    )
    return response.text


print(recommend_book("fantasy"))
