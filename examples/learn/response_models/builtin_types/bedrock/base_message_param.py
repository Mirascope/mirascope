from mirascope.core import BaseMessageParam, bedrock


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=list[str])
def extract_book(texts: list[str]) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


book = extract_book(
    [
        "The Name of the Wind by Patrick Rothfuss",
        "Mistborn: The Final Empire by Brandon Sanderson",
    ]
)
print(book)
# Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
