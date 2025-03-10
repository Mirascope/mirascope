# MCP Client

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [MCP Server](./server.md)
    </div>

MCP Client in Mirascope enables you to interact with MCP servers through a standardized protocol. The client provides methods to access resources, tools, and prompts exposed by MCP servers.

## Basic Usage and Syntax

Let's connect to our book recommendation server using the MCP client:

```python hl_lines="11-15 19-26 28-33 35 39 44-47"
--8<-- "examples/learn/mcp/client.py"
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
--8<-- "examples/learn/mcp/client.py:9:19"
```

The `StdioServerParameters` specify how to launch and connect to the server process.

### Prompts

You can list available prompts and get prompt templates from the server:

```python
--8<-- "examples/learn/mcp/client.py:20:26"
```

The client automatically converts server prompts into Mirascope-compatible prompt templates that return `BaseMessageParam` instances.

### Resources

Resources can be listed and read from the server:

```python
--8<-- "examples/learn/mcp/client.py:28:33"
```

The client provides methods to:
- `list_resources()`: Get available resources
- `read_resource(uri)`: Read resource content by URI

### Tools

Tools from the server can be used with Mirascope's standard call decorators:

```python hl_lines="1 5 10-13"
--8<-- "examples/learn/mcp/client.py:35:47"
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
