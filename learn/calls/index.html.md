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

We currently support [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Gemini](https://gemini.google.com), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Vertex AI](https://cloud.google.com/vertex-ai)

If there are any providers we don't yet support that you'd like to see supported, let us know!

??? api "API Documentation"

    [`mirascope.core.openai.call`](../api/core/openai/call.md)
    [`mirascope.core.anthropic.call`](../api/core/anthropic/call.md)
    [`mirascope.core.mistral.call`](../api/core/mistral/call.md)
    [`mirascope.core.gemini.call`](../api/core/gemini/call.md)
    [`mirascope.core.groq.call`](../api/core/groq/call.md)
    [`mirascope.core.cohere.call`](../api/core/cohere/call.md)
    [`mirascope.core.litellm.call`](../api/core/litellm/call.md)
    [`mirascope.core.azure.call`](../api/core/azure/call.md)
    [`mirascope.core.vertex.call`](../api/core/vertex/call.md)
    [`mirascope.core.bedrock.call`](../api/core/bedrock/call.md)

## Basic Usage and Syntax

### Provider-Specific Usage

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 6"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="4 6"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="4 6"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="4 6"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="4 6"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="4 6"
                from mirascope.core import cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="4 6"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="4 6"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="4 6"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="4 6"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="4 6"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 5"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="4 5"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="4 5"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="4 5"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="4 5"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="4 5"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="4 5"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="4 5"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="4 5"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="4 5"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="4 6"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
                print(response.content)
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
                    model="claude-3-5-sonnet-20240620",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                    max_tokens=1024,
                )
                block = message.content[0]
                return block.text if block.type == "text" else ""


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

    === "Gemini"

        ```python hl_lines="7-10"
            from google.generativeai import GenerativeModel

            client = GenerativeModel("gemini-1.5-flash")


            def recommend_book(genre: str) -> str:
                generation = client.generate_content(
                    contents=[{"role": "user", "parts": f"Recommend a {genre} book"}]  # pyright: ignore [reportArgumentType]
                )
                return generation.candidates[0].content.parts[0].text


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Groq"

        ```python hl_lines="7-11"
            from groq import Groq

            client = Groq()


            def recommend_book(genre: str) -> str:
                completion = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
                )
                return str(completion.choices[0].message.content)


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

    === "Vertex AI"

        ```python hl_lines="7-10"
            from vertexai.generative_models import GenerativeModel

            client = GenerativeModel("gemini-1.5-flash")


            def recommend_book(genre: str) -> str:
                generation = client.generate_content(
                    contents=[{"role": "user", "parts": f"Recommend a {genre} book"}]
                )
                return generation.candidates[0].content.parts[0].text  # type: ignore


            output = recommend_book("fantasy")
            print(output)
        ```

    === "Bedrock"

        ```python hl_lines="7-11"
            import boto3

            bedrock_client = boto3.client(service_name="bedrock-runtime")


            def recommend_book(genre: str) -> str:
                messages = [{"role": "user", "content": [{"text": f"Recommend a {genre} book"}]}]
                response = bedrock_client.converse(
                    modelId="anthropic.claude-3-haiku-20240307-v1:0",
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

In these above Mirascope examples, we are directly tying the prompt to a specific provider and call setting (provider-specific prompt engineering). In these cases, the `@prompt_template` decorator becomes optional unless you're using string templates.

### Provider-Agnostic Usage

We've implemented calls as decorators so that they work for both provider-specific cases (as seen above) as well as provider-agnostic cases.

Let's take a look at a basic example using Mirascope to call both OpenAI and Anthropic with the same prompt:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="4-6 11 17"
            from mirascope.core import anthropic, openai, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> str:
                return f"Recommend a {genre} book"


            # OpenAI
            openai_model = "gpt-4o-mini"
            openai_recommend_book = openai.call(openai_model)(recommend_book_prompt)
            openai_response = openai_recommend_book("fantasy")
            print(openai_response.content)

            # Anthropic
            anthropic_model = "claude-3-5-sonnet-20240620"
            anthropic_recommend_book = anthropic.call(anthropic_model)(recommend_book_prompt)
            anthropic_response = anthropic_recommend_book("fantasy")
            print(anthropic_response.content)
        ```
    === "Messages"

        ```python hl_lines="4-6 11 17"
            from mirascope.core import Messages, anthropic, openai, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> Messages.Type:
                return Messages.User(f"Recommend a {genre} book")


            # OpenAI
            openai_model = "gpt-4o-mini"
            openai_recommend_book = openai.call(openai_model)(recommend_book_prompt)
            openai_response = openai_recommend_book("fantasy")
            print(openai_response.content)

            # Anthropic
            anthropic_model = "claude-3-5-sonnet-20240620"
            anthropic_recommend_book = anthropic.call(anthropic_model)(recommend_book_prompt)
            anthropic_response = anthropic_recommend_book("fantasy")
            print(anthropic_response.content)
        ```
    === "String Template"

        ```python hl_lines="4-5 10 16"
            from mirascope.core import anthropic, openai, prompt_template


            @prompt_template("Recommend a {genre} book")
            def recommend_book_prompt(genre: str): ...


            # OpenAI
            openai_model = "gpt-4o-mini"
            openai_recommend_book = openai.call(openai_model)(recommend_book_prompt)
            openai_response = openai_recommend_book("fantasy")
            print(openai_response.content)

            # Anthropic
            anthropic_model = "claude-3-5-sonnet-20240620"
            anthropic_recommend_book = anthropic.call(anthropic_model)(recommend_book_prompt)
            anthropic_response = anthropic_recommend_book("fantasy")
            print(anthropic_response.content)
        ```
    === "BaseMessageParam"

        ```python hl_lines="4-6 11 17"
            from mirascope.core import BaseMessageParam, anthropic, openai, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
                return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


            # OpenAI
            openai_model = "gpt-4o-mini"
            openai_recommend_book = openai.call(openai_model)(recommend_book_prompt)
            openai_response = openai_recommend_book("fantasy")
            print(openai_response.content)

            # Anthropic
            anthropic_model = "claude-3-5-sonnet-20240620"
            anthropic_recommend_book = anthropic.call(anthropic_model)(recommend_book_prompt)
            anthropic_response = anthropic_recommend_book("fantasy")
            print(anthropic_response.content)
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

### Provider-Specific Response Details

??? api "API Documentation"

    [`mirascope.core.openai.call_response`](../api/core/openai/call_response.md)
    [`mirascope.core.anthropic.call_response`](../api/core/anthropic/call_response.md)
    [`mirascope.core.mistral.call_response`](../api/core/mistral/call_response.md)
    [`mirascope.core.gemini.call_response`](../api/core/gemini/call_response.md)
    [`mirascope.core.groq.call_response`](../api/core/groq/call_response.md)
    [`mirascope.core.cohere.call_response`](../api/core/cohere/call_response.md)
    [`mirascope.core.litellm.call_response`](../api/core/openai/call_response.md)
    [`mirascope.core.azure.call_response`](../api/core/azure/call_response.md)
    [`mirascope.core.vertex.call_response`](../api/core/vertex/call_response.md)
    [`mirascope.core.bedrock.call_response`](../api/core/bedrock/call_response.md)

While Mirascope provides a consistent interface, you can also always access the full, provider-specific response object if needed. This is available through the `response` property of the `BaseCallResponse` object.

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="10"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Anthropic"

            ```python hl_lines="10"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Mistral"

            ```python hl_lines="10"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Gemini"

            ```python hl_lines="10"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Groq"

            ```python hl_lines="10"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Cohere"

            ```python hl_lines="10"
                from mirascope.core import cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "LiteLLM"

            ```python hl_lines="10"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Azure AI"

            ```python hl_lines="10"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Vertex AI"

            ```python hl_lines="10"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Bedrock"

            ```python hl_lines="10"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            original_response = response.response
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="10"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Anthropic"

            ```python hl_lines="10"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Mistral"

            ```python hl_lines="10"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Gemini"

            ```python hl_lines="10"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Groq"

            ```python hl_lines="10"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Cohere"

            ```python hl_lines="10"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "LiteLLM"

            ```python hl_lines="10"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Azure AI"

            ```python hl_lines="10"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Vertex AI"

            ```python hl_lines="10"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Bedrock"

            ```python hl_lines="10"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            original_response = response.response
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="10"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Anthropic"

            ```python hl_lines="10"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Mistral"

            ```python hl_lines="10"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Gemini"

            ```python hl_lines="10"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Groq"

            ```python hl_lines="10"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Cohere"

            ```python hl_lines="10"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "LiteLLM"

            ```python hl_lines="10"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Azure AI"

            ```python hl_lines="10"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Vertex AI"

            ```python hl_lines="10"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Bedrock"

            ```python hl_lines="10"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            original_response = response.response
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Anthropic"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Mistral"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Gemini"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Groq"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Cohere"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "LiteLLM"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Azure AI"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Vertex AI"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```

        === "Bedrock"

            ```python hl_lines="10"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            original_response = response.response
            ```


