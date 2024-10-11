from mirascope.core import bedrock, prompt_template


def parse_recommendation(response: bedrock.BedrockCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@bedrock.call(
    "anthropic.claude-3-haiku-20240307-v1:0", output_parser=parse_recommendation
)
@prompt_template("Recommend a {genre} book. Output only Title by Author")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
