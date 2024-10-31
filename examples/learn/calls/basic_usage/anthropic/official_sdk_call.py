from anthropic import Anthropic

client = Anthropic()


def recommend_book(genre: str) -> str:
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
        max_tokens=1024,
    )
    block = message.content[0]
    return block.text if block.type == "text" else ""


output = recommend_book("fantasy")
print(output)
