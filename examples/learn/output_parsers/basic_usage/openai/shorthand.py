from mirascope.core import openai


def parse_recommendation(response: openai.OpenAICallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@openai.call("gpt-4o-mini", output_parser=parse_recommendation)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book. Output only Title by Author"


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
