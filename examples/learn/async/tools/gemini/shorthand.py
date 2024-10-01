import asyncio

from mirascope.core import BaseTool, gemini


class FormatBook(BaseTool):
    title: str
    author: str

    async def call(self) -> str:
        # Simulating an async API call
        await asyncio.sleep(1)
        return f"{self.title} by {self.author}"


@gemini.call("gemini-1.5-flash", tools=[FormatBook])
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    response = await recommend_book("fantasy")
    if tool := response.tool:
        if isinstance(tool, FormatBook):
            output = await tool.call()
            print(output)
    else:
        print(response.content)


asyncio.run(main())
