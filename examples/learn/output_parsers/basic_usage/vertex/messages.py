from mirascope.core import Messages, vertex


def parse_recommendation(response: vertex.VertexCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@vertex.call("gemini-1.5-flash", output_parser=parse_recommendation)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
