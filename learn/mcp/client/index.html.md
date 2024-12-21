# MCP Client

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [MCP Server](./server.md)
    </div>

MCP Client in Mirascope enables you to interact with MCP servers through a standardized protocol. The client provides methods to access resources, tools, and prompts exposed by MCP servers.

## Basic Usage and Syntax

Let's connect to our book recommendation server using the MCP client:

```python hl_lines="11-15 19-26 28-33 35 39 44-47"
    import asyncio

    from pathlib import Path

    from mirascope.core import openai
    from mirascope.mcp.client import create_mcp_client, StdioServerParameters


    server_file = Path(__file__).parent / "server.py"

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", str(server_file)],
        env=None,
    )


    async def main() -> None:
        async with create_mcp_client(server_params) as client:
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

            @openai.call(
                "gpt-4o-mini",
                tools=tools,
            )
            def recommend_book(genre: str) -> str:
                return f"Recommend a {genre} book"

            if tool := recommend_book("fantasy").tool:
                call_result = await tool.call()
                print(call_result)
                # ['The Name of the Wind by Patrick Rothfuss']


    asyncio.run(main())
```

This example demonstrates:

1. Creating server parameters with `StdioServerParameters`
2. Using the `create_mcp_client` context manager to connect to the server
3. Accessing server components:
   - Listing and using prompts
   - Reading resources 
   - Using tools with Mirascope calls

## Client Components

### Server Connection

To connect to an MCP server, use the `create_mcp_client` context manager with appropriate server parameters:

```python hl_lines="3-7 11"
    server_file = Path(__file__).parent / "server.py"

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", str(server_file)],
        env=None,
    )


    async def main() -> None:
        async with create_mcp_client(server_params) as client:
```

The `StdioServerParameters` specify how to launch and connect to the server process.

### Prompts

You can list available prompts and get prompt templates from the server:

```python
            prompts = await client.list_prompts()
            print(prompts[0])
            # name='recommend_book' description='Get book recommendations by genre.' arguments=[PromptArgument(name='genre', description='Genre of book to recommend (fantasy, mystery, sci-fi, etc.)', required=True)]
            prompt_template = await client.get_prompt_template(prompts[0].name)
            prompt = await prompt_template(genre="fantasy")
            print(prompt)
            # [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

The client automatically converts server prompts into Mirascope-compatible prompt templates that return `BaseMessageParam` instances.

### Resources

Resources can be listed and read from the server:

```python
            resources = await client.list_resources()
            resource = await client.read_resource(resources[0].uri)
            print(resources[0])
            # uri=AnyUrl('file://books.txt/') name='Books Database' description='Read the books database file.' mimeType='text/plain'
            print(resource)
            # ['The Name of the Wind by Patrick Rothfuss\nThe Silent Patient by Alex Michaelides']
```

The client provides methods to:
- `list_resources()`: Get available resources
- `read_resource(uri)`: Read resource content by URI

### Tools

Tools from the server can be used with Mirascope's standard call decorators:

```python hl_lines="1 5 10-13"
            tools = await client.list_tools()

            @openai.call(
                "gpt-4o-mini",
                tools=tools,
            )
            def recommend_book(genre: str) -> str:
                return f"Recommend a {genre} book"

            if tool := recommend_book("fantasy").tool:
                call_result = await tool.call()
                print(call_result)
                # ['The Name of the Wind by Patrick Rothfuss']
```

The client automatically converts server tools into Mirascope-compatible tool types that can be used with any provider's call decorator.

## Type Safety

The MCP client preserves type information from the server:

1. **Prompts**: Arguments and return types from server prompt definitions
2. **Resources**: MIME types and content types for resources
3. **Tools**: Input schemas and return types for tools

This enables full editor support and type checking when using server components.


## Next Steps

By using the MCP client with Mirascope's standard features like [Calls](../calls.md), [Tools](../tools.md), and [Prompts](../prompts.md), you can build powerful applications that leverage local services through MCP servers.
