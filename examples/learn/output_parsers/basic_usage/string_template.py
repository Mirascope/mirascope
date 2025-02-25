from mirascope import llm, prompt_template


def parse_recommendation(response: llm.CallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@llm.call(provider="openai", model="gpt-4o-mini", output_parser=parse_recommendation)
@prompt_template("Recommend a {genre} book. Output only Title by Author")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