!!! note "Reasoning For Provider-Specific `BaseCallResponse` Objects"

    The reason that we have provider-specific response objects (e.g. `OpenAICallResponse`) is to provide proper type hints and safety when accessing the original response.

## Multi-Modal Outputs

While most LLM providers focus on text outputs, some providers support additional output modalities like audio. The availability of multi-modal outputs varies among providers:

| Provider    | Text | Audio | Image |
|------------|------|-------|-------|
| OpenAI     | ✓    | ✓     | -     |
| Anthropic  | ✓    | -     | -     |
| Mistral    | ✓    | -     | -     |
| Gemini     | ✓    | -     | -     |
| Groq       | ✓    | -     | -     |
| Cohere     | ✓    | -     | -     |
| LiteLLM    | ✓    | -     | -     |
| Azure AI   | ✓    | -     | -     |
| Vertex AI  | ✓    | -     | -     |

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

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="13 14 23 25"
                # Not supported
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

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="13 14 23 25"
                # Not supported
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

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="13 14 23 25"
                # Not supported
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

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="13 14 23 25"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="13 14 23 25"
                # Not supported
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

While each LLM provider has its own specific parameters, there are several common parameters that you'll find across all providers when using the `call` decorator. These parameters allow you to control various aspects of the LLM call:

- `model`: The only required parameter for all providers, which may be passed in as a standard argument (whereas all others are optional and must be provided as keyword arguments). It specifies which language model to use for the generation. Each provider has its own set of available models.
- `stream`: A boolean that determines whether the response should be streamed or returned as a complete response. We cover this in more detail in the [`Streams`](./streams.md) documentation.
- `response_model`: A Pydantic `BaseModel` type that defines how to structure the response. We cover this in more detail in the [`Response Models`](./response_models.md) documentation.
- `output_parser`: A function for parsing the response output. We cover this in more detail in the [`Output Parsers`](./output_parsers.md) documentation.
- `json_mode`: A boolean that deterines whether to use JSON mode or not. We cover this in more detail in the [`JSON Mode`](./json_mode.md) documentation.
- `tools`: A list of tools that the model may request to use in its response. We cover this in more detail in the [`Tools`](./tools.md) documentation.
- `client`: A custom client to use when making the call to the LLM. We cover this in more detail in the [`Custom Client`](#custom-client) section below.
- `call_params`: The provider-specific parameters to use when making the call to that provider's API. We cover this in more detail in the [`Provider-Specific Parameters`](#provider-specific-parameters) section below.

These common parameters provide a consistent way to control the behavior of LLM calls across different providers. Keep in mind that while these parameters are widely supported, there might be slight variations in how they're implemented or their exact effects across different providers (and the documentation should cover any such differences).

## Provider-Specific Parameters

??? api "API Documentation"

    [`mirascope.core.openai.call_params`](../api/core/openai/call_params.md)
    [`mirascope.core.anthropic.call_params`](../api/core/anthropic/call_params.md)
    [`mirascope.core.mistral.call_params`](../api/core/mistral/call_params.md)
    [`mirascope.core.gemini.call_params`](../api/core/gemini/call_params.md)
    [`mirascope.core.groq.call_params`](../api/core/groq/call_params.md)
    [`mirascope.core.cohere.call_params`](../api/core/cohere/call_params.md)
    [`mirascope.core.litellm.call_params`](../api/core/openai/call_params.md)
    [`mirascope.core.azure.call_params`](../api/core/azure/call_params.md)
    [`mirascope.core.vertex.call_params`](../api/core/vertex/call_params.md)
    [`mirascope.core.bedrock.call_params`](../api/core/bedrock/call_params.md)

While Mirascope provides a consistent interface across different LLM providers, each provider has its own set of specific parameters that can be used to further configure the behavior of the model. These parameters are passed to the `call` decorator through the `call_params` argument.

For all providers, we have only included additional call parameters that are not already covered as shared arguments to the `call` decorator (e.g. `model`). We have also opted to exclude currently deprecated parameters entirely. However, since `call_params` is just a `TypedDict`, you can always include any additional keys at the expense of type errors (and potentially unknown behavior).

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="4"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            ```

        === "Anthropic"

            ```python hl_lines="4"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            ```

        === "Mistral"

            ```python hl_lines="4"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            ```

        === "Gemini"

            ```python hl_lines="1 7"
                from google.generativeai import GenerationConfig
                from mirascope.core import gemini


                @gemini.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                def recommend_book(genre: str) -> str:
            ```

        === "Groq"

            ```python hl_lines="4"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            ```

        === "Cohere"

            ```python hl_lines="4"
                from mirascope.core import cohere


                @cohere.call("command-r-plus", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            ```

        === "LiteLLM"

            ```python hl_lines="4"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            ```

        === "Azure AI"

            ```python hl_lines="4"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                response = recommend_book("fantasy")
            ```

        === "Vertex AI"

            ```python hl_lines="2 7"
                from mirascope.core import vertex
                from vertexai.generative_models import GenerationConfig


                @vertex.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                def recommend_book(genre: str) -> str:
            ```

        === "Bedrock"

            ```python hl_lines="4"
                from mirascope.core import bedrock


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    call_params={"inferenceConfig": {"maxTokens": 512}},
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="4"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            ```

        === "Anthropic"

            ```python hl_lines="4"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            ```

        === "Mistral"

            ```python hl_lines="4"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            ```

        === "Gemini"

            ```python hl_lines="1 7"
                from google.generativeai import GenerationConfig
                from mirascope.core import Messages, gemini


                @gemini.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                def recommend_book(genre: str) -> Messages.Type:
            ```

        === "Groq"

            ```python hl_lines="4"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            ```

        === "Cohere"

            ```python hl_lines="4"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            ```

        === "LiteLLM"

            ```python hl_lines="4"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            ```

        === "Azure AI"

            ```python hl_lines="4"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                response = recommend_book("fantasy")
            ```

        === "Vertex AI"

            ```python hl_lines="2 7"
                from mirascope.core import Messages, vertex
                from vertexai.generative_models import GenerationConfig


                @vertex.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                def recommend_book(genre: str) -> Messages.Type:
            ```

        === "Bedrock"

            ```python hl_lines="4"
                from mirascope.core import Messages, bedrock


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    call_params={"inferenceConfig": {"maxTokens": 512}},
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="4"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", call_params={"max_tokens": 512})
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            ```

        === "Anthropic"

            ```python hl_lines="4"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", call_params={"max_tokens": 512})
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            ```

        === "Mistral"

            ```python hl_lines="4"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", call_params={"max_tokens": 512})
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            ```

        === "Gemini"

            ```python hl_lines="1 7"
                from google.generativeai import GenerationConfig
                from mirascope.core import gemini, prompt_template


                @gemini.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                @prompt_template("Recommend a {genre} book")
            ```

        === "Groq"

            ```python hl_lines="4"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", call_params={"max_tokens": 512})
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            ```

        === "Cohere"

            ```python hl_lines="4"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", call_params={"max_tokens": 512})
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            ```

        === "LiteLLM"

            ```python hl_lines="4"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", call_params={"max_tokens": 512})
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            ```

        === "Azure AI"

            ```python hl_lines="4"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", call_params={"max_tokens": 512})
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                response = recommend_book("fantasy")
            ```

        === "Vertex AI"

            ```python hl_lines="2 7"
                from mirascope.core import prompt_template, vertex
                from vertexai.generative_models import GenerationConfig


                @vertex.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                @prompt_template("Recommend a {genre} book")
            ```

        === "Bedrock"

            ```python hl_lines="4"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    call_params={"inferenceConfig": {"maxTokens": 512}},
                )
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            ```

        === "Anthropic"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            ```

        === "Mistral"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            ```

        === "Gemini"

            ```python hl_lines="1 7"
                from google.generativeai import GenerationConfig
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
            ```

        === "Groq"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            ```

        === "Cohere"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            ```

        === "LiteLLM"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            ```

        === "Azure AI"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", call_params={"max_tokens": 512})
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                response = recommend_book("fantasy")
            ```

        === "Vertex AI"

            ```python hl_lines="2 7"
                from mirascope.core import BaseMessageParam, vertex
                from vertexai.generative_models import GenerationConfig


                @vertex.call(
                    "gemini-1.5-flash",
                    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
            ```

        === "Bedrock"

            ```python hl_lines="4"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    call_params={"inferenceConfig": {"maxTokens": 512}},
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```


## Dynamic Configuration

Often you will want (or need) to configure your calls dynamically at runtime. Mirascope supports returning a `BaseDynamicConfig` from your prompt template, which will then be used to dynamically update the settings of the call.

In all cases, you will need to return your prompt messages through the `messages` keyword of the dynamic config unless you're using string templates.

### Call Params

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="7 8"
                from mirascope.core import BaseDynamicConfig, Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, openai, prompt_template


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 8"
                from mirascope.core import BaseDynamicConfig, bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="7-10"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```


### Metadata

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="7 9"
                from mirascope.core import BaseDynamicConfig, Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, openai, prompt_template


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 9"
                from mirascope.core import BaseDynamicConfig, bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, openai


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="7-9 11"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> BaseDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "call_params": {"max_tokens": 512},
                        "metadata": {"tags": {"version:0001"}},
                    }


                response = recommend_book("fantasy")
                print(response.content)
            ```


## Custom Messages

You can also always return the original message types for any provider. To do so, simply return the provider-specific dynamic config:

!!! mira ""

    === "OpenAI"

        ```python hl_lines="6"
            from mirascope.core import openai


            @openai.call("gpt-4o-mini")
            def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Anthropic"

        ```python hl_lines="6"
            from mirascope.core import anthropic


            @anthropic.call("claude-3-5-sonnet-20240620")
            def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Mistral"

        ```python hl_lines="7"
            from mirascope.core import mistral
            from mistralai.models import UserMessage


            @mistral.call("mistral-large-latest")
            def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                return {"messages": [UserMessage(role="user", content=f"Recommend a {genre} book")]}


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Gemini"

        ```python hl_lines="6"
            from mirascope.core import gemini


            @gemini.call("gemini-1.5-flash")
            def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                return {"messages": [{"role": "user", "parts": [f"Recommend a {genre} book"]}]}


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Groq"

        ```python hl_lines="6"
            from mirascope.core import groq


            @groq.call("llama-3.1-70b-versatile")
            def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Cohere"

        ```python hl_lines="7"
            from cohere.types.chat_message import ChatMessage
            from mirascope.core import cohere


            @cohere.call("command-r-plus")
            def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
                return {"messages": [ChatMessage(role="user", message=f"Recommend a {genre} book")]}  # pyright: ignore [reportCallIssue, reportReturnType]


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "LiteLLM"

        ```python hl_lines="6"
            from mirascope.core import litellm


            @litellm.call("gpt-4o-mini")
            def recommend_book(genre: str) -> litellm.LiteLLMDynamicConfig:
                return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Azure AI"

        ```python hl_lines="7"
            from azure.ai.inference.models import UserMessage
            from mirascope.core import azure


            @azure.call("gpt-4o-mini")
            def recommend_book(genre: str) -> azure.AzureDynamicConfig:
                return {"messages": [UserMessage(content=f"Recommend a {genre} book")]}


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Vertex AI"

        ```python hl_lines="8-10"
            from mirascope.core import vertex
            from vertexai.generative_models import Content, Part


            @vertex.call("gemini-1.5-flash")
            def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
                return {
                    "messages": [
                        Content(role="user", parts=[Part.from_text(f"Recommend a {genre} book")])
                    ]
                }


            response = recommend_book("fantasy")
            print(response.content)
        ```
    === "Bedrock"

        ```python hl_lines="6"
            from mirascope.core import bedrock


            @bedrock.call("claude-3-5-sonnet-20240620")
            def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
                return {
                    "messages": [
                        {"role": "user", "content": [{"text": f"Recommend a {genre} book"}]}
                    ]
                }


            response = recommend_book("fantasy")
            print(response.content)
        ```

## Custom Client

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


                @anthropic.call("claude-3-5-sonnet-20240620", client=Anthropic())
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Mistral"

            ```python hl_lines="4 8"
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

        === "Gemini"

            ```python hl_lines="1 5"
                from google.generativeai import GenerativeModel
                from mirascope.core import gemini


                @gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", client=Groq())
                def recommend_book(genre: str) -> str:
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

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                from mirascope.core import bedrock
                import boto3


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=boto3.client("bedrock-runtime")
                )
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


                @anthropic.call("claude-3-5-sonnet-20240620", client=Anthropic())
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Mistral"

            ```python hl_lines="4 8"
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

        === "Gemini"

            ```python hl_lines="1 5"
                from google.generativeai import GenerativeModel
                from mirascope.core import Messages, gemini


                @gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", client=Groq())
                def recommend_book(genre: str) -> Messages.Type:
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

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import Messages, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                from mirascope.core import Messages, bedrock
                import boto3


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=boto3.client("bedrock-runtime")
                )
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


                @anthropic.call("claude-3-5-sonnet-20240620", client=Anthropic())
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Mistral"

            ```python hl_lines="4 8"
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

        === "Gemini"

            ```python hl_lines="1 5"
                from google.generativeai import GenerativeModel
                from mirascope.core import gemini, prompt_template


                @gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", client=Groq())
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
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

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, prompt_template


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import prompt_template, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                from mirascope.core import bedrock, prompt_template
                import boto3


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=boto3.client("bedrock-runtime")
                )
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


                @anthropic.call("claude-3-5-sonnet-20240620", client=Anthropic())
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Mistral"

            ```python hl_lines="4 8"
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

        === "Gemini"

            ```python hl_lines="1 5"
                from google.generativeai import GenerativeModel
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import Groq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", client=Groq())
                def recommend_book(genre: str) -> list[BaseMessageParam]:
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

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference import ChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import BaseMessageParam, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=ChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Bedrock"

            ```python hl_lines="1 6"
                from mirascope.core import BaseMessageParam, bedrock
                import boto3


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=boto3.client("bedrock-runtime")
                )
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

            ```python hl_lines="2 9"
                from anthropic import Anthropic
                from mirascope.core import anthropic, Messages


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Anthropic(),
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

        === "Gemini"

            ```python hl_lines="2 9"
                from google.generativeai import GenerativeModel
                from mirascope.core import gemini, Messages


                @gemini.call("")
                def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="2 9"
                from groq import Groq
                from mirascope.core import groq, Messages


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Groq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="2 9"
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

            ```python hl_lines="1-2 10-11"
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

        === "Vertex AI"

            ```python hl_lines="2 9"
                from mirascope.core import vertex, Messages
                from vertexai.generative_models import GenerativeModel


                @vertex.call("")
                def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 11"
                from mirascope.core import bedrock, Messages
                import boto3


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
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

            ```python hl_lines="2 9"
                from anthropic import Anthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Anthropic(),
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

        === "Gemini"

            ```python hl_lines="2 9"
                from google.generativeai import GenerativeModel
                from mirascope.core import Messages, gemini


                @gemini.call("")
                def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="2 9"
                from groq import Groq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Groq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="2 9"
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

            ```python hl_lines="1-2 10-11"
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

        === "Vertex AI"

            ```python hl_lines="2 9"
                from mirascope.core import Messages, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("")
                def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 11"
                from mirascope.core import Messages, bedrock
                import boto3


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                )
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

            ```python hl_lines="2 9"
                from anthropic import Anthropic
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "client": Anthropic(),
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

        === "Gemini"

            ```python hl_lines="2 9"
                from google.generativeai import GenerativeModel
                from mirascope.core import gemini, prompt_template


                @gemini.call("")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="2 9"
                from groq import Groq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "client": Groq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="2 9"
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

            ```python hl_lines="1-2 10-11"
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

        === "Vertex AI"

            ```python hl_lines="2 9"
                from mirascope.core import prompt_template, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
                    return {
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 11"
                from mirascope.core import bedrock, prompt_template
                import boto3


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
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

            ```python hl_lines="2 11"
                from anthropic import Anthropic
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Anthropic(),
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

        === "Gemini"

            ```python hl_lines="2 11"
                from google.generativeai import GenerativeModel
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("")
                def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="2 11"
                from groq import Groq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> groq.GroqDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Groq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="2 11"
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

        === "Vertex AI"

            ```python hl_lines="2 11"
                from mirascope.core import BaseMessageParam, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("")
                def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="1 11"
                from mirascope.core import BaseMessageParam, bedrock
                import boto3


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
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

            ```python hl_lines="2 10 13"
                from mirascope.core import openai
                from openai import OpenAIError


                @openai.call(model="gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import mistral
                from mistralai import models


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import gemini


                @gemini.call(model="gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import groq


                @groq.call(model="llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import cohere


                @cohere.call(model="command-r-plus")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import litellm


                @litellm.call(model="gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import azure


                @azure.call(model="gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import vertex


                @vertex.call(model="gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import bedrock
                from botocore.exceptions import ClientError


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="2 10 13"
                from mirascope.core import Messages, openai
                from openai import OpenAIError


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import Messages, mistral
                from mistralai import models


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import Messages, bedrock
                from botocore.exceptions import ClientError


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="2 10 13"
                from mirascope.core import openai, prompt_template
                from openai import OpenAIError


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import mistral, prompt_template
                from mistralai import models


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import bedrock, prompt_template
                from botocore.exceptions import ClientError


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="2 10 13"
                from mirascope.core import BaseMessageParam, openai
                from openai import OpenAIError


                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import BaseMessageParam, mistral
                from mistralai import models


                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import BaseMessageParam, bedrock
                from botocore.exceptions import ClientError


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    response = recommend_book("fantasy")
                    print(response.content)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```


By catching provider-specific errors, you can implement appropriate error handling and fallback strategies in your application. You can of course always catch the base Exception instead of provider-specific exceptions (which we needed to do in some of our examples due to not being able to find the right exceptions to catch for those providers...).

## Next Steps

By mastering calls in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend choosing one of:

- [Streams](./streams.md) to see how to stream call responses for a more real-time interaction.
- [Chaining](./chaining.md) to see how to chain calls together.
- [Response Models](./response_models.md) to see how to generate structured outputs.
- [Tools](./tools.md) to see how to give LLMs access to custom tools to extend their capabilities.
- [Async](./async.md) to see how to better take advantage of asynchronous programming and parallelization for improved performance.

Pick whichever path aligns best with what you're hoping to get from Mirascope.
