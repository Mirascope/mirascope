import asyncio

from mirascope import llm


async def main():
    async with llm.mcp.streamable_http_client("https://gofastmcp.com/mcp") as client:
        tools = await client.list_tools()

        @llm.prompt(tools=tools)
        async def assistant(query: str):
            return query

        response = await assistant(
            "openai/gpt-5-mini", "Give me a getting started primer on FastMCP."
        )

        while response.tool_calls:
            tool_outputs = await response.execute_tools()
            response = await response.resume(tool_outputs)

        print(response.pretty())


asyncio.run(main())
