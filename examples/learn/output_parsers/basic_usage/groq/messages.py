from mirascope.core import Messages, groq


def parse_recommendation(response: groq.GroqCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@groq.call("llama-3.1-70b-versatile", output_parser=parse_recommendation)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
