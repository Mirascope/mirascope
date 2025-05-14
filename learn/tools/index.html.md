---
search:
  boost: 2 
---

# Tools


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
    [`mirascope.core.openai.tool`](../api/core/openai/tool.md)
    [`mirascope.core.anthropic.tool`](../api/core/anthropic/tool.md)
    [`mirascope.core.google.tool`](../api/core/google/tool.md)
    [`mirascope.core.groq.tool`](../api/core/groq/tool.md)
    [`mirascope.core.xai.tool`](../api/core/xai/tool.md)
    [`mirascope.core.mistral.tool`](../api/core/mistral/tool.md)
    [`mirascope.core.cohere.tool`](../api/core/cohere/tool.md)
    [`mirascope.core.litellm.tool`](../api/core/openai/tool.md)
    [`mirascope.core.azure.tool`](../api/core/azure/tool.md)
    [`mirascope.core.bedrock.tool`](../api/core/bedrock/tool.md)

There are two ways of defining tools in Mirascope: [`BaseTool`](../api/core/base/tool.md) and functions.

You can consider the functional definitions a shorthand form of writing the `BaseTool` version of the same tool. Under the hood, tools defined as functions will get converted automatically into their corresponding `BaseTool`.

Let's take a look at a basic example of each using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="5-16 19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/base_message_param.py

                ```


    === "Function"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="4-15 18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/base_message_param.py

                ```



