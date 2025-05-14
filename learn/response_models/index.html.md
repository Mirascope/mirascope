---
search:
  boost: 2
---

# Response Models

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Response Models in Mirascope provide a powerful way to structure and validate the output from Large Language Models (LLMs). By leveraging Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), Response Models offer type safety, automatic validation, and easier data manipulation for your LLM responses. While we cover some details in this documentation, we highly recommend reading through Pydantic's documentation for a deeper, comprehensive dive into everything you can do with Pydantic's `BaseModel`.

## Why Use Response Models?

1. **Structured Output**: Define exactly what you expect from the LLM, ensuring consistency in responses.
2. **Automatic Validation**: Pydantic handles type checking and validation, reducing errors in your application.
3. **Improved Type Hinting**: Better IDE support and clearer code structure.
4. **Easier Data Manipulation**: Work with Python objects instead of raw strings or dictionaries.

## Basic Usage and Syntax

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/base_message_param.py

            ```


??? note "Official SDK"

    === "OpenAI"

        ```python hl_lines="18-39 44"
            from openai import OpenAI
            from pydantic import BaseModel

            client = OpenAI()


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Extract {text}"}],
                    tools=[
                        {
                            "function": {
                                "name": "Book",
                                "description": "An extracted book.",
                                "parameters": {
                                    "properties": {
                                        "title": {"type": "string"},
                                        "author": {"type": "string"},
                                    },
                                    "required": ["title", "author"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                    tool_choice="required",
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    return Book.model_validate_json(tool_calls[0].function.arguments)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Anthropic"

        ```python hl_lines="19-38 43"
            from anthropic import Anthropic
            from pydantic import BaseModel

            client = Anthropic()


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                message = client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": f"Extract {text}"}],
                    tools=[
                        {
                            "name": "Book",
                            "description": "An extracted book.",
                            "input_schema": {
                                "properties": {
                                    "title": {"type": "string"},
                                    "author": {"type": "string"},
                                },
                                "required": ["title", "author"],
                                "type": "object",
                            },
                        }
                    ],
                    tool_choice={"type": "tool", "name": "Book"},
                )
                for block in message.content:
                    if block.type == "tool_use" and block.input is not None:
                        return Book.model_validate(block.input)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Google"

        ```python hl_lines="21-60 65"
            from google.genai import Client
            from google.genai.types import FunctionDeclaration, Tool
            from proto.marshal.collections import RepeatedComposite
            from pydantic import BaseModel

            client = Client()


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents={"parts": [{"text": f"Extract {text}"}]},
                    config={
                        "tools": [
                            Tool(
                                function_declarations=[
                                    FunctionDeclaration(
                                        **{
                                            "name": "Book",
                                            "description": "An extracted book.",
                                            "parameters": {
                                                "properties": {
                                                    "title": {"type": "string"},
                                                    "author": {"type": "string"},
                                                },
                                                "required": ["title", "author"],
                                                "type": "object",
                                            },
                                        }
                                    )
                                ]
                            )
                        ],
                        "tool_config": {
                            "function_calling_config": {
                                "mode": "any",
                                "allowed_function_names": ["Book"],
                            }
                        },  # pyright: ignore [reportArgumentType]
                    },
                )
                if tool_calls := [
                    function_call
                    for function_call in (response.function_calls or [])
                    if function_call.args
                ]:
                    return Book.model_validate(
                        {
                            k: v if not isinstance(v, RepeatedComposite) else list(v)
                            for k, v in (tool_calls[0].args or {}).items()
                        }
                    )
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Groq"

        ```python hl_lines="18-39 44"
            from groq import Groq
            from pydantic import BaseModel

            client = Groq()


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Extract {text}"}],
                    tools=[
                        {
                            "function": {
                                "name": "Book",
                                "description": "An extracted book.",
                                "parameters": {
                                    "properties": {
                                        "title": {"type": "string"},
                                        "author": {"type": "string"},
                                    },
                                    "required": ["title", "author"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                    tool_choice="required",
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    return Book.model_validate_json(tool_calls[0].function.arguments)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "xAI"

        ```python hl_lines="18-39 44"
            from openai import OpenAI
            from pydantic import BaseModel

            client = OpenAI(base_url="https://api.x.ai/v1", api_key="YOUR_KEY_HERE")


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Extract {text}"}],
                    tools=[
                        {
                            "function": {
                                "name": "Book",
                                "description": "An extracted book.",
                                "parameters": {
                                    "properties": {
                                        "title": {"type": "string"},
                                        "author": {"type": "string"},
                                    },
                                    "required": ["title", "author"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                    tool_choice="required",
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    return Book.model_validate_json(tool_calls[0].function.arguments)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Mistral"

        ```python hl_lines="21-46 51"
            import os
            from typing import cast

            from mistralai import Mistral
            from pydantic import BaseModel

            client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                completion = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": f"Extract {text}"}],
                    tools=[
                        {
                            "function": {
                                "name": "Book",
                                "description": "An extracted book.",
                                "parameters": {
                                    "properties": {
                                        "title": {"type": "string"},
                                        "author": {"type": "string"},
                                    },
                                    "required": ["title", "author"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                    tool_choice="any",
                )
                if (
                    completion
                    and (choices := completion.choices)
                    and (tool_calls := choices[0].message.tool_calls)
                ):
                    return Book.model_validate_json(cast(str, tool_calls[0].function.arguments))
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Cohere"

        ```python hl_lines="19-36 41"
            from cohere import Client
            from cohere.types import Tool, ToolParameterDefinitionsValue
            from pydantic import BaseModel

            client = Client()


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                response = client.chat(
                    model="command-r-plus",
                    message=f"Extract {text}",
                    tools=[
                        Tool(
                            name="Book",
                            description="An extracted book.",
                            parameter_definitions={
                                "title": ToolParameterDefinitionsValue(
                                    description=None, type="string", required=True
                                ),
                                "author": ToolParameterDefinitionsValue(
                                    description=None, type="string", required=True
                                ),
                            },
                        )
                    ],
                )
                if response.tool_calls:
                    return Book.model_validate(response.tool_calls[0].parameters)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "LiteLLM"

        ```python hl_lines="16-37 42"
            from litellm import completion
            from pydantic import BaseModel


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                response = completion(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Extract {text}"}],
                    tools=[
                        {
                            "function": {
                                "name": "Book",
                                "description": "An extracted book.",
                                "parameters": {
                                    "properties": {
                                        "title": {"type": "string"},
                                        "author": {"type": "string"},
                                    },
                                    "required": ["title", "author"],
                                    "type": "object",
                                },
                            },
                            "type": "function",
                        }
                    ],
                    tool_choice="required",
                )
                if tool_calls := response.choices[0].message.tool_calls:  # pyright: ignore [reportAttributeAccessIssue]
                    return Book.model_validate_json(tool_calls[0].function.arguments)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Azure AI"

        ```python hl_lines="26-46 51"
            from azure.ai.inference import ChatCompletionsClient
            from azure.ai.inference.models import (
                ChatCompletionsToolDefinition,
                ChatRequestMessage,
                FunctionDefinition,
            )
            from azure.core.credentials import AzureKeyCredential
            from pydantic import BaseModel

            client = ChatCompletionsClient(
                endpoint="YOUR_ENDPOINT", credential=AzureKeyCredential("YOUR_KEY")
            )


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                completion = client.complete(
                    model="gpt-4o-mini",
                    messages=[ChatRequestMessage({"role": "user", "content": f"Extract {text}"})],
                    tools=[
                        ChatCompletionsToolDefinition(
                            function=FunctionDefinition(
                                name="Book",
                                description="An extracted book.",
                                parameters={
                                    "properties": {
                                        "title": {"type": "string"},
                                        "author": {"type": "string"},
                                    },
                                    "required": ["title", "author"],
                                    "type": "object",
                                },
                            )
                        )
                    ],
                    tool_choices="required",
                )
                if tool_calls := completion.choices[0].message.tool_calls:
                    return Book.model_validate_json(tool_calls[0].function.arguments)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Bedrock"

        ```python hl_lines="16-48 53"
            import boto3
            from pydantic import BaseModel

            bedrock_client = boto3.client(service_name="bedrock-runtime")


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                messages = [{"role": "user", "content": [{"text": f"Extract {text}"}]}]
                tool_config = {
                    "tools": [
                        {
                            "toolSpec": {
                                "name": "Book",
                                "description": "An extracted book.",
                                "inputSchema": {
                                    "json": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "author": {"type": "string"},
                                        },
                                        "required": ["title", "author"],
                                    }
                                },
                            }
                        }
                    ],
                    "toolChoice": {"type": "tool", "name": "Book"},
                }
                response = bedrock_client.converse(
                    modelId="amazon.nova-lite-v1:0",
                    messages=messages,
                    toolConfig=tool_config,
                )
                output_message = response["output"]["message"]
                messages.append(output_message)
                for content_piece in output_message["content"]:
                    if "toolUse" in content_piece and content_piece["toolUse"].get("input"):
                        tool_input = content_piece["toolUse"]["input"]
                        return Book.model_validate(tool_input)
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```


Notice how Mirascope makes generating structured outputs significantly simpler than the official SDKs. It also greatly reduces boilerplate and standardizes the interaction across all supported LLM providers.

!!! info "Tools By Default"

    By default, `response_model` will use [Tools](./tools.md) under the hood, forcing to the LLM to call that specific tool and constructing the response model from the tool's arguments.

    We default to using tools because all supported providers support tools. You can also optionally set `json_mode=True` to use [JSON Mode](./json_mode.md) instead, which we cover in [more detail below](#json-mode).

### Accessing Original Call Response

Every `response_model` that uses a Pydantic `BaseModel` will automatically have the original `BaseCallResponse` instance accessible through the `_response` property:

!!! mira "Mirascope"

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/basic_usage/bedrock/base_message_param.py

            ```


### Built-In Types

For cases where you want to extract just a single built-in type, Mirascope provides a shorthand:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/builtin_types/bedrock/base_message_param.py

            ```


Here, we are using `list[str]` as the `response_model`, which Mirascope handles without needing to define a full `BaseModel`. You could of course set `response_model=list[Book]` as well.

Note that we have no way of attaching `BaseCallResponse` to built-in types, so using a Pydantic `BaseModel` is recommended if you anticipate needing access to the original call response.

## Supported Field Types

While Mirascope provides a consistent interface, type support varies among providers:

|     Type      | OpenAI | Anthropic | Google | Groq | xAI | Mistral | Cohere |
|---------------|--------|-----------|--------|------|-----|---------|--------|
|     str       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     int       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|    float      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bool      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bytes     |✓✓|✓✓|-✓|✓✓|✓✓|✓✓|✓✓|
|     list      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     set       |✓✓|✓✓|--|✓✓|✓✓|✓✓|✓✓|
|     tuple     |-✓|✓✓|-✓|✓✓|-✓|✓✓|✓✓|
|     dict      |-✓|✓✓|✓✓|✓✓|-✓|✓✓|✓✓|
|  Literal/Enum |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|   BaseModel   |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|-✓|
| Nested ($def) |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|--|

✓✓ : Fully Supported, -✓: Only JSON Mode Support, -- : Not supported

## Validation and Error Handling

While `response_model` significantly improves output structure and validation, it's important to handle potential errors.

Let's take a look at an example where we want to validate that all fields are uppercase:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/base_message_param.py

            ```


Without additional prompt engineering, this call will fail every single time. It's important to engineer your prompts to reduce errors, but LLMs are far from perfect, so always remember to catch and handle validation errors gracefully.

We highly recommend taking a look at our section on [retries](./retries.md) to learn more about automatically retrying and re-inserting validation errors, which enables retrying the call such that the LLM can learn from its previous mistakes.

### Accessing Original Call Response On Error

In case of a `ValidationError`, you can access the original response for debugging:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/shorthand.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/messages.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/string_template.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/base_message_param.py

                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/validation/bedrock/base_message_param.py

            ```


This allows you to gracefully handle errors as well as inspect the original LLM response when validation fails.

## JSON Mode

By default, `response_model` uses [Tools](./tools.md) under the hood. You can instead use [JSON Mode](./json_mode.md) in conjunction with `response_model` by setting `json_mode=True`:

!!! mira ""

    === "Shorthand"

        === "OpenAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/openai/shorthand.py

            ```
        === "Anthropic"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/anthropic/shorthand.py

            ```
        === "Google"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/google/shorthand.py

            ```
        === "Groq"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/groq/shorthand.py

            ```
        === "xAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/xai/shorthand.py

            ```
        === "Mistral"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/mistral/shorthand.py

            ```
        === "Cohere"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/cohere/shorthand.py

            ```
        === "LiteLLM"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/litellm/shorthand.py

            ```
        === "Azure AI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/azure/shorthand.py

            ```
        === "Bedrock"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/openai/messages.py

            ```
        === "Anthropic"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/anthropic/messages.py

            ```
        === "Google"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/google/messages.py

            ```
        === "Groq"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/groq/messages.py

            ```
        === "xAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/xai/messages.py

            ```
        === "Mistral"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/mistral/messages.py

            ```
        === "Cohere"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/cohere/messages.py

            ```
        === "LiteLLM"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/litellm/messages.py

            ```
        === "Azure AI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/azure/messages.py

            ```
        === "Bedrock"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/openai/string_template.py

            ```
        === "Anthropic"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/anthropic/string_template.py

            ```
        === "Google"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/google/string_template.py

            ```
        === "Groq"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/groq/string_template.py

            ```
        === "xAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/xai/string_template.py

            ```
        === "Mistral"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/mistral/string_template.py

            ```
        === "Cohere"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/cohere/string_template.py

            ```
        === "LiteLLM"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/litellm/string_template.py

            ```
        === "Azure AI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/azure/string_template.py

            ```
        === "Bedrock"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/openai/base_message_param.py

            ```
        === "Anthropic"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/anthropic/base_message_param.py

            ```
        === "Google"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/google/base_message_param.py

            ```
        === "Groq"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/groq/base_message_param.py

            ```
        === "xAI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/xai/base_message_param.py

            ```
        === "Mistral"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/mistral/base_message_param.py

            ```
        === "Cohere"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/cohere/base_message_param.py

            ```
        === "LiteLLM"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/litellm/base_message_param.py

            ```
        === "Azure AI"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/azure/base_message_param.py

            ```
        === "Bedrock"
            ```python hl_lines="12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/json_mode/bedrock/base_message_param.py

            ```


## Few-Shot Examples

Adding few-shot examples to your response model can improve results by demonstrating exactly how to adhere to your desired output.

We take advantage of Pydantic's [`Field`](https://docs.pydantic.dev/latest/concepts/fields/) and [`ConfigDict`](https://docs.pydantic.dev/latest/concepts/config/) to add these examples to response models:

!!! mira ""

    === "Shorthand"

        === "OpenAI"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/openai/shorthand.py

            ```
        === "Anthropic"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/anthropic/shorthand.py

            ```
        === "Google"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/google/shorthand.py

            ```
        === "Groq"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/groq/shorthand.py

            ```
        === "xAI"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/xai/shorthand.py

            ```
        === "Mistral"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/mistral/shorthand.py

            ```
        === "Cohere"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/cohere/shorthand.py

            ```
        === "LiteLLM"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/litellm/shorthand.py

            ```
        === "Azure AI"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/azure/shorthand.py

            ```
        === "Bedrock"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/openai/messages.py

            ```
        === "Anthropic"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/anthropic/messages.py

            ```
        === "Google"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/google/messages.py

            ```
        === "Groq"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/groq/messages.py

            ```
        === "xAI"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/xai/messages.py

            ```
        === "Mistral"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/mistral/messages.py

            ```
        === "Cohere"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/cohere/messages.py

            ```
        === "LiteLLM"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/litellm/messages.py

            ```
        === "Azure AI"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/azure/messages.py

            ```
        === "Bedrock"
            ```python hl_lines="6-7 11-13 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/openai/string_template.py

            ```
        === "Anthropic"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/anthropic/string_template.py

            ```
        === "Google"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/google/string_template.py

            ```
        === "Groq"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/groq/string_template.py

            ```
        === "xAI"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/xai/string_template.py

            ```
        === "Mistral"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/mistral/string_template.py

            ```
        === "Cohere"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/cohere/string_template.py

            ```
        === "LiteLLM"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/litellm/string_template.py

            ```
        === "Azure AI"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/azure/string_template.py

            ```
        === "Bedrock"
            ```python hl_lines="6-7 11-13 25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/openai/base_message_param.py

            ```
        === "Anthropic"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/anthropic/base_message_param.py

            ```
        === "Google"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/google/base_message_param.py

            ```
        === "Groq"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/groq/base_message_param.py

            ```
        === "xAI"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/xai/base_message_param.py

            ```
        === "Mistral"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/mistral/base_message_param.py

            ```
        === "Cohere"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/cohere/base_message_param.py

            ```
        === "LiteLLM"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/litellm/base_message_param.py

            ```
        === "Azure AI"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/azure/base_message_param.py

            ```
        === "Bedrock"
            ```python hl_lines="6-7 11-13 30"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/few_shot_examples/bedrock/base_message_param.py

            ```


## Streaming Response Models

If you set `stream=True` when `response_model` is set, your LLM call will return an `Iterable` where each item will be a partial version of your response model representing the current state of the streamed information. The final model returned by the iterator will be the full response model.

!!! mira ""

    === "Shorthand"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/openai/shorthand.py

            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/anthropic/shorthand.py

            ```
        === "Google"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/google/shorthand.py

            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/groq/shorthand.py

            ```
        === "xAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/xai/shorthand.py

            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/mistral/shorthand.py

            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/cohere/shorthand.py

            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/litellm/shorthand.py

            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/azure/shorthand.py

            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/openai/messages.py

            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/anthropic/messages.py

            ```
        === "Google"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/google/messages.py

            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/groq/messages.py

            ```
        === "xAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/xai/messages.py

            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/mistral/messages.py

            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/cohere/messages.py

            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/litellm/messages.py

            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/azure/messages.py

            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/openai/string_template.py

            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/anthropic/string_template.py

            ```
        === "Google"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/google/string_template.py

            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/groq/string_template.py

            ```
        === "xAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/xai/string_template.py

            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/mistral/string_template.py

            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/cohere/string_template.py

            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/litellm/string_template.py

            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/azure/string_template.py

            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/openai/base_message_param.py

            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/anthropic/base_message_param.py

            ```
        === "Google"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/google/base_message_param.py

            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/groq/base_message_param.py

            ```
        === "xAI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/xai/base_message_param.py

            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/mistral/base_message_param.py

            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/cohere/base_message_param.py

            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/litellm/base_message_param.py

            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/azure/base_message_param.py

            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/streaming/bedrock/base_message_param.py

            ```


Once exhausted, you can access the final, full response model through the `constructed_response_model` property of the structured stream. Note that this will also give you access to the [`._response` property](#accessing-original-call-response) that every `BaseModel` receives.

You can also use the `stream` property to access the `BaseStream` instance and [all of it's properties](./streams.md#common-stream-properties-and-methods).

## FromCallArgs

Fields annotated with `FromCallArgs` will be populated with the corresponding argument from the function call rather than expecting it from the LLM's response. This enables seamless validation of LLM outputs against function inputs:

!!! mira "Mirascope"

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="15 27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="15 26"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/response_models/from_call_args/bedrock/base_message_param.py

            ```


## Next Steps

By following these best practices and leveraging Response Models effectively, you can create more robust, type-safe, and maintainable LLM-powered applications with Mirascope.

Next, we recommend taking a lookg at one of:

- [JSON Mode](./json_mode.md) to see an alternate way to generate structured outputs where using Pydantic to validate outputs is optional.
- [Evals](./evals.md) to see how to use `response_model` to evaluate your prompts.
