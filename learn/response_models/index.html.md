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
                from mirascope.core import openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                from mirascope.core import anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"

            ```python hl_lines="12 19"
                from mirascope.core import mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"

            ```python hl_lines="12 19"
                from mirascope.core import gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"

            ```python hl_lines="12 19"
                from mirascope.core import groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"

            ```python hl_lines="12 19"
                from mirascope.core import cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                from mirascope.core import litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                from mirascope.core import azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"

            ```python hl_lines="12 19"
                from mirascope.core import vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                from mirascope.core import bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                from mirascope.core import Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="12 19"
                from mirascope.core import openai, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                from mirascope.core import anthropic, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"

            ```python hl_lines="12 19"
                from mirascope.core import mistral, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"

            ```python hl_lines="12 19"
                from mirascope.core import gemini, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"

            ```python hl_lines="12 19"
                from mirascope.core import groq, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"

            ```python hl_lines="12 19"
                from mirascope.core import cohere, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                from mirascope.core import litellm, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                from mirascope.core import azure, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"

            ```python hl_lines="12 19"
                from mirascope.core import prompt_template, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                from mirascope.core import bedrock, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"

            ```python hl_lines="12 19"
                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
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
                    model="claude-3-5-sonnet-20240620",
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

    === "Gemini"

        ```python hl_lines="19-57 62"
            from google.generativeai import GenerativeModel
            from google.generativeai.types import FunctionDeclaration, Tool, content_types
            from proto.marshal.collections import RepeatedComposite
            from pydantic import BaseModel

            model = GenerativeModel("gemini-1.5-flash")


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                response = model.generate_content(
                    f"Extract {text}",
                    tools=[
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
                    tool_config=content_types.to_tool_config(
                        {
                            "function_calling_config": {
                                "mode": "any",
                                "allowed_function_names": ["Book"],
                            }
                        }  # pyright: ignore [reportArgumentType]
                    ),
                )
                if tool_calls := [
                    part.function_call for part in response.parts if part.function_call.args
                ]:
                    return Book.model_validate(
                        {
                            k: v if not isinstance(v, RepeatedComposite) else list(v)
                            for k, v in tool_calls[0].args.items()
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
                    model="llama-3.1-70b-versatile",
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

    === "Vertex AI"

        ```python hl_lines="23-62 67"
            from proto.marshal.collections import RepeatedComposite
            from pydantic import BaseModel
            from vertexai.generative_models import (
                FunctionDeclaration,
                GenerativeModel,
                Tool,
                ToolConfig,
            )

            model = GenerativeModel("gemini-1.5-flash")


            class Book(BaseModel):
                """An extracted book."""

                title: str
                author: str


            def extract_book(text: str) -> Book:
                response = model.generate_content(
                    f"Extract {text}",
                    tools=[
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
                    tool_config=ToolConfig(
                        function_calling_config=ToolConfig.FunctionCallingConfig(
                            mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
                            allowed_function_names=["Book"],
                        ),
                    ),
                )
                if tool_calls := [
                    part.function_call
                    for candidate in response.candidates  # pyright: ignore [reportAttributeAccessIssue]
                    for part in candidate.content.parts
                    if part.function_call.args
                ]:
                    return Book.model_validate(
                        {
                            k: v if not isinstance(v, RepeatedComposite) else list(v)
                            for k, v in tool_calls[0].args.items()
                        }
                    )
                raise ValueError("No tool call found")


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```

    === "Bedrock"

        ```python hl_lines="18-39 44"
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
                    modelId="anthropic.claude-3-haiku-20240307-v1:0",
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
                from typing import cast

                from mirascope.core import openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(openai.OpenAICallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(anthropic.AnthropicCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(mistral.MistralCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(gemini.GeminiCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(groq.GroqCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(cohere.CohereCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(litellm.LiteLLMCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(azure.AzureCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(vertex.VertexCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(bedrock.BedrockCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(openai.OpenAICallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(anthropic.AnthropicCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(mistral.MistralCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(gemini.GeminiCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(groq.GroqCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(cohere.CohereCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(litellm.LiteLLMCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(azure.AzureCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(vertex.VertexCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(bedrock.BedrockCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import openai, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(openai.OpenAICallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import anthropic, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(anthropic.AnthropicCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import mistral, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(mistral.MistralCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import gemini, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(gemini.GeminiCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import groq, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(groq.GroqCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import cohere, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(cohere.CohereCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import litellm, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(litellm.LiteLLMCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import azure, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(azure.AzureCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import prompt_template, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(vertex.VertexCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import bedrock, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(bedrock.BedrockCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(openai.OpenAICallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(anthropic.AnthropicCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(mistral.MistralCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(gemini.GeminiCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(groq.GroqCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(cohere.CohereCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(litellm.LiteLLMCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(azure.AzureCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(vertex.VertexCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="1 23-25"
                from typing import cast

                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'

                response = cast(bedrock.BedrockCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
                print(response.model_dump())
                # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```


### Built-In Types

For cases where you want to extract just a single built-in type, Mirascope provides a shorthand:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 16"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Mistral"

            ```python hl_lines="4 16"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Gemini"

            ```python hl_lines="4 16"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Groq"

            ```python hl_lines="4 16"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Cohere"

            ```python hl_lines="4 16"
                from mirascope.core import cohere


                @cohere.call("command-r-plus", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Vertex AI"

            ```python hl_lines="4 16"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=list[str])
                def extract_book(texts: list[str]) -> str:
                    return f"Extract book titles from {texts}"


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Mistral"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Gemini"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Groq"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Cohere"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Vertex AI"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=list[str])
                def extract_book(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract book titles from {texts}")


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 16"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Mistral"

            ```python hl_lines="4 16"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Gemini"

            ```python hl_lines="4 16"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Groq"

            ```python hl_lines="4 16"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Cohere"

            ```python hl_lines="4 16"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Vertex AI"

            ```python hl_lines="4 16"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=list[str])
                @prompt_template("Extract book titles from {texts}")
                def extract_book(texts: list[str]): ...


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Anthropic"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Mistral"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Gemini"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Groq"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Cohere"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "LiteLLM"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Azure AI"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Vertex AI"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```
        === "Bedrock"

            ```python hl_lines="4 16"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=list[str])
                def extract_book(texts: list[str]) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract book titles from {texts}")]


                book = extract_book(
                    [
                        "The Name of the Wind by Patrick Rothfuss",
                        "Mistborn: The Final Empire by Brandon Sanderson",
                    ]
                )
                print(book)
                # Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
            ```


Here, we are using `list[str]` as the `response_model`, which Mirascope handles without needing to define a full `BaseModel`. You could of course set `response_model=list[Book]` as well.

Note that we have no way of attaching `BaseCallResponse` to built-in types, so using a Pydantic `BaseModel` is recommended if you anticipate needing access to the original call response.

## Supported Field Types

While Mirascope provides a consistent interface, type support varies among providers:

|     Type      | Anthropic | Cohere | Gemini | Groq | Mistral | OpenAI |
|---------------|-----------|--------|--------|------|---------|--------|
|     str       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     int       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|    float      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bool      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bytes     |✓✓|✓✓|-✓|✓✓|✓✓|✓✓|
|     list      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     set       |✓✓|✓✓|--|✓✓|✓✓|✓✓|
|     tuple     |✓✓|✓✓|-✓|✓✓|✓✓|-✓|
|     dict      |✓✓|✓✓|✓✓|✓✓|✓✓|-✓|
|  Literal/Enum |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|   BaseModel   |✓✓|-✓|✓✓|✓✓|✓✓|✓✓|
| Nested ($def) |✓✓|--|--|✓✓|✓✓|✓✓|

✓✓ : Fully Supported, -✓: Only JSON Mode Support, -- : Not supported

## Validation and Error Handling

While `response_model` significantly improves output structure and validation, it's important to handle potential errors.

Let's take a look at an example where we want to validate that all fields are uppercase:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import openai
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import anthropic
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import mistral
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Gemini"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import gemini
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import groq
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import cohere
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import litellm
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import azure
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Vertex AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import bedrock
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, openai
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, anthropic
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, mistral
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Gemini"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, gemini
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, groq
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, cohere
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, litellm
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, azure
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Vertex AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import Messages, bedrock
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import openai, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import anthropic, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import mistral, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Gemini"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import gemini, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import groq, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import cohere, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import litellm, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import azure, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Vertex AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import prompt_template, vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import bedrock, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, openai
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Anthropic"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Mistral"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, mistral
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Gemini"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, gemini
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Groq"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, groq
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Cohere"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, cohere
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "LiteLLM"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, litellm
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Azure AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, azure
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Vertex AI"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```
        === "Bedrock"

            ```python hl_lines="1 4 7-9 15-16 24 28"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    print(f"Error: {str(e)}")
                    # Error: 2 validation errors for Book
                    # title
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
                    # author
                    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
            ```


Without additional prompt engineering, this call will fail every single time. It's important to engineer your prompts to reduce errors, but LLMs are far from perfect, so always remember to catch and handle validation errors gracefully.

We highly recommend taking a look at our section on [retries](./retries.md) to learn more about automatically retrying and re-inserting validation errors, which enables retrying the call such that the LLM can learn from its previous mistakes.

### Accessing Original Call Response On Error

In case of a `ValidationError`, you can access the original response for debugging:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import openai
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(openai.OpenAICallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import anthropic
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(anthropic.AnthropicCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import mistral
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(mistral.MistralCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import gemini
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(gemini.GeminiCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import groq
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(groq.GroqCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import cohere
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(cohere.CohereCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import litellm
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(litellm.LiteLLMCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import azure
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(azure.AzureCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(vertex.VertexCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import bedrock
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(bedrock.BedrockCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, openai
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(openai.OpenAICallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, anthropic
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(anthropic.AnthropicCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, mistral
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(mistral.MistralCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, gemini
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(gemini.GeminiCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, groq
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(groq.GroqCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, cohere
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(cohere.CohereCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, litellm
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(litellm.LiteLLMCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, azure
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(azure.AzureCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(vertex.VertexCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import Messages, bedrock
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(bedrock.BedrockCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import openai, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(openai.OpenAICallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import anthropic, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(anthropic.AnthropicCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import mistral, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(mistral.MistralCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import gemini, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(gemini.GeminiCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import groq, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(groq.GroqCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import cohere, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(cohere.CohereCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import litellm, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(litellm.LiteLLMCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import azure, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(azure.AzureCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import prompt_template, vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(vertex.VertexCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import bedrock, prompt_template
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(bedrock.BedrockCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, openai
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @openai.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(openai.OpenAICallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Anthropic"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(anthropic.AnthropicCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Mistral"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, mistral
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @mistral.call("mistral-large-latest", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(mistral.MistralCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Gemini"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, gemini
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @gemini.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(gemini.GeminiCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Groq"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, groq
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(groq.GroqCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Cohere"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, cohere
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @cohere.call("command-r-plus", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(cohere.CohereCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "LiteLLM"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, litellm
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @litellm.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(litellm.LiteLLMCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Azure AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, azure
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @azure.call("gpt-4o-mini", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(azure.AzureCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Vertex AI"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, vertex
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @vertex.call("gemini-1.5-flash", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(vertex.VertexCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```
        === "Bedrock"

            ```python hl_lines="28-31"
                from typing import Annotated, cast

                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import AfterValidator, BaseModel, ValidationError


                def validate_upper(v: str) -> str:
                    assert v.isupper(), "Field must be uppercase"
                    return v


                class Book(BaseModel):
                    """An extracted book."""

                    title: Annotated[str, AfterValidator(validate_upper)]
                    author: Annotated[str, AfterValidator(validate_upper)]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                try:
                    book = extract_book("The Name of the Wind by Patrick Rothfuss")
                    print(book)
                    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
                except ValidationError as e:
                    response = cast(bedrock.BedrockCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
                    print(response.model_dump())
                    # > {'metadata': {}, 'response': {'id': ...}, ...}
            ```


This allows you to gracefully handle errors as well as inspect the original LLM response when validation fails.

## JSON Mode

By default, `response_model` uses [Tools](./tools.md) under the hood. You can instead use [JSON Mode](./json_mode.md) in conjunction with `response_model` by setting `json_mode=True`:

!!! mira ""

    === "Shorthand"

        === "OpenAI"
            ```python hl_lines="12"
                from mirascope.core import openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="12"
                from mirascope.core import anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="12"
                from mirascope.core import mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="12"
                from mirascope.core import gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="12"
                from mirascope.core import groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="12"
                from mirascope.core import cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="12"
                from mirascope.core import litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="12"
                from mirascope.core import azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="12"
                from mirascope.core import vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="13"
                from mirascope.core import bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "Messages"

        === "OpenAI"
            ```python hl_lines="12"
                from mirascope.core import Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="12"
                from mirascope.core import Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="12"
                from mirascope.core import Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="12"
                from mirascope.core import Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="12"
                from mirascope.core import Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="12"
                from mirascope.core import Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="12"
                from mirascope.core import Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="12"
                from mirascope.core import Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="12"
                from mirascope.core import Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="13"
                from mirascope.core import Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "String Template"

        === "OpenAI"
            ```python hl_lines="12"
                from mirascope.core import openai, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="12"
                from mirascope.core import anthropic, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="12"
                from mirascope.core import mistral, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="12"
                from mirascope.core import gemini, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="12"
                from mirascope.core import groq, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="12"
                from mirascope.core import cohere, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="12"
                from mirascope.core import litellm, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="12"
                from mirascope.core import azure, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="12"
                from mirascope.core import prompt_template, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="13"
                from mirascope.core import bedrock, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "BaseMessageParam"

        === "OpenAI"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="12"
                from mirascope.core import BaseMessageParam, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    """An extracted book."""

                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book = extract_book("The Name of the Wind by Patrick Rothfuss")
                print(book)
                # Output: title='The Name of the Wind' author='Patrick Rothfuss'
            ```


## Few-Shot Examples

Adding few-shot examples to your response model can improve results by demonstrating exactly how to adhere to your desired output.

We take advantage of Pydantic's [`Field`](https://docs.pydantic.dev/latest/concepts/fields/) and [`ConfigDict`](https://docs.pydantic.dev/latest/concepts/config/) to add these examples to response models:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import openai
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Anthropic"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import anthropic
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Mistral"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import mistral
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Gemini"

            ```python
                # Not supported
            ```
        === "Groq"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import groq
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Cohere"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import cohere
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "LiteLLM"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import litellm
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Azure AI"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import azure
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Vertex AI"

            ```python
                # Not supported
            ```
        === "Bedrock"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import bedrock
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                def extract_book(text: str) -> str:
                    return f"Extract {text}. Match example format excluding 'examples' key."


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, openai
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Anthropic"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, anthropic
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Mistral"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, mistral
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Gemini"

            ```python
                # Not supported
            ```
        === "Groq"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, groq
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Cohere"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, cohere
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "LiteLLM"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, litellm
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Azure AI"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, azure
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Vertex AI"

            ```python
                # Not supported
            ```
        === "Bedrock"

            ```python hl_lines="6-7 11-13 27"
                from mirascope.core import Messages, bedrock
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(
                        f"Extract {text}. Match example format excluding 'examples' key."
                    )


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import openai, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Anthropic"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import anthropic, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Mistral"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import mistral, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Gemini"

            ```python
                # Not supported
            ```
        === "Groq"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import groq, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Cohere"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import cohere, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "LiteLLM"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import litellm, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Azure AI"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import azure, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Vertex AI"

            ```python
                # Not supported
            ```
        === "Bedrock"

            ```python hl_lines="6-7 11-13 25"
                from mirascope.core import bedrock, prompt_template
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                @prompt_template("Extract {text}. Match example format excluding 'examples' key.")
                def extract_book(text: str): ...


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, openai
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Anthropic"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Mistral"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, mistral
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @mistral.call("mistral-large-latest", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Gemini"

            ```python
                # Not supported
            ```
        === "Groq"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, groq
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @groq.call("llama-3.1-70b-versatile", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Cohere"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, cohere
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @cohere.call("command-r-plus", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "LiteLLM"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, litellm
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Azure AI"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, azure
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @azure.call("gpt-4o-mini", response_model=Book, json_mode=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```
        === "Vertex AI"

            ```python
                # Not supported
            ```
        === "Bedrock"

            ```python hl_lines="6-7 11-13 30"
                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import BaseModel, ConfigDict, Field


                class Book(BaseModel):
                    title: str = Field(..., examples=["THE NAME OF THE WIND"])
                    author: str = Field(..., examples=["Rothfuss, Patrick"])

                    model_config = ConfigDict(
                        json_schema_extra={
                            "examples": [
                                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
                            ]
                        }
                    )


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
                )
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Extract {text}. Match example format excluding 'examples' key.",
                        )
                    ]


                book = extract_book("The Way of Kings by Brandon Sanderson")
                print(book)
                # Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
            ```


## Streaming Response Models

If you set `stream=True` when `response_model` is set, your LLM call will return an `Iterable` where each item will be a partial version of your response model representing the current state of the streamed information. The final model returned by the iterator will be the full response model.

!!! mira ""

    === "Shorthand"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                from mirascope.core import openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                from mirascope.core import anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                from mirascope.core import mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="10 16-17"
                from mirascope.core import gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                from mirascope.core import groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                from mirascope.core import cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                from mirascope.core import litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, stream=True)
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                from mirascope.core import bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, stream=True
                )
                def extract_book(text: str) -> str:
                    return f"Extract {text}"


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "Messages"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, stream=True)
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                from mirascope.core import Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, stream=True
                )
                def extract_book(text: str) -> Messages.Type:
                    return Messages.User(f"Extract {text}")


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "String Template"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                from mirascope.core import openai, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                from mirascope.core import anthropic, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                from mirascope.core import mistral, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="10 16-17"
                from mirascope.core import gemini, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                from mirascope.core import groq, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                from mirascope.core import cohere, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                from mirascope.core import litellm, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import azure, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import prompt_template, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, stream=True)
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                from mirascope.core import bedrock, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, stream=True
                )
                @prompt_template("Extract {text}")
                def extract_book(text: str): ...


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```

    === "BaseMessageParam"

        === "OpenAI"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @openai.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Anthropic"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Mistral"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @mistral.call("mistral-large-latest", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Gemini"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @gemini.call("gemini-1.5-flash", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Groq"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @groq.call("llama-3.1-70b-versatile", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Cohere"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @cohere.call("command-r-plus", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "LiteLLM"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @litellm.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Azure AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @azure.call("gpt-4o-mini", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Vertex AI"
            ```python hl_lines="10 16-17"
                from mirascope.core import BaseMessageParam, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @vertex.call("gemini-1.5-flash", response_model=Book, stream=True)
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```
        === "Bedrock"
            ```python hl_lines="11 18-19"
                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, stream=True
                )
                def extract_book(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Extract {text}")]


                book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
                for partial_book in book_stream:
                    print(partial_book)
                # Output:
                # title=None author=None
                # title='' author=None
                # title='The' author=None
                # title='The Name' author=None
                # title='The Name of' author=None
                # title='The Name of the' author=None
                # title='The Name of the Wind' author=None
                # title='The Name of the Wind' author=''
                # title='The Name of the Wind' author='Patrick'
                # title='The Name of the Wind' author='Patrick Roth'
                # title='The Name of the Wind' author='Patrick Rothf'
                # title='The Name of the Wind' author='Patrick Rothfuss'
            ```


Once exhausted, you can access the final, full response model through the `constructed_response_model` property of the structured stream. Note that this will also give you access to the [`._response` property](#accessing-original-call-response) that every `BaseModel` receives.

You can also use the `stream` property to access the `BaseStream` instance and [all of it's properties](./streams.md#common-stream-properties-and-methods).

## FromCallArgs

Fields annotated with `FromCallArgs` will be populated with the corresponding argument from the function call rather than expecting it from the LLM's response. This enables seamless validation of LLM outputs against function inputs:

!!! mira "Mirascope"

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, openai
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @openai.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Anthropic"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, anthropic
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Mistral"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, mistral
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @mistral.call("mistral-large-latest", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Gemini"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, gemini
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @gemini.call("gemini-1.5-flash", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Groq"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, groq
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @groq.call("llama-3.1-70b-versatile", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Cohere"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, cohere
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @cohere.call("command-r-plus", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "LiteLLM"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, litellm
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @litellm.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Azure AI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, azure
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @azure.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Vertex AI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, vertex
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @vertex.call("gemini-1.5-flash", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Bedrock"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, bedrock
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Books)
                def extract_books(texts: list[str]) -> str:
                    return f"Extract the books from these texts: {texts}"


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, openai
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @openai.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Anthropic"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, anthropic
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Mistral"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, mistral
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @mistral.call("mistral-large-latest", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Gemini"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, gemini
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @gemini.call("gemini-1.5-flash", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Groq"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, groq
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @groq.call("llama-3.1-70b-versatile", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Cohere"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, cohere
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @cohere.call("command-r-plus", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "LiteLLM"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, litellm
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @litellm.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Azure AI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, azure
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @azure.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Vertex AI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, vertex
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @vertex.call("gemini-1.5-flash", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Bedrock"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import FromCallArgs, Messages, bedrock
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Books)
                def extract_books(texts: list[str]) -> Messages.Type:
                    return Messages.User(f"Extract the books from these texts: {texts}")


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, openai, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @openai.call("gpt-4o-mini", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Anthropic"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, anthropic, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Mistral"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, mistral, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @mistral.call("mistral-large-latest", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Gemini"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, gemini, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @gemini.call("gemini-1.5-flash", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Groq"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, groq, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @groq.call("llama-3.1-70b-versatile", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Cohere"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, cohere, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @cohere.call("command-r-plus", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "LiteLLM"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, litellm, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @litellm.call("gpt-4o-mini", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Azure AI"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, azure, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @azure.call("gpt-4o-mini", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Vertex AI"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, prompt_template, vertex
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @vertex.call("gemini-1.5-flash", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Bedrock"

            ```python hl_lines="14 26"
                from typing import Annotated

                from mirascope.core import FromCallArgs, bedrock, prompt_template
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Books)
                @prompt_template("Extract the books from these texts: {texts}")
                def extract_books(texts: list[str]): ...


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, openai
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @openai.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Anthropic"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, anthropic
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Mistral"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, mistral
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @mistral.call("mistral-large-latest", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Gemini"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, gemini
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @gemini.call("gemini-1.5-flash", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Groq"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, groq
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @groq.call("llama-3.1-70b-versatile", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Cohere"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, cohere
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @cohere.call("command-r-plus", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "LiteLLM"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, litellm
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @litellm.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Azure AI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, azure
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @azure.call("gpt-4o-mini", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Vertex AI"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, vertex
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @vertex.call("gemini-1.5-flash", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```
        === "Bedrock"

            ```python hl_lines="14 25"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, FromCallArgs, bedrock
                from pydantic import BaseModel, model_validator
                from typing_extensions import Self


                class Book(BaseModel):
                    title: str
                    author: str


                class Books(BaseModel):
                    texts: Annotated[list[str], FromCallArgs()]
                    books: list[Book]

                    @model_validator(mode="after")
                    def validate_output_length(self) -> Self:
                        if len(self.texts) != len(self.books):
                            raise ValueError("length mismatch...")
                        return self


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Books)
                def extract_books(texts: list[str]) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Extract the books from these texts: {texts}"
                        )
                    ]


                texts = [
                    "The Name of the Wind by Patrick Rothfuss",
                    "Mistborn: The Final Empire by Brandon Sanderson",
                ]
                print(extract_books(texts))
                # Output: texts=['The Name of the Wind by Patrick Rothfuss', 'Mistborn: The Final Empire by Brandon Sanderson'] books=[Book(title='The Name of the Wind', author='Patrick Rothfuss'), Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')]
            ```


## Next Steps

By following these best practices and leveraging Response Models effectively, you can create more robust, type-safe, and maintainable LLM-powered applications with Mirascope.

Next, we recommend taking a lookg at one of:

- [JSON Mode](./json_mode.md) to see an alternate way to generate structured outputs where using Pydantic to validate outputs is optional.
- [Evals](./evals.md) to see how to use `response_model` to evaluate your prompts.
