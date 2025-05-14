---
search:
  boost: 3
---

# Calls

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on writing [Prompts](./prompts.md)
    </div>

When working with Large Language Model (LLM) APIs in Mirascope, a "call" refers to making a request to a LLM provider's API with a particular setting and prompt.

The `call` decorator is a core feature of the Mirascope library, designed to simplify and streamline interactions with various LLM providers. This powerful tool allows you to transform prompt templates written as Python functions into LLM API calls with minimal boilerplate code while providing type safety and consistency across different providers.

We currently support [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Google (Gemini/Vertex)](https://ai.google.dev/), [Groq](https://groq.com/), [xAI](https://x.ai/api), [Mistral](https://mistral.ai/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Amazon Bedrock](https://aws.amazon.com/bedrock/).

If there are any providers we don't yet support that you'd like to see supported, let us know!

??? api "API Documentation"

    [`mirascope.llm.call`](../api/llm/call.md)

## Basic Usage and Syntax

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="4 5"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="4 6"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/basic_usage/bedrock/base_message_param.py

            ```


??? note "Official SDK"

    === "OpenAI"

        ```python hl_lines="7-11"
            from openai import OpenAI

            client = OpenAI()


            def recommend_book(genre: str) -> str:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                )
                return str(completion.choices[0].message.content)


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Anthropic"

        ```python hl_lines="7-13"
            from anthropic import Anthropic

            client = Anthropic()


            def recommend_book(genre: str) -> str:
                message = client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                    max_tokens=1024,
                )
                block = message.content[0]
                return block.text if block.type == "text" else ""


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Google"

        ```python hl_lines="7-11"
            from google.genai import Client

            client = Client()


            def recommend_book(genre: str) -> str:
                generation = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents={"role": "user", "parts": [{"text": f"Recommend a {genre} book"}]},  # pyright: ignore [reportArgumentType]
                )
                return generation.candidates[0].content.parts[0].text  # pyright: ignore [reportOptionalSubscript, reportOptionalMemberAccess, reportReturnType]


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Groq"

        ```python hl_lines="7-11"
            from groq import Groq

            client = Groq()


            def recommend_book(genre: str) -> str:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                )
                return str(completion.choices[0].message.content)


            output = recommend_book("fantasy")
            print(output)
        ```

    === "xAI"

        ```python hl_lines="7-11"
            from openai import OpenAI

            client = OpenAI(base_url="https://api.x.ai/v1", api_key="YOUR_KEY_HERE")


            def recommend_book(genre: str) -> str:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                )
                return str(completion.choices[0].message.content)


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Mistral"

        ```python hl_lines="10-15"
            import os
            from typing import cast

            from mistralai import Mistral

            client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


            def recommend_book(genre: str) -> str | None:
                completion = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                )
                if completion and (choices := completion.choices):
                    return cast(str, choices[0].message.content)


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Cohere"

        ```python hl_lines="7-11"
            from cohere import Client

            client = Client()


            def recommend_book(genre: str) -> str:
                response = client.chat(
                    model="command-r-plus",
                    message=f"Recommend a {genre} book",
                )
                return response.text


            output = recommend_book("fantasy")
            print(output)
        ```

    === "LiteLLM"

        ```python hl_lines="5-9"
            from litellm import completion


            def recommend_book(genre: str) -> str:
                response = completion(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                )
                return str(response.choices[0].message.content)  # type: ignore


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Azure AI"

        ```python hl_lines="11-18"
            from azure.ai.inference import ChatCompletionsClient
            from azure.ai.inference.models import ChatRequestMessage
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(
                endpoint="YOUR_ENDPOINT", credential=AzureKeyCredential("YOUR_KEY")
            )


            def recommend_book(genre: str) -> str:
                completion = client.complete(
                    model="gpt-4o-mini",
                    messages=[
                        ChatRequestMessage({"role": "user", "content": f"Recommend a {genre} book"})
                    ],
                )
                message = completion.choices[0].message
                return message.content if message.content is not None else ""


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Bedrock"

        ```python hl_lines="7-18"
            import boto3

            bedrock_client = boto3.client(service_name="bedrock-runtime")


            def recommend_book(genre: str) -> str:
                messages = [{"role": "user", "content": [{"text": f"Recommend a {genre} book"}]}]
                response = bedrock_client.converse(
                    modelId="amazon.nova-lite-v1:0",
                    messages=messages,
                    inferenceConfig={"maxTokens": 1024},
                )
                output_message = response["output"]["message"]
                content = ""
                for content_piece in output_message["content"]:
                    if "text" in content_piece:
                        content += content_piece["text"]
                return content


            output = recommend_book("fantasy")
            print(output)
        ```


Notice how Mirascope makes calls more readable by reducing boilerplate and standardizing interactions with LLM providers.

