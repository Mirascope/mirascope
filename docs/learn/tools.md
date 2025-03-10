---
search:
  boost: 2 
---

# Tools

{% set tool_methods = [["base_tool", "BaseTool"], ["function", "Function"]] %}

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Tools are user-defined functions that an LLM (Large Language Model) can ask the user to invoke on its behalf. This greatly enhances the capabilities of LLMs by enabling them to perform specific tasks, access external data, interact with other systems, and more.

Mirascope enables defining tools in a provider-agnostic way, which can be used across all supported LLM providers without modification.

??? info "Diagram illustrating how tools are called"

    When an LLM decides to use a tool, it indicates the tool name and argument values in its response. It's important to note that the LLM doesn't actually execute the function; instead, you are responsible for calling the tool and (optionally) providing the output back to the LLM in a subsequent interaction. For more details on such iterative tool-use flows, check out the [Tool Message Parameters](#tool-message-parameters) section below as well as the section on [Agents](./agents.md).

    ```mermaid
    sequenceDiagram
        participant YC as Your Code
        participant LLM

        YC->>LLM: Call with prompt and function definitions
        loop Tool Calls
            LLM->>LLM: Decide to respond or call functions
            LLM->>YC: Respond with function to call and arguments
            YC->>YC: Execute function with given arguments
            YC->>LLM: Call with prompt and function result
        end
        LLM->>YC: Final response
    ```

## Basic Usage and Syntax

??? api "API Documentation"

    [`mirascope.core.base.tool`](../api/core/base/tool.md)
    {% for provider in supported_llm_providers %}
    {% if provider == "LiteLLM" %}
    [`mirascope.core.litellm.tool`](../api/core/openai/tool.md)
    {% else %}
    [`mirascope.core.{{ provider | provider_dir }}.tool`](../api/core/{{ provider | provider_dir }}/tool.md)
    {% endif %}
    {% endfor %}

There are two ways of defining tools in Mirascope: [`BaseTool`](../api/core/base/tool.md) and functions.

You can consider the functional definitions a shorthand form of writing the `BaseTool` version of the same tool. Under the hood, tools defined as functions will get converted automatically into their corresponding `BaseTool`.

Let's take a look at a basic example of each using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if tool_method == "function" %}
                ```python hl_lines="4-15 18 24-26"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py::26"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py:28:"
                ```
                {% else %}
                ```python hl_lines="5-16 19 25-27"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py::27"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py:29:"
                ```
                {% endif %}
            {% endfor %}

        {% endfor %}

    {% endfor %}

??? note "Official SDK"

    {% for provider in supported_llm_providers %}
    === "{{ provider }}"

        {% if provider == "Anthropic" %}
        ```python hl_lines="6-12 20-30 33-36"
        {% elif provider == "Cohere" %}
        ```python hl_lines="9-15 22-32 34-36"
        {% elif provider == "Google" %}
        ```python hl_lines="7-13 21-37 30-46"
        {% elif provider == "LiteLLM" %}
        ```python hl_lines="6-12 19-32 34-36"
        {% elif provider == "Azure AI" %}
        ```python hl_lines="16-22 31-43 45-47"
        {% elif provider == "Mistral" %}
        ```python hl_lines="10-16 23-36 38-44"
        {% elif provider == "Bedrock" %}
        ```python hl_lines="6-12 18-37 49-55"
        {% else %}
        ```python hl_lines="8-14 21-34 36-38"
        {% endif %}
        --8<-- "examples/learn/tools/basic_usage/official_sdk/{{ provider | provider_dir }}_sdk.py"
        ```

    {% endfor %}

In this example we:

1. Define the `GetBookAuthor`/`get_book_author` tool (a dummy method for the example)
2. Set the `tools` argument in the `call` decorator to give the LLM access to the tool.
3. We call `identify_author`, which automatically generates the corresponding provider-specific tool schema under the hood.
4. Check if the response from `identify_author` contains a tool, which is the `BaseTool` instance constructed from the underlying tool call
    - If yes, we call the constructed tool's `call` method and print its output. This calls the tool with the arguments provided by the LLM.
    - If no, we print the content of the response (assuming no tool was called).

The core idea to understand here is that the LLM is asking us to call the tool on its behalf with arguments that it has provided. In the above example, the LLM chooses to call the tool to get the author rather than relying on its world knowledge.

This is particularly important for buildling applications with access to live information and external systems.

For the purposes of this example we are showing just a single tool call. Generally, you would then give the tool call's output back to the LLM and make another call so the LLM can generate a response based on the output of the tool. We cover this in more detail in the section on [Agents](./agents.md)

### Accessing Original Tool Call

The `BaseTool` instances have a `tool_call` property for accessing the original LLM tool call.

!!! mira ""

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if tool_method == "function" %}
                ```python hl_lines="26"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py::25"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py:27:"
                ```
                {% else %}
                ```python hl_lines="27"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py::26"
                --8<-- "build/snippets/learn/tools/basic_usage/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py:28:"
                ```
                {% endif %}
            {% endfor %}

        {% endfor %}
        
    {% endfor %}

## Supported Field Types

While Mirascope provides a consistent interface, type support varies among providers:

|     Type      | OpenAI | Anthropic | Google | Groq | xAI | Mistral | Cohere |
|---------------|--------|-----------|--------|------|-----|---------|--------|
|     str       | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | ✓      |
|     int       | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | ✓      |
|    float      | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | ✓      |
|     bool      | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | ✓      |
|     bytes     | ✓      | ✓         | -      | ✓    | ✓   | ✓       | ✓      |
|     list      | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | ✓      |
|     set       | ✓      | ✓         | -      | ✓    | ✓   | ✓       | ✓      |
|     tuple     | -      | ✓         | -      | ✓    | -   | ✓       | ✓      |
|     dict      | -      | ✓         | ✓      | ✓    | -   | ✓       | ✓      |
|  Literal/Enum | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | ✓      |
|   BaseModel   | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | -      |
| Nested ($def) | ✓      | ✓         | ✓      | ✓    | ✓   | ✓       | -      |

Legend: ✓ (Supported), - (Not Supported)

Consider provider-specific capabilities when working with advanced type structures. Even for supported types, LLM outputs may sometimes be incorrect or of the wrong type. In such cases, prompt engineering or error handling (like [retries](./retries.md) and [reinserting validation errors](./retries.md#error-reinsertion)) may be necessary.

## Parallel Tool Calls

In certain cases the LLM will ask to call multiple tools in the same response. Mirascope makes calling all such tools simple:

!!! mira ""

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if tool_method == "function" %}
                ```python hl_lines="23-26"
                {% else %}
                ```python hl_lines="24-27"
                {% endif %}
                --8<-- "build/snippets/learn/tools/parallel/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}

        {% endfor %}

    {% endfor %}

If your tool calls are I/O-bound, it's often worth writing [async tools](./async.md#async-tools) so that you can run all of the tools calls [in parallel](./async.md#parallel-async-calls) for better efficiency.

## Streaming Tools

Mirascope supports streaming responses with tools, which is useful for long-running tasks or real-time updates:

!!! mira ""

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if provider | provider_dir in ["openai", "anthropic", "mistral", "groq"] %}
                {% if tool_method == "function" %}
                ```python hl_lines="18 24-26"
                {% else %}
                ```python hl_lines="19 25-27"
                {% endif %}
                {% else %}
                ```python
                {% endif %}
                --8<-- "build/snippets/learn/tools/streams/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}

        {% endfor %}

    {% endfor %}

!!! note "When are tools returned?"

    When we identify that a tool is being streamed, we will internally reconstruct the tool from the streamed response. This means that the tool won't be returned until the full tool has been streamed and reconstructed on your behalf.

!!! warning "Not all providers support streaming tools"

    Currently only OpenAI, Anthropic, Mistral, and Groq support streaming tools. All other providers will always return `None` for tools.
    
    If you think we're missing any, let us know!

### Streaming Partial Tools

You can also stream intermediate partial tools and their deltas (rather than just the fully constructed tool) by setting `stream={"partial_tools": True}`:

!!! mira ""

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if provider | provider_dir in ["openai", "anthropic", "mistral", "groq"] %}
                {% if tool_method == "function" %}
                ```python hl_lines="22 30"
                {% else %}
                ```python hl_lines="23 31"
                {% endif %}
                {% else %}
                ```python
                {% endif %}               
                 --8<-- "build/snippets/learn/tools/partial_tool_streams/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}

        {% endfor %}

    {% endfor %}

## Tool Message Parameters

!!! mira ""

    <div align="center">
        Calling tools and inserting their outputs into subsequent LLM API calls in a loop in the most basic form of an agent. While we cover this briefly here, we recommend reading the section on [Agents](./agents.md) for more details and examples.
    </div>

Generally the next step after the LLM returns a tool call is for you to call the tool on its behalf and supply the output in a subsequent call.

Let's take a look at a basic example of this:

!!! mira ""

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if tool_method == "function" and method == "string_template" %}
                ```python hl_lines="16 21 30-32 35"
                {% elif tool_method == "function" %}
                ```python hl_lines="15 17 27-29 32"
                {% elif method == "string_template" %}
                ```python hl_lines="19 24 33-35 38"
                {% else %}
                ```python hl_lines="18 20 30-32 35"
                {% endif %}
                --8<-- "build/snippets/learn/tools/tool_message_params/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}

        {% endfor %}

    {% endfor %}

In this example we:

1. Add `history` to maintain the messages across multiple calls to the LLM.
2. Loop until the response no longer has tools calls.
3. While there are tool calls, call the tools, append their corresponding message parameters to the history, and make a subsequent call with an empty query and updated history. We use an empty query because the original user message is already included in the history.
4. Print the final response content once the LLM is done calling tools.

## Validation and Error Handling

Since `BaseTool` is a subclass of Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), they are validated on construction, so it's important that you handle potential `ValidationError`'s for building more robust applications:

!!! mira ""

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if tool_method == "function" %}
                ```python hl_lines="12 32 37"
                {% else %}
                ```python hl_lines="15 34 39"
                {% endif %}
                --8<-- "build/snippets/learn/tools/validation/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}

        {% endfor %}

    {% endfor %}

In this example we've added additional validation, but it's important that you still handle `ValidationError`'s even with standard tools since they are still `BaseModel` instances and will validate the field types regardless.

## Few-Shot Examples

Just like with [Response Models](./response_models.md#few-shot-examples), you can add few-shot examples to your tools:

!!! mira ""

    {% for tool_method, tool_method_title in tool_methods %}
    === "{{ tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"
                {% if tool_method == "function" %}
                ```python hl_lines="14 20-21"
                {% else %}
                ```python hl_lines="11 15"
                {% endif %}
                --8<-- "build/snippets/learn/tools/few_shot_examples/{{ tool_method }}/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}

        {% endfor %}

    {% endfor %}

Both approaches will result in the same tool schema with examples included. The function approach gets automatically converted to use Pydantic fields internally, making both methods equivalent in terms of functionality.

!!! note "Field level examples in both styles"
    Both `BaseTool` and function-style definitions support field level examples through Pydantic's `Field`. When using function-style definitions, you'll need to wrap the type with `Annotated` to use `Field`.

## ToolKit

??? api "API Documentation"

    [`mirascope.core.base.toolkit`](../api/core/base/toolkit.md)

The `BaseToolKit` class enables:

- Organiziation of a group of tools under a single namespace.
    - This can be useful for making it clear to the LLM when to use certain tools over others. For example, you could namespace a set of tools under "file_system" to indicate that those tools are specifically for interacting with the file system.
- Dynamic tool definitions.
    - This can be useful for generating tool definitions that are dependent on some input or state. For example, you may want to update the description of tools based on an argument of the call being made.

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
            {% else %}
            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
            {% endif %}
            --8<-- "build/snippets/learn/tools/toolkit/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

In this example we:

1. Create a `BookTools` toolkit
2. We set `__namespace__` equal to "book_tools"
3. We define the `reading_level` state of the toolkit
4. We define the `suggest_author` tool and mark it with `@toolkit_tool` to identify the method as a tool of the toolkit
5. We use the `{self.reading_level}` template variable in the description of the tool.
6. We create the toolkit with the `reading_level` argument.
7. We call `create_tools` to generate the toolkit's tools. This will generate the tools on every call, ensuring that the description correctly includes the provided reading level.
8. We call `recommend_author` with a "beginner" reading level, and the LLM calls the `suggest_author` tool with its suggested author.
9. We call `recommend_author` again but with "advanced" reading level, and again the LLM calls the `suggest_author` tool with its suggested author.

The core concept to understand here is that the `suggest_author` tool's description is dynamically generated on each call to `recommend_author` through the toolkit.

This is why the "beginner" recommendation and "advanced" recommendations call the `suggest_author` tool with authors befitting the reading level of each call.

## Pre-Made Tools and ToolKits

Mirascope provides several pre-made tools and toolkits to help you get started quickly:

!!! warning "Dependencies Required"
    Pre-made tools and toolkits require installing the dependencies listed in the "Dependencies" column for each tool/toolkit. 
    
    For example:
    ```bash
    pip install httpx  # For HTTPX tool
    pip install requests  # For Requests tool
    ```

### Pre-Made Tools

??? api "API Documentation"

    - [`mirascope.tools.web.DuckDuckGoSearch`](../api/tools/web/duckduckgo.md)
    - [`mirascope.tools.web.HTTPX`](../api/tools/web/httpx.md)
    - [`mirascope.tools.web.ParseURLContent`](../api/tools/web/parse_url_content.md)
    - [`mirascope.tools.web.Requests`](../api/tools/web/requests.md)

| Tool | Primary Use | Dependencies | Key Features | Characteristics |
|------|-------------|--------------|--------------|-----------------|
| [`DuckDuckGoSearch`](../api/tools/web/duckduckgo.md) | Web Searching | [`duckduckgo-search`](https://pypi.org/project/duckduckgo-search/) | • Multiple query support<br>• Title/URL/snippet extraction<br>• Result count control<br>• Automated formatting | • Privacy-focused search<br>• Async support (AsyncDuckDuckGoSearch)<br>• Automatic filtering<br>• Structured results |
| [`HTTPX`](../api/tools/web/httpx.md) | Advanced HTTP Requests | [`httpx`](https://pypi.org/project/httpx/) | • Full HTTP method support (GET/POST/PUT/DELETE)<br>• Custom header support<br>• File upload/download<br>• Form data handling | • Async support (AsyncHTTPX)<br>• Configurable timeouts<br>• Comprehensive error handling<br>• Redirect control |
| [`ParseURLContent`](../api/tools/web/parse_url_content.md) | Web Content Extraction | [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/), [`httpx`](https://pypi.org/project/httpx/) | • HTML content fetching<br>• Main content extraction<br>• Element filtering<br>• Text normalization | • Automatic cleaning<br>• Configurable parser<br>• Timeout settings<br>• Error handling |
| [`Requests`](../api/tools/web/requests.md) | Simple HTTP Requests | [`requests`](https://pypi.org/project/requests/) | • Basic HTTP methods<br>• Simple API<br>• Response text retrieval<br>• Basic authentication | • Minimal configuration<br>• Intuitive interface<br>• Basic error handling<br>• Lightweight implementation |

Example using DuckDuckGoSearch:

!!! mira ""

    {% for pre_made_tool_method, pre_made_tool_method_title in [["basic_usage", "Basic Usage"], ["custom_config", "Custom Config"]] %}
    === "{{ pre_made_tool_method_title }}"

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if pre_made_tool_method == "basic_usage" %}
                ```python hl_lines="2 5"
                {% else %}
                ```python hl_lines="2 4-5 8"
                {% endif %}
                --8<-- "build/snippets/learn/tools/pre_made_tools/{{ pre_made_tool_method }}/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}

        {% endfor %}

    {% endfor %}

### Pre-Made ToolKits

??? api "API Documentation"

    - [`mirascope.tools.system.FileSystemToolKit`](../api/tools/system/file_system.md)
    - [`mirascope.tools.system.DockerOperationToolKit`](../api/tools/system/docker_operation.md)

| ToolKit | Primary Use | Dependencies                                                      | Tools and Features | Characteristics |
|---------|-------------|-------------------------------------------------------------------|-------------------|-----------------|
| [`FileSystemToolKit`](../api/tools/system/file_system.md) | File System Operations | None                                                              | • ReadFile: File content reading<br>• WriteFile: Content writing<br>• ListDirectory: Directory listing<br>• CreateDirectory: Directory creation<br>• DeleteFile: File deletion | • Path traversal protection<br>• File size limits<br>• Extension validation<br>• Robust error handling<br>• Base directory isolation |
| [`DockerOperationToolKit`](../api/tools/system/docker_operation.md) | Code & Command Execution | [`docker`](https://pypi.org/project/docker/), [`docker engine`](https://docs.docker.com/engine/install/) | • ExecutePython: Python code execution with optional package installation<br>• ExecuteShell: Shell command execution | • Docker container isolation<br>• Memory limits<br>• Network control<br>• Security restrictions<br>• Resource cleanup |

Example using FileSystemToolKit:

!!! mira ""


    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="4 10 12"
            {% elif method == "base_message_param" %}
            ```python hl_lines="4 9 17"
            {% else %}
            ```python hl_lines="4 9 16"
            {% endif %}
            --8<-- "build/snippets/learn/tools/pre_made_toolkit/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Next Steps

Tools can significantly extend LLM capabilities, enabling more interactive and dynamic applications. We encourage you to explore and experiment with tools to enhance your projects and the find the best fit for your specific needs.

Mirascope hopes to provide a simple and clean interface that is both easy to learn and easy to use; however, we understand that LLM tools can be a difficult concept regardless of the supporting tooling.

[Join our community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) and ask us any questions you might have, we're here to help!

Next, we recommend learning about how to build [Agents](./agents.md) that take advantage of these tools.
