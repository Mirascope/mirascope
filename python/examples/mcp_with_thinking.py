import asyncio

from mirascope import llm


async def main():
    async with llm.mcp.streamable_http_client(
        "https://gofastmcp.com/mcp"
    ) as mcp_client:
        tools = await mcp_client.list_tools()

        @llm.call(
            "google/gemini-3-flash-preview",
            thinking={"level": "medium", "include_thoughts": True},
            tools=tools,
        )
        async def learn_mcp():
            return "Use the tools to learn about FastMCP, and write a report on the library."

        response = await learn_mcp.stream()
        while True:  # Loop for tool calls
            # Use pretty_stream to see the tool calls for debug purposes
            async for chunk in response.pretty_stream():
                print(chunk, flush=True, end="")
            print()

            if response.tool_calls:
                tool_output = await response.execute_tools()
                response = await response.resume(tool_output)
            else:
                break


if __name__ == "__main__":
    asyncio.run(main())