??? note "Official SDK"

    === "OpenAI"

        ```python hl_lines="8-14 21-34 36-38"
            import json

            from openai import OpenAI

            client = OpenAI()


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Who wrote {book}"}],
                    tools=[
                        {
                            "function": {
                                "name": "get_book_author",
                                "description": "Returns the author of the book with the given title.",
                                "parameters": {
                                    "properties": {"title": {"type": "string"}},
                                    "required": ["title"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    if tool_calls[0].function.name == "get_book_author":
                        return get_book_author(**json.loads(tool_calls[0].function.arguments))
                return str(completion.choices[0].message.content)


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "Anthropic"

        ```python hl_lines="6-12 20-30 33-36"
            from anthropic import Anthropic

            client = Anthropic()


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                message = client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": f"Who wrote {book}?"}],
                    tools=[
                        {
                            "name": "get_book_author",
                            "description": "Returns the author of the book with the given title.",
                            "input_schema": {
                                "properties": {"title": {"type": "string"}},
                                "required": ["title"],
                                "type": "object",
                            },
                        }
                    ],
                )
                content = ""
                for block in message.content:
                    if block.type == "tool_use":
                        if block.name == "get_book_author":
                            return get_book_author(**block.input)  # pyright: ignore [reportCallIssue]
                    else:
                        content += block.text
                return content


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "Google"

        ```python hl_lines="7-13 21-37 30-46"
            from google.genai import Client
            from google.genai.types import FunctionDeclaration, GenerateContentConfig, Tool

            client = Client()


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents={"parts": [{"text": f"Who wrote {book}?"}]},
                    config=GenerateContentConfig(
                        tools=[
                            Tool(
                                function_declarations=[
                                    FunctionDeclaration(
                                        **{
                                            "name": "get_book_author",
                                            "description": "Returns the author of the book with the given title.",
                                            "parameters": {
                                                "properties": {"title": {"type": "string"}},
                                                "required": ["title"],
                                                "type": "object",
                                            },
                                        }
                                    )
                                ]
                            )
                        ]
                    ),
                )
                if tool_calls := [
                    function_call
                    for function_call in (response.function_calls or [])
                    if function_call.args
                ]:
                    if tool_calls[0].name == "get_book_author":
                        return get_book_author(**dict((tool_calls[0].args or {}).items()))  # pyright: ignore [reportArgumentType]
                return response.text or ""


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "Groq"

        ```python hl_lines="8-14 21-34 36-38"
            import json

            from groq import Groq

            client = Groq()


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Who wrote {book}?"}],
                    tools=[
                        {
                            "function": {
                                "name": "get_book_author",
                                "description": "Returns the author of the book with the given title.",
                                "parameters": {
                                    "properties": {"title": {"type": "string"}},
                                    "required": ["title"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    if tool_calls[0].function.name == "get_book_author":
                        return get_book_author(**json.loads(tool_calls[0].function.arguments))
                return str(completion.choices[0].message.content)


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "xAI"

        ```python hl_lines="8-14 21-34 36-38"
            import json

            from openai import OpenAI

            client = OpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY")


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Who wrote {book}"}],
                    tools=[
                        {
                            "function": {
                                "name": "get_book_author",
                                "description": "Returns the author of the book with the given title.",
                                "parameters": {
                                    "properties": {"title": {"type": "string"}},
                                    "required": ["title"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    if tool_calls[0].function.name == "get_book_author":
                        return get_book_author(**json.loads(tool_calls[0].function.arguments))
                return str(completion.choices[0].message.content)


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "Mistral"

        ```python hl_lines="10-16 23-36 38-44"
            import json
            import os
            from typing import cast

            from mistralai import Mistral

            client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str | None:
                completion = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": f"Who wrote {book}?"}],
                    tools=[
                        {
                            "function": {
                                "name": "get_book_author",
                                "description": "Returns the author of the book with the given title.",
                                "parameters": {
                                    "properties": {"title": {"type": "string"}},
                                    "required": ["title"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                )
                if not completion or not completion.choices:
                    return None
                if tool_calls := completion.choices[0].message.tool_calls:
                    if tool_calls[0].function.name == "get_book_author":
                        return get_book_author(
                            **json.loads(cast(str, tool_calls[0].function.arguments))
                        )
                return cast(str, completion.choices[0].message.content)


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "Cohere"

        ```python hl_lines="9-15 22-32 34-36"
            from typing import cast

            from cohere import Client
            from cohere.types import Tool, ToolParameterDefinitionsValue

            client = Client()


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                response = client.chat(
                    model="command-r-plus",
                    message=f"Who wrote {book}?",
                    tools=[
                        Tool(
                            name="get_book_author",
                            description="Returns the author of the book with the given title.",
                            parameter_definitions={
                                "title": ToolParameterDefinitionsValue(
                                    description=None, type="string", required=True
                                )
                            },
                        )
                    ],
                )
                if tool_calls := response.tool_calls:
                    if tool_calls[0].name == "get_book_author":
                        return get_book_author(**(cast(dict[str, str], tool_calls[0].parameters)))
                return response.text


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "LiteLLM"

        ```python hl_lines="6-12 19-32 34-36"
            import json

            from litellm import completion


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                response = completion(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Who wrote {book}"}],
                    tools=[
                        {
                            "function": {
                                "name": "get_book_author",
                                "description": "Returns the author of the book with the given title.",
                                "parameters": {
                                    "properties": {"title": {"type": "string"}},
                                    "required": ["title"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                )
                if tool_calls := response.choices[0].message.tool_calls:  # pyright: ignore [reportAttributeAccessIssue]
                    if tool_calls[0].function.name == "get_book_author":
                        return get_book_author(**json.loads(tool_calls[0].function.arguments))
                return str(response.choices[0].message.content)  # pyright: ignore [reportAttributeAccessIssue]


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "Azure AI"

        ```python hl_lines="16-22 31-43 45-47"
            import json

            from azure.ai.inference import ChatCompletionsClient
            from azure.ai.inference.models import (
                ChatCompletionsToolDefinition,
                ChatRequestMessage,
                FunctionDefinition,
            )
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(
                endpoint="YOUR_ENDPOINT", credential=AzureKeyCredential("YOUR_KEY")
            )


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                completion = client.complete(
                    model="gpt-4o-mini",
                    messages=[
                        ChatRequestMessage({"role": "user", "content": f"Who wrote {book}?"})
                    ],
                    tools=[
                        ChatCompletionsToolDefinition(
                            function=FunctionDefinition(
                                name="get_book_author",
                                description="Returns the author of the book with the given title.",
                                parameters={
                                    "properties": {"title": {"type": "string"}},
                                    "required": ["title"],
                                    "type": "object",
                                },
                            )
                        )
                    ],
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    if tool_calls[0].function.name == "get_book_author":
                        return get_book_author(**json.loads(tool_calls[0].function.arguments))
                return str(completion.choices[0].message.content)


            author = identify_author("The Name of the Wind")
            print(author)
        ```

    === "Bedrock"

        ```python hl_lines="6-12 18-37 49-55"
            import boto3

            bedrock_client = boto3.client(service_name="bedrock-runtime")


            def get_book_author(title: str) -> str:
                if title == "The Name of the Wind":
                    return "Patrick Rothfuss"
                elif title == "Mistborn: The Final Empire":
                    return "Brandon Sanderson"
                else:
                    return "Unknown"


            def identify_author(book: str) -> str:
                messages = [{"role": "user", "content": [{"text": f"Who wrote {book}?"}]}]
                tool_config = {
                    "tools": [
                        {
                            "toolSpec": {
                                "name": "get_book_author",
                                "description": "Returns the author of the book with the given title.",
                                "inputSchema": {
                                    "json": {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                                "type": "string",
                                                "description": "The title of the book.",
                                            }
                                        },
                                        "required": ["title"],
                                    }
                                },
                            }
                        }
                    ]
                }
                response = bedrock_client.converse(
                    modelId="amazon.nova-lite-v1:0",
                    messages=messages,
                    toolConfig=tool_config,
                )
                content = ""
                output_message = response["output"]["message"]
                messages.append(output_message)
                stop_reason = response["stopReason"]

                if stop_reason == "tool_use":
                    tool_requests = output_message["content"]
                    for tool_request in tool_requests:
                        if "toolUse" in tool_request:
                            tool = tool_request["toolUse"]
                            if tool["name"] == "get_book_author":
                                return get_book_author(**tool["input"])
                for content_piece in output_message["content"]:
                    if "text" in content_piece:
                        content += content_piece["text"]
                return content


            author = identify_author("The Name of the Wind")
            print(author)
        ```


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

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/base_tool/bedrock/base_message_param.py

                ```

        
    === "Function"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/shorthand.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/messages.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/string_template.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/base_message_param.py

                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/basic_usage/function/bedrock/base_message_param.py

                ```

        

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

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="24-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/base_tool/bedrock/base_message_param.py

                ```


    === "Function"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="23-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/parallel/function/bedrock/base_message_param.py

                ```



If your tool calls are I/O-bound, it's often worth writing [async tools](./async.md#async-tools) so that you can run all of the tools calls [in parallel](./async.md#parallel-async-calls) for better efficiency.

## Streaming Tools

Mirascope supports streaming responses with tools, which is useful for long-running tasks or real-time updates:

!!! mira ""

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/anthropic/shorthand.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/groq/shorthand.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/mistral/shorthand.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/azure/shorthand.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/anthropic/messages.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/groq/messages.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/mistral/messages.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/cohere/messages.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/litellm/messages.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/azure/messages.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/anthropic/string_template.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/groq/string_template.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/mistral/string_template.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/litellm/string_template.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/azure/string_template.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/anthropic/base_message_param.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/groq/base_message_param.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="19 25-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/base_tool/bedrock/base_message_param.py

                ```


    === "Function"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/anthropic/shorthand.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/groq/shorthand.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/mistral/shorthand.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/azure/shorthand.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/anthropic/messages.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/groq/messages.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/mistral/messages.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/cohere/messages.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/litellm/messages.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/azure/messages.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/anthropic/string_template.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/groq/string_template.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/mistral/string_template.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/litellm/string_template.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/azure/string_template.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/anthropic/base_message_param.py

                ```
            === "Google"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/groq/base_message_param.py

                ```
            === "xAI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="18 24-26"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/streams/function/bedrock/base_message_param.py

                ```



!!! note "When are tools returned?"

    When we identify that a tool is being streamed, we will internally reconstruct the tool from the streamed response. This means that the tool won't be returned until the full tool has been streamed and reconstructed on your behalf.

!!! warning "Not all providers support streaming tools"

    Currently only OpenAI, Anthropic, Mistral, and Groq support streaming tools. All other providers will always return `None` for tools.
    
    If you think we're missing any, let us know!

### Streaming Partial Tools

You can also stream intermediate partial tools and their deltas (rather than just the fully constructed tool) by setting `stream={"partial_tools": True}`:

!!! mira ""

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/anthropic/shorthand.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/groq/shorthand.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/mistral/shorthand.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/azure/shorthand.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/anthropic/messages.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/groq/messages.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/mistral/messages.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/cohere/messages.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/litellm/messages.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/azure/messages.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/anthropic/string_template.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/groq/string_template.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/mistral/string_template.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/litellm/string_template.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/azure/string_template.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/anthropic/base_message_param.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/groq/base_message_param.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="23 31"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/base_tool/bedrock/base_message_param.py

                ```


    === "Function"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/anthropic/shorthand.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/groq/shorthand.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/mistral/shorthand.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/azure/shorthand.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/anthropic/messages.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/groq/messages.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/mistral/messages.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/cohere/messages.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/litellm/messages.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/azure/messages.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/anthropic/string_template.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/groq/string_template.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/mistral/string_template.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/litellm/string_template.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/azure/string_template.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/anthropic/base_message_param.py

                ```
            === "Google"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/groq/base_message_param.py

                ```
            === "xAI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="22 30"
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python
               
                     # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/partial_tool_streams/function/bedrock/base_message_param.py

                ```



## Tool Message Parameters

!!! mira ""

    <div align="center">
        Calling tools and inserting their outputs into subsequent LLM API calls in a loop in the most basic form of an agent. While we cover this briefly here, we recommend reading the section on [Agents](./agents.md) for more details and examples.
    </div>

Generally the next step after the LLM returns a tool call is for you to call the tool on its behalf and supply the output in a subsequent call.

Let's take a look at a basic example of this:

!!! mira ""

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="19 24 33-35 38"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="18 20 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/base_tool/bedrock/base_message_param.py

                ```


    === "Function"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="16 21 30-32 35"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="15 17 27-29 32"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/tool_message_params/function/bedrock/base_message_param.py

                ```



In this example we:

1. Add `history` to maintain the messages across multiple calls to the LLM.
2. Loop until the response no longer has tools calls.
3. While there are tool calls, call the tools, append their corresponding message parameters to the history, and make a subsequent call with an empty query and updated history. We use an empty query because the original user message is already included in the history.
4. Print the final response content once the LLM is done calling tools.

## Validation and Error Handling

Since `BaseTool` is a subclass of Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), they are validated on construction, so it's important that you handle potential `ValidationError`'s for building more robust applications:

!!! mira ""

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="15 34 39"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/base_tool/bedrock/base_message_param.py

                ```


    === "Function"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="12 32 37"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/validation/function/bedrock/base_message_param.py

                ```



In this example we've added additional validation, but it's important that you still handle `ValidationError`'s even with standard tools since they are still `BaseModel` instances and will validate the field types regardless.

## Few-Shot Examples

Just like with [Response Models](./response_models.md#few-shot-examples), you can add few-shot examples to your tools:

!!! mira ""

    === "BaseTool"

        === "Shorthand"

            === "OpenAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/openai/shorthand.py

                ```
            === "Anthropic"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/anthropic/shorthand.py

                ```
            === "Google"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/google/shorthand.py

                ```
            === "Groq"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/groq/shorthand.py

                ```
            === "xAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/xai/shorthand.py

                ```
            === "Mistral"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/mistral/shorthand.py

                ```
            === "Cohere"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/cohere/shorthand.py

                ```
            === "LiteLLM"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/litellm/shorthand.py

                ```
            === "Azure AI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/azure/shorthand.py

                ```
            === "Bedrock"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/openai/messages.py

                ```
            === "Anthropic"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/anthropic/messages.py

                ```
            === "Google"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/google/messages.py

                ```
            === "Groq"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/groq/messages.py

                ```
            === "xAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/xai/messages.py

                ```
            === "Mistral"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/mistral/messages.py

                ```
            === "Cohere"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/cohere/messages.py

                ```
            === "LiteLLM"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/litellm/messages.py

                ```
            === "Azure AI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/azure/messages.py

                ```
            === "Bedrock"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/openai/string_template.py

                ```
            === "Anthropic"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/anthropic/string_template.py

                ```
            === "Google"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/google/string_template.py

                ```
            === "Groq"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/groq/string_template.py

                ```
            === "xAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/xai/string_template.py

                ```
            === "Mistral"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/mistral/string_template.py

                ```
            === "Cohere"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/cohere/string_template.py

                ```
            === "LiteLLM"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/litellm/string_template.py

                ```
            === "Azure AI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/azure/string_template.py

                ```
            === "Bedrock"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/openai/base_message_param.py

                ```
            === "Anthropic"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/anthropic/base_message_param.py

                ```
            === "Google"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/google/base_message_param.py

                ```
            === "Groq"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/groq/base_message_param.py

                ```
            === "xAI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/xai/base_message_param.py

                ```
            === "Mistral"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/mistral/base_message_param.py

                ```
            === "Cohere"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/cohere/base_message_param.py

                ```
            === "LiteLLM"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/litellm/base_message_param.py

                ```
            === "Azure AI"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/azure/base_message_param.py

                ```
            === "Bedrock"
                ```python hl_lines="11 15"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/base_tool/bedrock/base_message_param.py

                ```


    === "Function"

        === "Shorthand"

            === "OpenAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/openai/shorthand.py

                ```
            === "Anthropic"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/anthropic/shorthand.py

                ```
            === "Google"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/google/shorthand.py

                ```
            === "Groq"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/groq/shorthand.py

                ```
            === "xAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/xai/shorthand.py

                ```
            === "Mistral"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/mistral/shorthand.py

                ```
            === "Cohere"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/cohere/shorthand.py

                ```
            === "LiteLLM"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/litellm/shorthand.py

                ```
            === "Azure AI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/azure/shorthand.py

                ```
            === "Bedrock"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/openai/messages.py

                ```
            === "Anthropic"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/anthropic/messages.py

                ```
            === "Google"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/google/messages.py

                ```
            === "Groq"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/groq/messages.py

                ```
            === "xAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/xai/messages.py

                ```
            === "Mistral"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/mistral/messages.py

                ```
            === "Cohere"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/cohere/messages.py

                ```
            === "LiteLLM"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/litellm/messages.py

                ```
            === "Azure AI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/azure/messages.py

                ```
            === "Bedrock"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/openai/string_template.py

                ```
            === "Anthropic"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/anthropic/string_template.py

                ```
            === "Google"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/google/string_template.py

                ```
            === "Groq"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/groq/string_template.py

                ```
            === "xAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/xai/string_template.py

                ```
            === "Mistral"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/mistral/string_template.py

                ```
            === "Cohere"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/cohere/string_template.py

                ```
            === "LiteLLM"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/litellm/string_template.py

                ```
            === "Azure AI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/azure/string_template.py

                ```
            === "Bedrock"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/openai/base_message_param.py

                ```
            === "Anthropic"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/anthropic/base_message_param.py

                ```
            === "Google"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/google/base_message_param.py

                ```
            === "Groq"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/groq/base_message_param.py

                ```
            === "xAI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/xai/base_message_param.py

                ```
            === "Mistral"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/mistral/base_message_param.py

                ```
            === "Cohere"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/cohere/base_message_param.py

                ```
            === "LiteLLM"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/litellm/base_message_param.py

                ```
            === "Azure AI"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/azure/base_message_param.py

                ```
            === "Bedrock"
                ```python hl_lines="14 20-21"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/few_shot_examples/function/bedrock/base_message_param.py

                ```



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

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="10 11 13 15 19 28 29 32 35 37 40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="10 11 13 15 19 27 29 34 37 39 42"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/toolkit/bedrock/base_message_param.py

            ```


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

    === "Basic Usage"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="2 5"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/basic_usage/bedrock/base_message_param.py

                ```


    === "Custom Config"

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/bedrock/shorthand.py

                ```

        === "Messages"

            === "OpenAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/bedrock/messages.py

                ```

        === "String Template"

            === "OpenAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/bedrock/string_template.py

                ```

        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="2 4-5 8"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_tools/custom_config/bedrock/base_message_param.py

                ```



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


    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="4 9 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="4 10 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="4 9 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/tools/pre_made_toolkit/bedrock/base_message_param.py

            ```


## Next Steps

Tools can significantly extend LLM capabilities, enabling more interactive and dynamic applications. We encourage you to explore and experiment with tools to enhance your projects and the find the best fit for your specific needs.

Mirascope hopes to provide a simple and clean interface that is both easy to learn and easy to use; however, we understand that LLM tools can be a difficult concept regardless of the supporting tooling.

[Join our community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) and ask us any questions you might have, we're here to help!

Next, we recommend learning about how to build [Agents](./agents.md) that take advantage of these tools.
