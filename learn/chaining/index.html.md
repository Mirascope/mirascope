---
search:
  boost: 2
---

# Chaining

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Chaining in Mirascope allows you to combine multiple LLM calls or operations in a sequence to solve complex tasks. This approach is particularly useful for breaking down complex problems into smaller, manageable steps.

Before diving into Mirascope's implementation, let's understand what chaining means in the context of LLM applications:

1. **Problem Decomposition**: Breaking a complex task into smaller, manageable steps.
2. **Sequential Processing**: Executing these steps in a specific order, where the output of one step becomes the input for the next.
3. **Data Flow**: Passing information between steps to build up a final result.

## Basic Usage and Syntax

### Function Chaining

Mirascope is designed to be Pythonic. Since calls are defined as functions, chaining them together is as simple as chaining the function calls as you would normally:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/bedrock/shorthand.py

            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/bedrock/messages.py

            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="6 11 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/bedrock/string_template.py

            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="5 10 19-20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/bedrock/base_message_param.py

            ```

One benefit of this approach is that you can chain your calls together any which way since they are just functions. You can then always wrap these functional chains in a parent function that operates as the single call to the chain.

### Nested Chains

In some cases you'll want to prompt engineer an entire chain rather than just chaining together individual calls. You can do this simply by calling the subchain inside the function body of the parent:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/bedrock/shorthand.py

            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/bedrock/messages.py

            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="6 10 12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/bedrock/string_template.py

            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="5 11 15 20"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/bedrock/base_message_param.py

            ```

We recommend using nested chains for better observability when using tracing tools or applications.

