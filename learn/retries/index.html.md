---
search:
  boost: 2
---

# Retries

Making an API call to a provider can fail due to various reasons, such as rate limits, internal server errors, validation errors, and more. This makes retrying calls extremely important when building robust systems.

Mirascope combined with [Tenacity](https://tenacity.readthedocs.io/en/latest/) increases the chance for these requests to succeed while maintaining end user transparency.

You can install the necessary packages directly or use the `tenacity` extras flag:

```python
pip install "mirascope[tenacity]"
```

## Tenacity `retry` Decorator

### Calls

Let's take a look at a basic Mirascope call that retries with exponential back-off:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/calls/bedrock/base_message_param.py

            ```


Ideally the call to `recommend_book` will succeed on the first attempt, but now the API call will be made again after waiting should it fail.

The call will then throw a `RetryError` after 3 attempts if unsuccessful. This error should be caught and handled.

### Streams

When streaming, the generator is not actually run until you start iterating. This means the initial API call may be successful but fail during the actual iteration through the stream.

Instead, you need to wrap your call and add retries to this wrapper:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/streams/bedrock/base_message_param.py

            ```


### Tools

When using tools, `ValidationError` errors won't happen until you attempt to construct the tool (either when calling `response.tools` or iterating through a stream with tools).

You need to handle retries in this case the same way as streams:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/tools/bedrock/base_message_param.py

            ```


### Error Reinsertion

Every example above simply retries after a failed attempt without making any updates to the call. This approach can be sufficient for some use-cases where we can safely expect the call to succeed on subsequent attempts (e.g. rate limits).

However, there are some cases where the LLM is likely to make the same mistake over and over again. For example, when using tools or response models, the LLM may return incorrect or missing arguments where it's highly likely the LLM will continuously make the same mistake on subsequent calls. In these cases, it's important that we update subsequent calls based on resulting errors to improve the chance of success on the next call.

To make it easier to make such updates, Mirascope provides a `collect_errors` handler that can collect any errors of your choice and insert them into subsequent calls through an `errors` keyword argument.

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="4 14 20 34"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="4 14 28 43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="4 14 21 38" 
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/retries/error_reinsertion/bedrock/base_message_param.py

            ```


In this example the first attempt fails because the identified author is not all uppercase. The `ValidationError` is then reinserted into the subsequent call, which enables the model to learn from it's mistake and correct its error.

Of course, we could always engineer a better prompt (i.e. ask for all caps), but even prompt engineering does not guarantee perfect results. The purpose of this example is to demonstrate the power of a feedback loop by reinserting errors to build more robust systems.

## Fallback

When using the provider-agnostic `llm.call` decorator, you can use the `fallback` decorator to automatically catch certain errors and use a backup provider/model to attempt the call again.

For example, we may want to attempt the call with Anthropic in the event that we get a `RateLimitError` from OpenAI:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="7-16 24 28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import llm
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError


            @fallback(
                OpenAIRateLimitError,
                [
                    {
                        "catch": AnthropicRateLimitError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @llm.call("openai", "gpt-4o-mini")
            def answer_question(question: str) -> str:
                return f"Answer this question: {question}"


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```

    === "Messages"

        ```python hl_lines="7-16 24 28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import Messages, llm
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError


            @fallback(
                OpenAIRateLimitError,
                [
                    {
                        "catch": AnthropicRateLimitError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @llm.call("openai", "gpt-4o-mini")
            def answer_question(question: str) -> Messages.Type:
                return Messages.User(f"Answer this question: {question}")


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```

    === "String Template"

        ```python hl_lines="7-16 24 28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import llm, prompt_template
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError


            @fallback(
                OpenAIRateLimitError,
                [
                    {
                        "catch": AnthropicRateLimitError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @llm.call("openai", "gpt-4o-mini")
            @prompt_template("Answer this question: {question}")
            def answer_question(question: str): ...


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```

    === "BaseMessageParam"

        ```python hl_lines="7-16 24 28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import BaseMessageParam, llm
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError


            @fallback(
                OpenAIRateLimitError,
                [
                    {
                        "catch": AnthropicRateLimitError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @llm.call("openai", "gpt-4o-mini")
            def answer_question(question: str) -> list[BaseMessageParam]:
                return [BaseMessageParam(role="user", content=f"Answer this question: {question}")]


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```


Here, we first attempt to call OpenAI (the default setting). If we catch the `OpenAIRateLimitError`, then we'll attempt to call Anthropic. If we catch the `AnthropicRateLimitError`, then we'll receive a `FallbackError` since all attempts failed.

You can provide an `Exception` or tuple of multiple to catch, and you can stack the `fallback` decorator to handle different errors differently if desired.

### Fallback With Retries

The decorator also works well with Tenacity's `retry` decorator. For example, we may want to first attempt to call OpenAI multiple times with exponential backoff, but if we fail 3 times fall back to Anthropic, which we'll also attempt to call 3 times:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="14-28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import llm
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError
            from tenacity import (
                RetryError,
                retry,
                retry_if_exception_type,
                stop_after_attempt,
                wait_exponential,
            )


            @fallback(
                RetryError,
                [
                    {
                        "catch": RetryError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @retry(
                retry=retry_if_exception_type((OpenAIRateLimitError, AnthropicRateLimitError)),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=4, max=10),
            )
            @llm.call("openai", "gpt-4o-mini")
            def answer_question(question: str) -> str:
                return f"Answer this question: {question}"


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```

    === "Messages"

        ```python hl_lines="14-28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import Messages, llm
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError
            from tenacity import (
                RetryError,
                retry,
                retry_if_exception_type,
                stop_after_attempt,
                wait_exponential,
            )


            @fallback(
                RetryError,
                [
                    {
                        "catch": RetryError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @retry(
                retry=retry_if_exception_type((OpenAIRateLimitError, AnthropicRateLimitError)),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=4, max=10),
            )
            @llm.call("openai", "gpt-4o-mini")
            def answer_question(question: str) -> Messages.Type:
                return Messages.User(f"Answer this question: {question}")


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```

    === "String Template"

        ```python hl_lines="14-28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import llm, prompt_template
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError
            from tenacity import (
                RetryError,
                retry,
                retry_if_exception_type,
                stop_after_attempt,
                wait_exponential,
            )


            @fallback(
                RetryError,
                [
                    {
                        "catch": RetryError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @retry(
                retry=retry_if_exception_type((OpenAIRateLimitError, AnthropicRateLimitError)),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=4, max=10),
            )
            @llm.call("openai", "gpt-4o-mini")
            @prompt_template("Answer this question: {question}")
            def answer_question(question: str): ...


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```

    === "BaseMessageParam"

        ```python hl_lines="14-28"
            from anthropic import RateLimitError as AnthropicRateLimitError
            from mirascope import BaseMessageParam, llm
            from mirascope.retries import FallbackError, fallback
            from openai import RateLimitError as OpenAIRateLimitError
            from tenacity import (
                RetryError,
                retry,
                retry_if_exception_type,
                stop_after_attempt,
                wait_exponential,
            )


            @fallback(
                RetryError,
                [
                    {
                        "catch": RetryError,
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-latest",
                    }
                ],
            )
            @retry(
                retry=retry_if_exception_type((OpenAIRateLimitError, AnthropicRateLimitError)),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=4, max=10),
            )
            @llm.call("openai", "gpt-4o-mini")
            def answer_question(question: str) -> list[BaseMessageParam]:
                return [BaseMessageParam(role="user", content=f"Answer this question: {question}")]


            try:
                response = answer_question("What is the meaning of life?")
                if caught := getattr(response, "_caught", None):
                    print(f"Exception caught: {caught}")
                print("### Response ###")
                print(response.content)
            except FallbackError as e:
                print(e)
        ```

