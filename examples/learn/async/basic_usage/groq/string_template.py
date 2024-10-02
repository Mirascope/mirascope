import asyncio

from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-70b-versatile")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str): ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
