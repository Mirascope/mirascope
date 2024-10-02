import asyncio

from mirascope.core import anthropic, prompt_template


@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
