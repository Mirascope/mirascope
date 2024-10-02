from mirascope.core import BaseMessageParam, anthropic


def parse_recommendation(response: anthropic.AnthropicCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@anthropic.call("claude-3-5-sonnet-20240620", output_parser=parse_recommendation)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=f"Recommend a {genre} book. Output only Title by Author",
        )
    ]


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
