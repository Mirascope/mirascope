from mirascope.core import BaseMessageParam, azure


def parse_recommendation(response: azure.AzureCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@azure.call("gpt-4o-mini", output_parser=parse_recommendation)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=f"Recommend a {genre} book. Output only Title by Author",
        )
    ]


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
