from mirascope.core import cohere, prompt_template


def parse_recommendation(response: cohere.CohereCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@cohere.call("command-r-plus", output_parser=parse_recommendation)
@prompt_template("Recommend a {genre} book. Output only Title by Author")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
