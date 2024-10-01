from mirascope.core import prompt_template, vertex


def parse_recommendation(response: vertex.VertexCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@vertex.call("gemini-1.5-flash", output_parser=parse_recommendation)
@prompt_template("Recommend a {genre} book. Output only Title by Author")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
