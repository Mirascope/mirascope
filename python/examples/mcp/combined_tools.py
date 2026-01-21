import asyncio

from mirascope import llm


@llm.tool
async def search_codebase(pattern: str) -> str:
    """Search the local codebase for a pattern using ripgrep."""
    proc = await asyncio.create_subprocess_exec(
        "rg",
        "--max-count=5",
        pattern,
        "./",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode() or "No matches found."


async def main():
    async with llm.mcp.streamable_http_client("https://gofastmcp.com/mcp") as client:
        mcp_tools = await client.list_tools()
        all_tools = [search_codebase, *mcp_tools]

        @llm.call("openai/gpt-5-mini", tools=all_tools)
        async def assistant(query: str):
            return query

        response = await assistant(
            "How does FastMCP handle tool registration? "
            "Search the FastMCP docs, then check our codebase for similar patterns."
        )

        while response.tool_calls:
            print(response.pretty())
            tool_outputs = await response.execute_tools()
            response = await response.resume(tool_outputs)

        print(response.pretty())


asyncio.run(main())
