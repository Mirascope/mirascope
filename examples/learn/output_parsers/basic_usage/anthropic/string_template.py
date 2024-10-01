from mirascope.core import anthropic, prompt_template


def parse_recommendation(response: anthropic.AnthropicCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@anthropic.call("claude-3-5-sonnet-20240620", output_parser=parse_recommendation)
@prompt_template("Recommend a {genre} book. Output only Title by Author")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
