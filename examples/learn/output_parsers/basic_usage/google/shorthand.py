from mirascope.core import google


def parse_recommendation(response: google.GoogleCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@google.call("gemini-1.5-flash", output_parser=parse_recommendation)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book. Output only Title by Author"


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