The `llm.call` decorator accepts `provider` and `model` arguments and returns a provider-agnostic `CallResponse` instance that provides a consistent interface regardless of the underlying provider. You can find more information on `CallResponse` in the [section below](#handling-responses) on handling responses.

Note the `@prompt_template` decorator is optional unless you're using string templates.

### Runtime Provider Overrides

You can override provider settings at runtime using `llm.override`. This takes a function decorated with `llm.call` and lets you specify:

- `provider`: Change the provider being called 
- `model`: Use a different model
- `call_params`: Override call parameters like temperature
- `client`: Use a different client instance

When overriding with a specific `provider`, you must specify the `model` parameter.

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/openai/shorthand.py

            ```

        === "Anthropic"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/anthropic/shorthand.py

            ```

        === "Google"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/google/shorthand.py

            ```

        === "Groq"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/groq/shorthand.py

            ```

        === "xAI"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/xai/shorthand.py

            ```

        === "Mistral"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/mistral/shorthand.py

            ```

        === "Cohere"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/cohere/shorthand.py

            ```

        === "LiteLLM"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/litellm/shorthand.py

            ```

        === "Azure AI"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/azure/shorthand.py

            ```

        === "Bedrock"

            ```python hl_lines="4-6 12-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/bedrock/shorthand.py

            ```


    === "Messages"

        === "OpenAI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/openai/messages.py

            ```

        === "Anthropic"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/anthropic/messages.py

            ```

        === "Google"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/google/messages.py

            ```

        === "Groq"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/groq/messages.py

            ```

        === "xAI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/xai/messages.py

            ```

        === "Mistral"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/mistral/messages.py

            ```

        === "Cohere"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/cohere/messages.py

            ```

        === "LiteLLM"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/litellm/messages.py

            ```

        === "Azure AI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/azure/messages.py

            ```

        === "Bedrock"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/bedrock/messages.py

            ```


    === "String Template"

        === "OpenAI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/openai/string_template.py

            ```

        === "Anthropic"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/anthropic/string_template.py

            ```

        === "Google"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/google/string_template.py

            ```

        === "Groq"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/groq/string_template.py

            ```

        === "xAI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/xai/string_template.py

            ```

        === "Mistral"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/mistral/string_template.py

            ```

        === "Cohere"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/cohere/string_template.py

            ```

        === "LiteLLM"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/litellm/string_template.py

            ```

        === "Azure AI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/azure/string_template.py

            ```

        === "Bedrock"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/bedrock/string_template.py

            ```


    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/openai/base_message_param.py

            ```

        === "Anthropic"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/anthropic/base_message_param.py

            ```

        === "Google"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/google/base_message_param.py

            ```

        === "Groq"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/groq/base_message_param.py

            ```

        === "xAI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/xai/base_message_param.py

            ```

        === "Mistral"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/mistral/base_message_param.py

            ```

        === "Cohere"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/cohere/base_message_param.py

            ```

        === "LiteLLM"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/litellm/base_message_param.py

            ```

        === "Azure AI"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/azure/base_message_param.py

            ```

        === "Bedrock"

            ```python hl_lines="5-7 13-18"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/overrides/bedrock/base_message_param.py

            ```



## Handling Responses

### Common Response Properties and Methods

??? api "API Documentation"

    [`mirascope.core.base.call_response`](../api/core/base/call_response.md)

All [`BaseCallResponse`](../api/core/base/call_response.md) objects share these common properties:

- `content`: The main text content of the response. If no content is present, this will be the empty string.
- `finish_reasons`: A list of reasons why the generation finished (e.g., "stop", "length"). These will be typed specifically for the provider used. If no finish reasons are present, this will be `None`.
- `model`: The name of the model used for generation.
- `id`: A unique identifier for the response if available. Otherwise this will be `None`.
- `usage`: Information about token usage for the call if available. Otherwise this will be `None`.
- `input_tokens`: The number of input tokens used if available. Otherwise this will be `None`.
- `output_tokens`: The number of output tokens generated if available. Otherwise this will be `None`.
- `cost`: An estimated cost of the API call if available. Otherwise this will be `None`.
- `message_param`: The assistant's response formatted as a message parameter.
- `tools`: A list of provider-specific tools used in the response, if any. Otherwise this will be `None`. Check out the [`Tools`](./tools.md) documentation for more details.
- `tool`: The first tool used in the response, if any. Otherwise this will be `None`. Check out the [`Tools`](./tools.md) documentation for more details.
- `tool_types`: A list of tool types used in the call, if any. Otherwise this will be `None`.
- `prompt_template`: The prompt template used for the call.
- `fn_args`: The arguments passed to the function.
- `dynamic_config`: The dynamic configuration used for the call.
- `metadata`: Any metadata provided using the dynamic configuration.
- `messages`: The list of messages sent in the request.
- `call_params`: The call parameters provided to the `call` decorator.
- `call_kwargs`: The finalized keyword arguments used to make the API call.
- `user_message_param`: The most recent user message, if any. Otherwise this will be `None`.
- `start_time`: The timestamp when the call started.
- `end_time`: The timestamp when the call ended.

There are also two common methods:

- `__str__`: Returns the `content` property of the response for easy printing.
- `tool_message_params`: Creates message parameters for tool call results. Check out the [`Tools`](./tools.md) documentation for more information.

## Multi-Modal Outputs

While most LLM providers focus on text outputs, some providers support additional output modalities like audio. The availability of multi-modal outputs varies among providers:

| Provider      | Text | Audio | Image |
|---------------|------|-------|-------|
| OpenAI        | ✓    | ✓     | -     |
| Anthropic     | ✓    | -     | -     |
| Mistral       | ✓    | -     | -     |
| Google Gemini | ✓    | -     | -     |
| Groq          | ✓    | -     | -     |
| Cohere        | ✓    | -     | -     |
| LiteLLM       | ✓    | -     | -     |
| Azure AI      | ✓    | -     | -     |

Legend: ✓ (Supported), - (Not Supported)

### Audio Outputs

- `audio`: Configuration for the audio output (voice, format, etc.)
- `modalities`: List of output modalities to receive (e.g. `["text", "audio"]`)

For providers that support audio outputs, you can receive both text and audio responses from your calls:

!!! mira ""

    === "Shorthand"
        === "OpenAI"
            ```python hl_lines="13 14 23 25"
                import io
                import wave

                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "wav"},
                        "modalities": ["text", "audio"],
                    },
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book(genre="fantasy")

                print(response.audio_transcript)

                if audio := response.audio:
                    audio_io = io.BytesIO(audio)

                    with wave.open(audio_io, "rb") as f:
                        audio_segment = AudioSegment.from_raw(
                            audio_io,
                            sample_width=f.getsampwidth(),
                            frame_rate=f.getframerate(),
                            channels=f.getnchannels(),
                        )

                    play(audio_segment)
            ```

        === "Anthropic"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Google"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Groq"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "xAI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Mistral"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Cohere"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "LiteLLM"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Azure AI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Bedrock"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

    === "Messages"
        === "OpenAI"
            ```python hl_lines="13 14 23 25"
                import io
                import wave

                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai, Messages


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "wav"},
                        "modalities": ["text", "audio"],
                    },
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book(genre="fantasy")

                print(response.audio_transcript)

                if audio := response.audio:
                    audio_io = io.BytesIO(audio)

                    with wave.open(audio_io, "rb") as f:
                        audio_segment = AudioSegment.from_raw(audio_io)

                    play(audio_segment)
            ```

        === "Anthropic"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Google"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Groq"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "xAI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Mistral"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Cohere"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "LiteLLM"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Azure AI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Bedrock"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

    === "String Template"
        === "OpenAI"
            ```python hl_lines="13 14 23 25"
                import io
                import wave

                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai, prompt_template


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "wav"},
                        "modalities": ["text", "audio"],
                    },
                )
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book(genre="fantasy")

                print(response.audio_transcript)

                if audio := response.audio:
                    audio_io = io.BytesIO(audio)

                    with wave.open(audio_io, "rb") as f:
                        audio_segment = AudioSegment.from_raw(
                            audio_io,
                            sample_width=f.getsampwidth(),
                            frame_rate=f.getframerate(),
                            channels=f.getnchannels(),
                        )

                    play(audio_segment)
            ```

        === "Anthropic"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Google"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Groq"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "xAI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Mistral"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Cohere"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "LiteLLM"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Azure AI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Bedrock"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

    === "BaseMessageParam"
        === "OpenAI"
            ```python hl_lines="13 14 23 25"
                import io
                import wave

                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai, BaseMessageParam


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "wav"},
                        "modalities": ["text", "audio"],
                    },
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book(genre="fantasy")

                print(response.audio_transcript)

                if audio := response.audio:
                    audio_io = io.BytesIO(audio)

                    with wave.open(audio_io, "rb") as f:
                        audio_segment = AudioSegment.from_raw(
                            audio_io,
                            sample_width=f.getsampwidth(),
                            frame_rate=f.getframerate(),
                            channels=f.getnchannels(),
                        )

                    play(audio_segment)
            ```

        === "Anthropic"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Google"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Groq"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "xAI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Mistral"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Cohere"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "LiteLLM"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Azure AI"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```

        === "Bedrock"
            ```python
                # ============================================================
                #                         NOT SUPPORTED
                # ============================================================
                # This example isn't supported for this provider.
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
            ```


When using models that support audio outputs, you'll have access to:

- `content`: The text content of the response
- `audio`: The raw audio bytes of the response
- `audio_transcript`: The transcript of the audio response

!!! warning "Audio Playback Requirements"

    The example above uses `pydub` and `ffmpeg` for audio playback, but you can use any audio processing libraries or media players that can handle WAV format audio data. Choose the tools that best fit your needs and environment.

    If you decide to use pydub:
    - Install [pydub](https://github.com/jiaaro/pydub): `pip install pydub`
    - Install ffmpeg: Available from [ffmpeg.org](https://www.ffmpeg.org/) or through system package managers

!!! note "Voice Options"

    For providers that support audio outputs, refer to their documentation for available voice options and configurations:
    
    - OpenAI: [Text to Speech Guide](https://platform.openai.com/docs/guides/text-to-speech)

## Common Parameters Across Providers

There are several common parameters that you'll find across all providers when using the `call` decorator. These parameters allow you to control various aspects of the LLM call:

- `model`: The only required parameter for all providers, which may be passed in as a standard argument (whereas all others are optional and must be provided as keyword arguments). It specifies which language model to use for the generation. Each provider has its own set of available models.
- `stream`: A boolean that determines whether the response should be streamed or returned as a complete response. We cover this in more detail in the [`Streams`](./streams.md) documentation.
- `response_model`: A Pydantic `BaseModel` type that defines how to structure the response. We cover this in more detail in the [`Response Models`](./response_models.md) documentation.
- `output_parser`: A function for parsing the response output. We cover this in more detail in the [`Output Parsers`](./output_parsers.md) documentation.
- `json_mode`: A boolean that deterines whether to use JSON mode or not. We cover this in more detail in the [`JSON Mode`](./json_mode.md) documentation.
- `tools`: A list of tools that the model may request to use in its response. We cover this in more detail in the [`Tools`](./tools.md) documentation.
- `client`: A custom client to use when making the call to the LLM. We cover this in more detail in the [`Custom Client`](#custom-client) section below.
- `call_params`: The provider-specific parameters to use when making the call to that provider's API. We cover this in more detail in the [`Provider-Specific Usage`](#provider-specific-usage) section below.

These common parameters provide a consistent way to control the behavior of LLM calls across different providers. Keep in mind that while these parameters are widely supported, there might be slight variations in how they're implemented or their exact effects across different providers (and the documentation should cover any such differences).

Since `call_params` is just a `TypedDict`, you can always include any additional keys at the expense of type errors (and potentially unknown behavior). This presents one way to pass provider-specific parameters (or deprecated parameters) while still using the general interface.

!!! mira ""

    === "Shorthand"
        === "OpenAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/openai/shorthand.py

            ```

        === "Anthropic"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/anthropic/shorthand.py

            ```

        === "Google"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/google/shorthand.py

            ```

        === "Groq"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/groq/shorthand.py

            ```

        === "xAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/xai/shorthand.py

            ```

        === "Mistral"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/mistral/shorthand.py

            ```

        === "Cohere"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/cohere/shorthand.py

            ```

        === "LiteLLM"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/litellm/shorthand.py

            ```

        === "Azure AI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/azure/shorthand.py

            ```

        === "Bedrock"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/bedrock/shorthand.py

            ```

    === "Messages"
        === "OpenAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/openai/messages.py

            ```

        === "Anthropic"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/anthropic/messages.py

            ```

        === "Google"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/google/messages.py

            ```

        === "Groq"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/groq/messages.py

            ```

        === "xAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/xai/messages.py

            ```

        === "Mistral"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/mistral/messages.py

            ```

        === "Cohere"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/cohere/messages.py

            ```

        === "LiteLLM"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/litellm/messages.py

            ```

        === "Azure AI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/azure/messages.py

            ```

        === "Bedrock"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/bedrock/messages.py

            ```

    === "String Template"
        === "OpenAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/openai/string_template.py

            ```

        === "Anthropic"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/anthropic/string_template.py

            ```

        === "Google"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/google/string_template.py

            ```

        === "Groq"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/groq/string_template.py

            ```

        === "xAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/xai/string_template.py

            ```

        === "Mistral"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/mistral/string_template.py

            ```

        === "Cohere"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/cohere/string_template.py

            ```

        === "LiteLLM"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/litellm/string_template.py

            ```

        === "Azure AI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/azure/string_template.py

            ```

        === "Bedrock"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/bedrock/string_template.py

            ```

    === "BaseMessageParam"
        === "OpenAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/openai/base_message_param.py

            ```

        === "Anthropic"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/anthropic/base_message_param.py

            ```

        === "Google"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/google/base_message_param.py

            ```

        === "Groq"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/groq/base_message_param.py

            ```

        === "xAI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/xai/base_message_param.py

            ```

        === "Mistral"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/mistral/base_message_param.py

            ```

        === "Cohere"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/cohere/base_message_param.py

            ```

        === "LiteLLM"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/litellm/base_message_param.py

            ```

        === "Azure AI"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/azure/base_message_param.py

            ```

        === "Bedrock"
            ```python hl_lines="4"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/call_params/bedrock/base_message_param.py

            ```


## Dynamic Configuration

Often you will want (or need) to configure your calls dynamically at runtime. Mirascope supports returning a `BaseDynamicConfig` from your prompt template, which will then be used to dynamically update the settings of the call.

In all cases, you will need to return your prompt messages through the `messages` keyword of the dynamic config unless you're using string templates.

### Call Params

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="7 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="5 8"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="7-10"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/base_message_param.py

            ```


### Metadata

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="7 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="5 9"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="7-9 11"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/dynamic_configuration/bedrock/base_message_param.py

            ```


## Provider-Specific Usage

??? api "API Documentation"

    === "OpenAI"
        [`mirascope.core.openai.call`](../api/core/openai/call.md)
        [`mirascope.core.openai.call_params`](../api/core/openai/call_params.md)
        [`mirascope.core.openai.call_response`](../api/core/openai/call_response.md)
    === "Anthropic"
        [`mirascope.core.anthropic.call`](../api/core/anthropic/call.md)
        [`mirascope.core.anthropic.call_params`](../api/core/anthropic/call_params.md)
        [`mirascope.core.anthropic.call_response`](../api/core/anthropic/call_response.md)
    === "Google"
        [`mirascope.core.google.call`](../api/core/google/call.md)
        [`mirascope.core.google.call_params`](../api/core/google/call_params.md)
        [`mirascope.core.google.call_response`](../api/core/google/call_response.md)
    === "Groq"
        [`mirascope.core.groq.call`](../api/core/groq/call.md)
        [`mirascope.core.groq.call_params`](../api/core/groq/call_params.md)
        [`mirascope.core.groq.call_response`](../api/core/groq/call_response.md)
    === "xAI"
        [`mirascope.core.xai.call`](../api/core/xai/call.md)
        [`mirascope.core.xai.call_params`](../api/core/xai/call_params.md)
        [`mirascope.core.xai.call_response`](../api/core/xai/call_response.md)
    === "Mistral"
        [`mirascope.core.mistral.call`](../api/core/mistral/call.md)
        [`mirascope.core.mistral.call_params`](../api/core/mistral/call_params.md)
        [`mirascope.core.mistral.call_response`](../api/core/mistral/call_response.md)
    === "Cohere"
        [`mirascope.core.cohere.call`](../api/core/cohere/call.md)
        [`mirascope.core.cohere.call_params`](../api/core/cohere/call_params.md)
        [`mirascope.core.cohere.call_response`](../api/core/cohere/call_response.md)
    === "LiteLLM"
        [`mirascope.core.litellm.call`](../api/core/litellm/call.md)
        [`mirascope.core.litellm.call_params`](../api/core/openai/call_params.md)
        [`mirascope.core.litellm.call_response`](../api/core/openai/call_response.md)
    === "Azure AI"
        [`mirascope.core.azure.call`](../api/core/azure/call.md)
        [`mirascope.core.azure.call_params`](../api/core/azure/call_params.md)
        [`mirascope.core.azure.call_response`](../api/core/azure/call_response.md)
    === "Bedrock"
        [`mirascope.core.bedrock.call`](../api/core/bedrock/call.md)
        [`mirascope.core.bedrock.call_params`](../api/core/bedrock/call_params.md)
        [`mirascope.core.bedrock.call_response`](../api/core/bedrock/call_response.md)

While Mirascope provides a consistent interface across different LLM providers, you can also use provider-specific modules with refined typing for an individual provider.

When using the provider modules, you'll receive a provider-specific `BaseCallResponse` object, which may have extra properties. Regardless, you can always access the full, provider-specific response object as `response.response`.

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: openai.OpenAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Anthropic"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Google"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import google


                @google.call("gemini-2.0-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: google.GoogleCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Groq"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import groq


                @groq.call("llama-3.3-70b-versatile")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: groq.GroqCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "xAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import xai


                @xai.call("grok-3")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: xai.XAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Mistral"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: mistral.MistralCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Cohere"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: cohere.CohereCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "LiteLLM"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Azure AI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: azure.AzureCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Bedrock"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import bedrock


                @bedrock.call("amazon.nova-lite-v1:0")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response: bedrock.BedrockCallResponse = recommend_book("fantasy")
                print(response.content)
            ```


    === "Messages"

        === "OpenAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: openai.OpenAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Anthropic"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Google"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, google


                @google.call("gemini-2.0-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: google.GoogleCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Groq"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.3-70b-versatile")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: groq.GroqCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "xAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, xai


                @xai.call("grok-3")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: xai.XAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Mistral"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: mistral.MistralCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Cohere"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: cohere.CohereCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "LiteLLM"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Azure AI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: azure.AzureCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Bedrock"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import Messages, bedrock


                @bedrock.call("amazon.nova-lite-v1:0")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response: bedrock.BedrockCallResponse = recommend_book("fantasy")
                print(response.content)
            ```


    === "String Template"

        === "OpenAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: openai.OpenAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Anthropic"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Google"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import google, prompt_template


                @google.call("gemini-2.0-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: google.GoogleCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Groq"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.3-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: groq.GroqCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "xAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import prompt_template, xai


                @xai.call("grok-3")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: xai.XAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Mistral"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: mistral.MistralCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Cohere"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: cohere.CohereCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "LiteLLM"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Azure AI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: azure.AzureCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Bedrock"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("amazon.nova-lite-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response: bedrock.BedrockCallResponse = recommend_book("fantasy")
                print(response.content)
            ```


    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: openai.OpenAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Anthropic"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Google"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, google


                @google.call("gemini-2.0-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: google.GoogleCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Groq"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.3-70b-versatile")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: groq.GroqCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "xAI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, xai


                @xai.call("grok-3")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: xai.XAICallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Mistral"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: mistral.MistralCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Cohere"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: cohere.CohereCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "LiteLLM"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Azure AI"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: azure.AzureCallResponse = recommend_book("fantasy")
                print(response.content)
            ```

        === "Bedrock"

            ```python hl_lines="4-6 12-17"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("amazon.nova-lite-v1:0")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response: bedrock.BedrockCallResponse = recommend_book("fantasy")
                print(response.content)
            ```



!!! note "Reasoning For Provider-Specific `BaseCallResponse` Objects"

    The reason that we have provider-specific response objects (e.g. `OpenAICallResponse`) is to provide proper type hints and safety when accessing the original response.

### Custom Messages

When using provider-specific calls, you can also always return the original message types for that provider. To do so, simply return the provider-specific dynamic config:

!!! mira ""

    === "OpenAI"

        ```python hl_lines="6"
            from mirascope.core import openai


            @openai.call("gpt-4o-mini")
            def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response: openai.OpenAICallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "Anthropic"

        ```python hl_lines="6"
            from mirascope.core import anthropic


            @anthropic.call("claude-3-5-sonnet-latest")
            def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "Google"

        ```python hl_lines="6"
            from mirascope.core import Messages, google


            @google.call("gemini-2.0-flash")
            def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                return {"messages": [Messages.User(f"Recommend a {genre} book")]}


            response: google.GoogleCallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "Groq"

        ```python hl_lines="6"
            from mirascope.core import groq


            @groq.call("llama-3.3-70b-versatile")
            def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response: groq.GroqCallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "xAI"

        ```python hl_lines="6"
            from mirascope.core import xai


            @xai.call("grok-3")
            def recommend_book(genre: str) -> xai.XAIDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response: xai.XAICallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "Mistral"

        ```python hl_lines="2 7"
            from mirascope.core import mistral
            from mistralai.models import UserMessage


            @mistral.call("mistral-large-latest")
            def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                return {"messages": [UserMessage(role="user", content=f"Recommend a {genre} book")]}


            response: mistral.MistralCallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "Cohere"

        ```python hl_lines="2 7"
            from cohere.types.chat_message import ChatMessage
            from mirascope.core import cohere


            @cohere.call("command-r-plus")
            def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
                return {"messages": [ChatMessage(role="user", message=f"Recommend a {genre} book")]}  # pyright: ignore [reportCallIssue, reportReturnType]


            response: cohere.CohereCallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "LiteLLM"

        ```python hl_lines="6"
            from mirascope.core import litellm


            @litellm.call("gpt-4o-mini")
            def recommend_book(genre: str) -> litellm.LiteLLMDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "Azure AI"

        ```python hl_lines="2 7"
            from azure.ai.inference.models import UserMessage
            from mirascope.core import azure


            @azure.call("gpt-4o-mini")
            def recommend_book(genre: str) -> azure.AzureDynamicConfig:
                return {"messages": [UserMessage(content=f"Recommend a {genre} book")]}


            response: azure.AzureCallResponse = recommend_book("fantasy")
            print(response.content)
        ```
    === "Bedrock"

        ```python hl_lines="7-9"
            from mirascope.core import bedrock


            @bedrock.call("amazon.nova-lite-v1:0")
            def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
                return {
                    "messages": [
                        {"role": "user", "content": [{"text": f"Recommend a {genre} book"}]}
                    ]
                }


            response: bedrock.BedrockCallResponse = recommend_book("fantasy")
            print(response.content)
        ```

Support for provider-specific messages ensures that you can still access newly released provider-specific features that Mirascope may not yet support natively.

### Custom Client

Mirascope allows you to use custom clients when making calls to LLM providers. This feature is particularly useful when you need to use specific client configurations, handle authentication in a custom way, or work with self-hosted models.

__Decorator Parameter:__

You can pass a client to the `call` decorator using the `client` parameter:

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai
                from openai import OpenAI


                @openai.call("gpt-4o-mini", client=OpenAI())
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import Anthropic
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-latest", client=Anthropic())
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Google"

            ```python hl_lines="1 7"
                from google.genai import Client
                from mirascope.core import google


                @google.call(
                    "gemini-2.0-flash",
                    client=Client(vertexai=True, project="your-project-id", location="us-central1"),
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import groq


                @groq.call("llama-3.3-70b-versatile", client=Groq())
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "xAI"

            ```python hl_lines="1 5"
                from mirascope.core import xai
                from openai import OpenAI


                @xai.call("grok-3", client=OpenAI(base_url="https://api.x.ai/v1"))
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Mistral"

            ```python hl_lines="4 9"
                import os

                from mirascope.core import mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import Client
                from mirascope.core import cohere


                @cohere.call("command-r-plus", client=Client())
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-11"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/",
                        credential=AzureKeyCredential("..."),
                    ),
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                import boto3

                from mirascope.core import bedrock


                @bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime"))
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, openai
                from openai import OpenAI


                @openai.call("gpt-4o-mini", client=OpenAI())
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import Anthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-latest", client=Anthropic())
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Google"

            ```python hl_lines="1 7"
                from google.genai import Client
                from mirascope.core import Messages, google


                @google.call(
                    "gemini-2.0-flash",
                    client=Client(vertexai=True, project="your-project-id", location="us-central1"),
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.3-70b-versatile", client=Groq())
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "xAI"

            ```python hl_lines="1 5"
                from mirascope.core import Messages, xai
                from openai import OpenAI


                @xai.call("grok-3", client=OpenAI(base_url="https://api.x.ai/v1"))
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Mistral"

            ```python hl_lines="4 9"
                import os

                from mirascope.core import Messages, mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import Client
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", client=Client())
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-11"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import Messages, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/",
                        credential=AzureKeyCredential("..."),
                    ),
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                import boto3

                from mirascope.core import Messages, bedrock


                @bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime"))
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai, prompt_template
                from openai import OpenAI


                @openai.call("gpt-4o-mini", client=OpenAI())
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import Anthropic
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-latest", client=Anthropic())
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Google"

            ```python hl_lines="1 7"
                from google.genai import Client
                from mirascope.core import google, prompt_template


                @google.call(
                    "gemini-2.0-flash",
                    client=Client(vertexai=True, project="your-project-id", location="us-central1"),
                )
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.3-70b-versatile", client=Groq())
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "xAI"

            ```python hl_lines="1 5"
                from mirascope.core import prompt_template, xai
                from openai import OpenAI


                @xai.call("grok-3", client=OpenAI(base_url="https://api.x.ai/v1"))
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Mistral"

            ```python hl_lines="4 9"
                import os

                from mirascope.core import mistral, prompt_template
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import Client
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", client=Client())
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-11"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, prompt_template


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/",
                        credential=AzureKeyCredential("..."),
                    ),
                )
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                import boto3

                from mirascope.core import bedrock, prompt_template


                @bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime"))
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, openai
                from openai import OpenAI


                @openai.call("gpt-4o-mini", client=OpenAI())
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import Anthropic
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-latest", client=Anthropic())
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Google"

            ```python hl_lines="1 7"
                from google.genai import Client
                from mirascope.core import BaseMessageParam, google


                @google.call(
                    "gemini-2.0-flash",
                    client=Client(vertexai=True, project="your-project-id", location="us-central1"),
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.3-70b-versatile", client=Groq())
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "xAI"

            ```python hl_lines="1 5"
                from mirascope.core import BaseMessageParam, xai
                from openai import OpenAI


                @xai.call("grok-3", client=OpenAI(base_url="https://api.x.ai/v1"))
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Mistral"

            ```python hl_lines="4 9"
                import os

                from mirascope.core import BaseMessageParam, mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @mistral.call(
                    "mistral-large-latest",
                    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import Client
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", client=Client())
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-11"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import BaseMessageParam, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/",
                        credential=AzureKeyCredential("..."),
                    ),
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                import boto3

                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime"))
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```


__Dynamic Configuration:__

You can also configure the client dynamically at runtime through the dynamic configuration:

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="2 9"       
                from mirascope.core import openai, Messages
                from openai import OpenAI


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": OpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import Anthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-latest")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Anthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 9-11" 
                from google.genai import Client
                from mirascope.core import Messages, google


                @google.call("gemini-2.0-flash")
                def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Client(
                            vertexai=True, project="your-project-id", location="us-central1"
                        ),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import Groq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.3-70b-versatile")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Groq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="2 9"       
                from mirascope.core import Messages, xai
                from openai import OpenAI


                @xai.call("grok-3")
                def recommend_book(genre: str) -> xai.XAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": OpenAI(base_url="https://api.x.ai/v1"),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"    
                import os

                from mirascope.core import mistral, Messages
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import Client
                from mirascope.core import cohere, Messages


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Client(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, Messages


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> azure.AzureDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": ChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 9"
                import boto3
                from mirascope.core import Messages, bedrock


                @bedrock.call("amazon.nova-lite-v1:0")
                def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": boto3.client("bedrock-runtime"),
                    }
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="2 9"       
                from mirascope.core import Messages, openai
                from openai import OpenAI


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": OpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import Anthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-latest")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Anthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 9-11" 
                from google.genai import Client
                from mirascope.core import Messages, google


                @google.call("gemini-2.0-flash")
                def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Client(
                            vertexai=True, project="your-project-id", location="us-central1"
                        ),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import Groq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.3-70b-versatile")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Groq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="2 9"       
                from mirascope.core import Messages, xai
                from openai import OpenAI


                @xai.call("grok-3")
                def recommend_book(genre: str) -> xai.XAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": OpenAI(base_url="https://api.x.ai/v1"),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"    
                import os

                from mirascope.core import Messages, mistral
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import Client
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Client(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> azure.AzureDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": ChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 9"
                import boto3
                from mirascope.core import Messages, bedrock


                @bedrock.call("amazon.nova-lite-v1:0")
                def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": boto3.client("bedrock-runtime"),
                    }
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="2 9"       
                from mirascope.core import openai, prompt_template
                from openai import OpenAI


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
                    return {
                        "client": OpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import Anthropic
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "client": Anthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 9-11" 
                from google.genai import Client
                from mirascope.core import google, prompt_template


                @google.call("gemini-2.0-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "client": Client(
                            vertexai=True, project="your-project-id", location="us-central1"
                        ),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import Groq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.3-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "client": Groq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="2 9"       
                from mirascope.core import prompt_template, xai
                from openai import OpenAI


                @xai.call("grok-3")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> xai.XAIDynamicConfig:
                    return {
                        "client": OpenAI(base_url="https://api.x.ai/v1"),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"    
                import os

                from mirascope.core import mistral, prompt_template
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import Client
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
                    return {
                        "client": Client(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> azure.AzureDynamicConfig:
                    return {
                        "client": ChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 9"
                import boto3
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("amazon.nova-lite-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
                    return {
                        "client": boto3.client("bedrock-runtime"),
                    }
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="2 11"
                from mirascope.core import BaseMessageParam, openai
                from openai import OpenAI


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": OpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 11"
                from anthropic import Anthropic
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-latest")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Anthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 11-13"
                from google.genai import Client
                from mirascope.core import BaseMessageParam, google


                @google.call("gemini-2.0-flash")
                def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Client(
                            vertexai=True, project="your-project-id", location="us-central1"
                        ),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 11"
                from groq import Groq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.3-70b-versatile")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Groq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="2 11"
                from mirascope.core import BaseMessageParam, xai
                from openai import OpenAI


                @xai.call("grok-3")
                def recommend_book(genre: str) -> xai.XAIDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": OpenAI(base_url="https://api.x.ai/v1"),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 13"
                import os

                from mirascope.core import BaseMessageParam, mistral
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 11"
                from cohere import Client
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Client(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 12-14"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> azure.AzureDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": ChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 11"
                import boto3
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("amazon.nova-lite-v1:0")
                def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": boto3.client("bedrock-runtime"),
                    }
            ```


!!! warning "Make sure to use the correct client!"

    A common mistake is to use the synchronous client with async calls. Read the section on [Async Custom Client](./async.md#custom-client) to see how to use a custom client with asynchronous calls.

## Error Handling

When making LLM calls, it's important to handle potential errors. Mirascope preserves the original error messages from providers, allowing you to catch and handle them appropriately:

!!! mira ""

    === "Shorthand"
        === "OpenAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/openai/shorthand.py

            ```

        === "Anthropic"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/anthropic/shorthand.py

            ```

        === "Google"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/google/shorthand.py

            ```

        === "Groq"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/groq/shorthand.py

            ```

        === "xAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/xai/shorthand.py

            ```

        === "Mistral"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/mistral/shorthand.py

            ```

        === "Cohere"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/cohere/shorthand.py

            ```

        === "LiteLLM"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/litellm/shorthand.py

            ```

        === "Azure AI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/azure/shorthand.py

            ```

        === "Bedrock"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/bedrock/shorthand.py

            ```

    === "Messages"
        === "OpenAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/openai/messages.py

            ```

        === "Anthropic"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/anthropic/messages.py

            ```

        === "Google"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/google/messages.py

            ```

        === "Groq"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/groq/messages.py

            ```

        === "xAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/xai/messages.py

            ```

        === "Mistral"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/mistral/messages.py

            ```

        === "Cohere"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/cohere/messages.py

            ```

        === "LiteLLM"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/litellm/messages.py

            ```

        === "Azure AI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/azure/messages.py

            ```

        === "Bedrock"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/bedrock/messages.py

            ```

    === "String Template"
        === "OpenAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/openai/string_template.py

            ```

        === "Anthropic"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/anthropic/string_template.py

            ```

        === "Google"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/google/string_template.py

            ```

        === "Groq"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/groq/string_template.py

            ```

        === "xAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/xai/string_template.py

            ```

        === "Mistral"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/mistral/string_template.py

            ```

        === "Cohere"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/cohere/string_template.py

            ```

        === "LiteLLM"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/litellm/string_template.py

            ```

        === "Azure AI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/azure/string_template.py

            ```

        === "Bedrock"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/bedrock/string_template.py

            ```

    === "BaseMessageParam"
        === "OpenAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/openai/base_message_param.py

            ```

        === "Anthropic"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/anthropic/base_message_param.py

            ```

        === "Google"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/google/base_message_param.py

            ```

        === "Groq"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/groq/base_message_param.py

            ```

        === "xAI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/xai/base_message_param.py

            ```

        === "Mistral"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/mistral/base_message_param.py

            ```

        === "Cohere"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/cohere/base_message_param.py

            ```

        === "LiteLLM"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/litellm/base_message_param.py

            ```

        === "Azure AI"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/azure/base_message_param.py

            ```

        === "Bedrock"
            ```python hl_lines="1 10 13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/calls/error_handling/bedrock/base_message_param.py

            ```


These examples catch the base Exception class; however, you can (and should) catch provider-specific exceptions instead when using provider-specific modules.

## Next Steps

By mastering calls in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend choosing one of:

- [Streams](./streams.md) to see how to stream call responses for a more real-time interaction.
- [Chaining](./chaining.md) to see how to chain calls together.
- [Response Models](./response_models.md) to see how to generate structured outputs.
- [Tools](./tools.md) to see how to give LLMs access to custom tools to extend their capabilities.
- [Async](./async.md) to see how to better take advantage of asynchronous programming and parallelization for improved performance.

Pick whichever path aligns best with what you're hoping to get from Mirascope.
