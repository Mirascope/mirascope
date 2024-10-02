from mirascope.core import groq, prompt_template


def parse_recommendation(response: groq.GroqCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@groq.call("llama-3.1-70b-versatile", output_parser=parse_recommendation)
@prompt_template("Recommend a {genre} book. Output only Title by Author")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
