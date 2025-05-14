---
search:
  boost: 2
---

# JSON Mode

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

JSON Mode is a feature in Mirascope that allows you to request structured JSON output from Large Language Models (LLMs). This mode is particularly useful when you need to extract structured information from the model's responses, making it easier to parse and use the data in your applications.

??? warning "Not all providers have an official JSON Mode"

    For providers with explicit support, Mirascope uses the native JSON Mode feature of the API. For providers without explicit support (e.g. Anthropic), Mirascope implements a pseudo JSON Mode by instructing the model in the prompt to output JSON.

    | Provider  | Support Type | Implementation      |
    |-----------|--------------|---------------------|
    | Anthropic | Pseudo       | Prompt engineering  |
    | Azure     | Explicit     | Native API feature  |
    | Bedrock   | Pseudo       | Prompt engineering  |
    | Cohere    | Pseudo       | Prompt engineering  |
    | Google    | Explicit     | Native API feature  |
    | Groq      | Explicit     | Native API feature  |
    | LiteLLM   | Explicit     | Native API feature  |
    | Mistral   | Explicit     | Native API feature  |
    | OpenAI    | Explicit     | Native API feature  |

    If you'd prefer not to have any internal updates made to your prompt, you can always set JSON mode yourself through `call_params` rather than using the `json_mode` argument, which provides provider-agnostic support but is certainly not required to use JSON mode.

## Basic Usage and Syntax

Let's take a look at a basic example using JSON Mode:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="6 8 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="6 7 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="6 10 17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/basic_usage/bedrock/base_message_param.py

            ```


In this example we

1. Enable JSON Mode with `json_mode=True` in the `call` decorator
2. Instruct the model what fields to include in our prompt
3. Load the JSON string response into a Python object and print it

## Error Handling and Validation

While JSON Mode can signifanctly improve the structure of model outputs, it's important to note that it's far from infallible. LLMs often produce invalid JSON or deviate from the expected structure, so it's crucial to implement proper error handling and validation in your code:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="11 14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="15 18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/json_mode/error_handling/bedrock/base_message_param.py

            ```


!!! warning "Beyond JSON Validation"

    While this example catches errors for invalid JSON, there's always a chance that the LLM returns valid JSON that doesn't conform to your expected schema (such as missing fields or incorrect types).

    For more robust validation, we recommend using [Response Models](./response_models.md) for easier structuring and validation of LLM outputs.

## Next Steps

By leveraging JSON Mode, you can create more robust and data-driven applications that efficiently process and utilize LLM outputs. This approach allows for easy integration with databases, APIs, or user interfaces, demonstrating the power of JSON Mode in creating robust, data-driven applications.

Next, we recommend reading the section on [Output Parsers](./output_parsers.md) to see how to engineer prompts with specific output structures and parse the outputs automatically on every call.
