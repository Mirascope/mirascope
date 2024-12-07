# MCP Server

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Tools](../tools.md)
    </div>

MCP (Model Context Protocol) Server in Mirascope enables you to expose resources, tools, and prompts to LLM clients through a standardized protocol. This allows for secure and controlled interactions between host applications (like Claude Desktop) and local services.

## Basic Usage and Syntax

Let's build a simple book recommendation server using MCP:

```python  hl_lines="7 10 27-32 40"
--8<-- "examples/learn/mcp/server_decorators.py:3"
```

This example demonstrates:

1. Creating an MCP server with the `MCPServer` class
2. Registering a tool to get book recommendations by genre
3. Exposing a books database as a resource
4. Creating a prompt template for book recommendations
5. Running the server asynchronously

## Server Components

### Tools

Tools in MCP Server expose callable functions to clients. Tools can be registered using the `@app.tool()` decorator, which follows the same patterns as described in the [Tools](../tools.md) documentation:

```python
--8<-- "examples/learn/mcp/server_decorators.py:12:26"
```

The `@app.tool()` decorator supports all the same functionality as the standard Mirascope tool decorators, including:

- Function-based tools
- Class-based tools inheriting from `BaseTool`
- Tool configurations and validation
- Computed fields and dynamic configuration

See the [Tools documentation](../tools.md) for more details on defining and using tools.

### Resources

Resources provide access to data through URIs. They can be registered using the `@app.resource()` decorator with configuration options:

```python
--8<-- "examples/learn/mcp/server_decorators.py:29:39"
```

Resources support both synchronous and asynchronous functions, making them flexible for different types of data access.

### Prompts

Prompts define reusable message templates. They can be registered using the `@app.prompt()` decorator, which provides the same functionality as the standard Mirascope `@prompt_template` decorator described in the [Prompts](../prompts.md) documentation:

```python
--8<-- "examples/learn/mcp/server_decorators.py:42:49"
```

The `@app.prompt()` decorator supports all the features of standard Mirascope prompts, including:

- String templates
- Multi-line prompts
- Chat history
- Object attribute access
- Format specifiers
- Computed fields and dynamic configuration

See the [Prompts documentation](../prompts.md) for more details on creating and using prompts.

## Alternative Definition Style

In addition to using decorators, you can also define your functions first and then register them when creating the MCP server. This style enables better function reusability and separation of concerns:

```python hl_lines="46-59"
--8<-- "examples/learn/mcp/server.py:3:69"
```

This alternative style offers several advantages:

1. **Function Reusability**: Functions can be used both independently and as part of the MCP server
2. **Cleaner Separation**: Clear separation between function definitions and server configuration
3. **Easier Testing**: Functions can be tested in isolation before being registered with the server
4. **Code Organization**: Related functions can be grouped together in separate modules

The same applies for prompts defined with `@prompt_template` - see the [Prompts](../prompts.md) documentation for more details about prompt reusability.

Both the decorator style and this alternative style are fully supported - choose the one that better fits your application's needs.

## Next Steps

By leveraging MCP Server in Mirascope, you can create secure and standardized integrations between LLM clients and local services. This enables powerful capabilities while maintaining control over how LLMs interact with your systems.
