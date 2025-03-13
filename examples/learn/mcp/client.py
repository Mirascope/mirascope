import asyncio
from pathlib import Path

from mcp.client.stdio import StdioServerParameters
from mirascope import llm
from mirascope.mcp import stdio_client

server_file = Path(__file__).parent / "server.py"

server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", str(server_file)],
    env=None,
)


async def main() -> None:
    async with stdio_client(server_params) as client:
        prompts = await client.list_prompts()
        print(prompts[0])
        # name='recommend_book' description='Get book recommendations by genre.' arguments=[PromptArgument(name='genre', description='Genre of book to recommend (fantasy, mystery, sci-fi, etc.)', required=True)]
        prompt_template = await client.get_prompt_template(prompts[0].name)
        prompt = await prompt_template(genre="fantasy")
        print(prompt)
        # [BaseMessageParam(role='user', content='Recommend a fantasy book')]

        resources = await client.list_resources()
        resource = await client.read_resource(resources[0].uri)
        print(resources[0])
        # uri=AnyUrl('file://books.txt/') name='Books Database' description='Read the books database file.' mimeType='text/plain'
        print(resource)
        # ['The Name of the Wind by Patrick Rothfuss\nThe Silent Patient by Alex Michaelides']

        tools = await client.list_tools()

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
            tools=tools,
        )
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"

        if tool := recommend_book("fantasy").tool:
            call_result = await tool.call()
            print(call_result)
            # ['The Name of the Wind by Patrick Rothfuss']


asyncio.run(main())
