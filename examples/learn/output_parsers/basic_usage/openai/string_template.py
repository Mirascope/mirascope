from mirascope.core import openai, prompt_template


def parse_recommendation(response: openai.OpenAICallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@openai.call("gpt-4o-mini", output_parser=parse_recommendation)
@prompt_template("Recommend a {genre} book. Output only Title by Author")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
