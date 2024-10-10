from mirascope.core import Messages, bedrock


def parse_recommendation(response: bedrock.BedrockCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@bedrock.call(
    "anthropic.claude-3-haiku-20240307-v1:0", output_parser=parse_recommendation
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
