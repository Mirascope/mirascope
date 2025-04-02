# MCP Client

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading and learning about [Model Context Protocol](https://github.com/modelcontextprotocol)
    </div>

MCP Client in Mirascope enables you to interact with MCP servers through a standardized protocol. The client provides methods to access resources, tools, and prompts exposed by MCP servers.

## Basic Usage and Syntax

Let's connect to our book recommendation server using the MCP client:

!!! mira ""

    ```python hl_lines="10-14 18"
    --8<-- "examples/learn/mcp/client.py:1:20"
    --8<-- "examples/learn/mcp/client.py:48:50"
    ```

This example demonstrates:

1. Creating server parameters with `StdioServerParameters`
2. Using the `stdio_client` context manager to connect to the server
3. Accessing the list of available prompts

## Client Components

### Standard In/Out (stdio) Server Connection

To connect to an MCP server, use the `stdio_client` context manager with appropriate server parameters:

!!! mira ""

    ```python hl_lines="1 3-7 11"
    --8<-- "examples/learn/mcp/client.py:8:20"
    ```

The `StdioServerParameters` specify how to launch and connect to the server process.

### Server Side Events (sse) Server Connection

You can also use the `sse_client` instead to connect to an MCP server side event endpoint:

!!! mira ""

    ```python hl_lines="4"
    from mirascope.mcp import sse_client


    async with sse_client("http://localhost:8000") as client:
        prompts = await client.list_prompts()
        print(prompts[0])
    ```

### Prompts

You can list available prompts and get prompt templates from the server:

!!! mira ""

    ```python
    --8<-- "examples/learn/mcp/client.py:19:25"
    ```

The client automatically converts server prompts into Mirascope-compatible prompt templates that return `BaseMessageParam` instances. This makes it easy to consume these prompts downstream in your Mirascope code.

### Resources

Resources can be listed and read from the server:

!!! mira ""

    ```python
    --8<-- "examples/learn/mcp/client.py:27:32"
    ```

The client provides methods to:

- `list_resources()`: Get available resources
- `read_resource(uri)`: Read resource content by URI

If the resource is text, it will be converted into a `TextPart` instance. Otherwise it will be the MCP `BlobResourceContents` type where the data contained is the original bytes encoded as a base64 string.

### Tools

Tools from the server can be used with Mirascope's standard call decorators:

```python hl_lines="1 6 11-14"
--8<-- "examples/learn/mcp/client.py:34:47"
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
