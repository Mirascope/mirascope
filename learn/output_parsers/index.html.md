---
search:
  boost: 2
---

# Output Parsers

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Output Parsers in Mirascope provide a flexible way to process and structure the raw output from Large Language Models (LLMs). They allow you to transform the LLM's response into a more usable format, enabling easier integration with your application logic and improving the overall reliability of your LLM-powered features.

## Basic Usage and Syntax

??? api "API Documentation"

    [`mirascope.core.openai.call.output_parser`](../api/core/openai/call.md?h=output_parser)
    [`mirascope.core.anthropic.call.output_parser`](../api/core/anthropic/call.md?h=output_parser)
    [`mirascope.core.google.call.output_parser`](../api/core/google/call.md?h=output_parser)
    [`mirascope.core.groq.call.output_parser`](../api/core/groq/call.md?h=output_parser)
    [`mirascope.core.xai.call.output_parser`](../api/core/xai/call.md?h=output_parser)
    [`mirascope.core.mistral.call.output_parser`](../api/core/mistral/call.md?h=output_parser)
    [`mirascope.core.cohere.call.output_parser`](../api/core/cohere/call.md?h=output_parser)
    [`mirascope.core.litellm.call.output_parser`](../api/core/litellm/call.md?h=output_parser)
    [`mirascope.core.azure.call.output_parser`](../api/core/azure/call.md?h=output_parser)
    [`mirascope.core.bedrock.call.output_parser`](../api/core/bedrock/call.md?h=output_parser)

Output Parsers are functions that take the call response object as input and return an output of a specified type. When you supply an output parser to a `call` decorator, it modifies the return type of the decorated function to match the output type of the parser.

Let's take a look at a basic example:

!!! mira ""

    === "Shorthand"

        === "OpenAI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/openai/shorthand.py

            ```
        === "Anthropic"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/anthropic/shorthand.py

            ```
        === "Google"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/google/shorthand.py

            ```
        === "Groq"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/groq/shorthand.py

            ```
        === "xAI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/xai/shorthand.py

            ```
        === "Mistral"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/mistral/shorthand.py

            ```
        === "Cohere"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/cohere/shorthand.py

            ```
        === "LiteLLM"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/litellm/shorthand.py

            ```
        === "Azure AI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/azure/shorthand.py

            ```
        === "Bedrock"
 
            ```python hl_lines="10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/openai/messages.py

            ```
        === "Anthropic"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/anthropic/messages.py

            ```
        === "Google"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/google/messages.py

            ```
        === "Groq"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/groq/messages.py

            ```
        === "xAI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/xai/messages.py

            ```
        === "Mistral"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/mistral/messages.py

            ```
        === "Cohere"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/cohere/messages.py

            ```
        === "LiteLLM"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/litellm/messages.py

            ```
        === "Azure AI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/azure/messages.py

            ```
        === "Bedrock"
 
            ```python hl_lines="10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/openai/string_template.py

            ```
        === "Anthropic"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/anthropic/string_template.py

            ```
        === "Google"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/google/string_template.py

            ```
        === "Groq"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/groq/string_template.py

            ```
        === "xAI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/xai/string_template.py

            ```
        === "Mistral"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/mistral/string_template.py

            ```
        === "Cohere"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/cohere/string_template.py

            ```
        === "LiteLLM"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/litellm/string_template.py

            ```
        === "Azure AI"
            ```python hl_lines="9 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/azure/string_template.py

            ```
        === "Bedrock"
 
            ```python hl_lines="10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/openai/base_message_param.py

            ```
        === "Anthropic"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/anthropic/base_message_param.py

            ```
        === "Google"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/google/base_message_param.py

            ```
        === "Groq"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/groq/base_message_param.py

            ```
        === "xAI"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/xai/base_message_param.py

            ```
        === "Mistral"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/mistral/base_message_param.py

            ```
        === "Cohere"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/cohere/base_message_param.py

            ```
        === "LiteLLM"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/litellm/base_message_param.py

            ```
        === "Azure AI"
            ```python hl_lines="9 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/azure/base_message_param.py

            ```
        === "Bedrock"
            ```python hl_lines="10 22"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/basic_usage/bedrock/base_message_param.py

            ```


## Additional Examples

There are many different ways to structure and parse LLM outputs, ranging from XML parsing to using regular expressions.

Here are a few examples:

!!! mira ""

    === "Regular Expression"

        === "OpenAI"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/openai/regex.py

            ```

        === "Anthropic"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/anthropic/regex.py

            ```

        === "Google"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/google/regex.py

            ```

        === "Groq"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/groq/regex.py

            ```

        === "xAI"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/xai/regex.py

            ```

        === "Mistral"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/mistral/regex.py

            ```

        === "Cohere"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/cohere/regex.py

            ```

        === "LiteLLM"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/litellm/regex.py

            ```

        === "Azure AI"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/azure/regex.py

            ```

        === "Bedrock"

            ```python hl_lines="7 14 17 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/bedrock/regex.py

            ```



    === "XML"

        === "OpenAI"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/openai/xml.py

            ```

        === "Anthropic"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/anthropic/xml.py

            ```

        === "Google"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/google/xml.py

            ```

        === "Groq"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/groq/xml.py

            ```

        === "xAI"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/xai/xml.py

            ```

        === "Mistral"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/mistral/xml.py

            ```

        === "Cohere"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/cohere/xml.py

            ```

        === "LiteLLM"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/litellm/xml.py

            ```

        === "Azure AI"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/azure/xml.py

            ```

        === "Bedrock"

            ```python hl_lines="14-28 31 35-40"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/bedrock/xml.py

            ```


    === "JSON Mode"

        === "OpenAI"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/openai/json_mode.py

            ```

        === "Anthropic"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/anthropic/json_mode.py

            ```

        === "Google"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/google/json_mode.py

            ```

        === "Groq"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/groq/json_mode.py

            ```

        === "xAI"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/xai/json_mode.py

            ```

        === "Mistral"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/mistral/json_mode.py

            ```

        === "Cohere"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/cohere/json_mode.py

            ```

        === "LiteLLM"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/litellm/json_mode.py

            ```

        === "Azure AI"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/azure/json_mode.py

            ```

        === "Bedrock"

            ```python hl_lines="7-9 12-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/output_parsers/additional_examples/bedrock/json_mode.py

            ```


## Next Steps

By leveraging Output Parsers effectively, you can create more robust and reliable LLM-powered applications, ensuring that the raw model outputs are transformed into structured data that's easy to work with in your application logic.

Next, we recommend taking a look at the section on [Tools](./tools.md) to learn how to extend the capabilities of LLMs with custom functions.
