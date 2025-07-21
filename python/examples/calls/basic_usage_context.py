from dataclasses import dataclass

from mirascope import llm


@dataclass
class UserProfile:
    favorite_author: str


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str, ctx: llm.Context[UserProfile]) -> str:
    return (
        f"Recommend a {genre} book. My favorite author is {ctx.deps.favorite_author}."
    )


def main():
    profile = UserProfile(favorite_author="Brandon Sanderson")
    ctx = llm.Context(deps=profile)
    response: llm.Response = recommend_book.call("fantasy", ctx=ctx)
    print(response.content)


main()