??? tip "Improved tracing through computed fields"

    If you use computed fields in your nested chains, you can always access the computed field in the response. This provides improved tracing for your chains from a single call. 

    !!! mira ""

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/openai/shorthand.py

                ```
            === "Anthropic"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/anthropic/shorthand.py

                ```
            === "Google"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/google/shorthand.py

                ```
            === "Groq"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/groq/shorthand.py

                ```
            === "xAI"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/xai/shorthand.py

                ```
            === "Mistral"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/mistral/shorthand.py

                ```
            === "Cohere"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/cohere/shorthand.py

                ```
            === "LiteLLM"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/litellm/shorthand.py

                ```
            === "Azure AI"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/azure/shorthand.py

                ```
            === "Bedrock"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/bedrock/shorthand.py

                ```
        === "Messages"

            === "OpenAI"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/openai/messages.py

                ```
            === "Anthropic"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/anthropic/messages.py

                ```
            === "Google"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/google/messages.py

                ```
            === "Groq"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/groq/messages.py

                ```
            === "xAI"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/xai/messages.py

                ```
            === "Mistral"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/mistral/messages.py

                ```
            === "Cohere"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/cohere/messages.py

                ```
            === "LiteLLM"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/litellm/messages.py

                ```
            === "Azure AI"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/azure/messages.py

                ```
            === "Bedrock"

                ```python hl_lines="16 23-24"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/bedrock/messages.py

                ```
        === "String Template"

            === "OpenAI"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/openai/string_template.py

                ```
            === "Anthropic"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/anthropic/string_template.py

                ```
            === "Google"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/google/string_template.py

                ```
            === "Groq"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/groq/string_template.py

                ```
            === "xAI"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/xai/string_template.py

                ```
            === "Mistral"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/mistral/string_template.py

                ```
            === "Cohere"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/cohere/string_template.py

                ```
            === "LiteLLM"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/litellm/string_template.py

                ```
            === "Azure AI"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/azure/string_template.py

                ```
            === "Bedrock"

                ```python hl_lines="12 18-19"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/bedrock/string_template.py

                ```
        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/openai/base_message_param.py

                ```
            === "Anthropic"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/anthropic/base_message_param.py

                ```
            === "Google"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/google/base_message_param.py

                ```
            === "Groq"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/groq/base_message_param.py

                ```
            === "xAI"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/xai/base_message_param.py

                ```
            === "Mistral"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/mistral/base_message_param.py

                ```
            === "Cohere"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/cohere/base_message_param.py

                ```
            === "LiteLLM"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/litellm/base_message_param.py

                ```
            === "Azure AI"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/azure/base_message_param.py

                ```
            === "Bedrock"

                ```python hl_lines="19 26-27"
                    # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/computed_fields/bedrock/base_message_param.py

                ```

## Advanced Chaining Techniques

There are many different ways to chain calls together, often resulting in breakdowns and flows that are specific to your task.

Here are a few examples:

!!! mira ""

    === "Conditional"

        ```python
            from enum import Enum

            from mirascope import BaseDynamicConfig, llm, prompt_template


            class Sentiment(str, Enum):
                POSITIVE = "positive"
                NEGATIVE = "negative"


            @llm.call(provider="openai", model="gpt-4o", response_model=Sentiment)
            def sentiment_classifier(review: str) -> str:
                return f"Is the following review positive or negative? {review}"


            @llm.call(provider="openai", model="gpt-4o-mini")
            @prompt_template(
                """
                SYSTEM:
                Your task is to respond to a review.
                The review has been identified as {sentiment}.
                Please write a {conditional_review_prompt}.

                USER: Write a response for the following review: {review}
                """
            )
            def review_responder(review: str) -> BaseDynamicConfig:
                sentiment = sentiment_classifier(review=review)
                conditional_review_prompt = (
                    "thank you response for the review."
                    if sentiment == Sentiment.POSITIVE
                    else "response addressing the review."
                )
                return {
                    "computed_fields": {
                        "conditional_review_prompt": conditional_review_prompt,
                        "sentiment": sentiment,
                    }
                }


            positive_review = "This tool is awesome because it's so flexible!"
            response = review_responder(review=positive_review)
            print(response)
            print(response.dynamic_config)
        ```

    === "Parallel"

        ```python
            import asyncio

            from mirascope import BaseDynamicConfig, llm, prompt_template
            from pydantic import BaseModel


            @llm.call(provider="openai", model="gpt-4o-mini")
            @prompt_template(
                """
                Please identify a chef who is well known for cooking with {ingredient}.
                Respond only with the chef's name.
                """
            )
            async def chef_selector(ingredient: str): ...


            class IngredientsList(BaseModel):
                ingredients: list[str]


            @llm.call(provider="openai", model="gpt-4o-mini", response_model=IngredientsList)
            @prompt_template(
                """
                Given a base ingredient {ingredient}, return a list of complementary ingredients.
                Make sure to exclude the original ingredient from the list.
                """
            )
            async def ingredients_identifier(ingredient: str): ...


            @llm.call(provider="openai", model="gpt-4o-mini")
            @prompt_template(
                """
                SYSTEM:
                Your task is to recommend a recipe. Pretend that you are chef {chef}.

                USER:
                Recommend recipes that use the following ingredients:
                {ingredients}
                """
            )
            async def recipe_recommender(ingredient: str) -> BaseDynamicConfig:
                chef, ingredients = await asyncio.gather(
                    chef_selector(ingredient), ingredients_identifier(ingredient)
                )
                return {"computed_fields": {"chef": chef, "ingredients": ingredients}}


            async def run():
                response = await recipe_recommender(ingredient="apples")
                print(response.content)


            asyncio.run(run())
        ```

    === "Iterative"

        ```python
            from mirascope import llm, prompt_template
            from pydantic import BaseModel, Field


            class SummaryFeedback(BaseModel):
                """Feedback on summary with a critique and review rewrite based on said critique."""

                critique: str = Field(..., description="The critique of the summary.")
                rewritten_summary: str = Field(
                    ...,
                    description="A rewritten summary that takes the critique into account.",
                )


            @llm.call(provider="openai", model="gpt-4o")
            def summarizer(original_text: str) -> str:
                return f"Summarize the following text into one sentence: {original_text}"


            @llm.call(provider="openai", model="gpt-4o", response_model=SummaryFeedback)
            @prompt_template(
                """
                Original Text: {original_text}
                Summary: {summary}

                Critique the summary of the original text.
                Then rewrite the summary based on the critique. It must be one sentence.
                """
            )
            def resummarizer(original_text: str, summary: str): ...


            def rewrite_iteratively(original_text: str, summary: str, depth=2):
                text = original_text
                for _ in range(depth):
                    text = resummarizer(original_text=text, summary=summary).rewritten_summary
                return text


            original_text = """
            In the heart of a dense forest, a boy named Timmy pitched his first tent, fumbling with the poles and pegs.
            His grandfather, a seasoned camper, guided him patiently, their bond strengthening with each knot tied.
            As night fell, they sat by a crackling fire, roasting marshmallows and sharing tales of old adventures.
            Timmy marveled at the star-studded sky, feeling a sense of wonder he'd never known.
            By morning, the forest had transformed him, instilling a love for the wild that would last a lifetime.
            """

            summary = summarizer(original_text=original_text).content
            print(f"Summary: {summary}")
            # > Summary: In the dense forest, Timmy's first tent-pitching experience with his seasoned camper grandfather deepened their bond and ignited a lifelong love for the wild.
            rewritten_summary = rewrite_iteratively(original_text, summary)
            print(f"Rewritten Summary: {rewritten_summary}")
            # > Rewritten Summary: In the dense forest, Timmy's first tent-pitching experience with his seasoned camper grandfather, filled with roasting marshmallows and sharing tales by the fire, deepened their bond, filled him with wonder at the starry sky, and ignited a lifelong love for the wild.
        ```

[Response Models](./response_models.md) are a great way to add more structure to your chains, and [parallel async calls](./async.md#parallel-async-calls) can be particularly powerful for making your chains more efficient.

For inspiration on even more ways you can chain calls together, check out our tutorial section on [chaining-based prompt engineering](../tutorials/prompt_engineering/chaining_based/self_refine.ipynb), which covers many advanced chaining techniques used to apply prompt engineering concepts.

## Next Steps

By mastering Mirascope's chaining techniques, you can create sophisticated LLM-powered applications that tackle complex, multi-step problems with greater accuracy, control, and observability.

Next, we recommend taking a look at the [Response Models](./response_models.md) documentation, which shows you how to generate structured outputs.
