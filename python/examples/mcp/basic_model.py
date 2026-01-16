import asyncio

from mirascope import llm


async def main():
    async with llm.mcp.streamable_http_client("https://gofastmcp.com/mcp") as client:
        tools = await client.list_tools()

        model = llm.use_model("openai/gpt-5-mini")
        response = await model.call_async(
            "Give me a getting started primer on FastMCP.",
            tools=tools,
        )

        while response.tool_calls:
            tool_outputs = await response.execute_tools()
            response = await response.resume(tool_outputs)

        print(response.pretty())


asyncio.run(main())
