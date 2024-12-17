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

    For providers with explicit support, Mirascope uses the native JSON Mode feature of the API. For providers without explicit support (Anthropic and Cohere), Mirascope implements a pseudo JSON Mode by instructing the model in the prompt to output JSON.

    | Provider  | Support Type | Implementation      |
    |-----------|--------------|---------------------|
    | OpenAI    | Explicit     | Native API feature  |
    | Anthropic | Pseudo       | Prompt engineering  |
    | Mistral   | Explicit     | Native API feature  |
    | Gemini    | Explicit     | Native API feature  |
    | Groq      | Explicit     | Native API feature  |
    | Cohere    | Pseudo       | Prompt engineering  |

    If you'd prefer not to have any internal updates made to your prompt, you can always set JSON mode yourself through `call_params` rather than using the `json_mode` argument, which provides provider-agnostic support but is certainly not required to use JSON mode.

## Basic Usage and Syntax

Let's take a look at a basic example using JSON Mode:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import openai


                @openai.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Anthropic"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Mistral"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Gemini"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Groq"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Cohere"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import cohere


                @cohere.call("command-r-plus", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "LiteLLM"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Azure AI"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import azure


                @azure.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Vertex AI"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Bedrock"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Anthropic"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Mistral"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Gemini"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Groq"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Cohere"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "LiteLLM"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Azure AI"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Vertex AI"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Bedrock"

            ```python hl_lines="6 8 13"
                import json

                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Anthropic"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Mistral"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Gemini"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Groq"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Cohere"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "LiteLLM"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Azure AI"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Vertex AI"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Bedrock"

            ```python hl_lines="6 7 13"
                import json

                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Anthropic"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Mistral"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Gemini"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Groq"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Cohere"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "LiteLLM"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Azure AI"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Vertex AI"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
            ```
        === "Bedrock"

            ```python hl_lines="6 10 17"
                import json

                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                response = get_book_info("The Name of the Wind")
                print(json.loads(response.content))
                # Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
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
                import json

                from mirascope.core import openai


                @openai.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Anthropic"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Mistral"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Gemini"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Groq"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Cohere"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import cohere


                @cohere.call("command-r-plus", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "LiteLLM"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Azure AI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import azure


                @azure.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Vertex AI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Bedrock"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                def get_book_info(book_title: str) -> str:
                    return f"Provide the author and genre of {book_title}"


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Anthropic"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Mistral"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Gemini"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Groq"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Cohere"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "LiteLLM"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Azure AI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Vertex AI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Bedrock"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                def get_book_info(book_title: str) -> Messages.Type:
                    return Messages.User(f"Provide the author and genre of {book_title}")


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Anthropic"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Mistral"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Gemini"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Groq"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Cohere"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "LiteLLM"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Azure AI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Vertex AI"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Bedrock"

            ```python hl_lines="11 14"
                import json

                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                @prompt_template("Provide the author and genre of {book_title}")
                def get_book_info(book_title: str): ...


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Anthropic"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Mistral"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Gemini"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Groq"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Cohere"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "LiteLLM"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Azure AI"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Vertex AI"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```
        === "Bedrock"

            ```python hl_lines="15 18"
                import json

                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
                def get_book_info(book_title: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user", content=f"Provide the author and genre of {book_title}"
                        )
                    ]


                try:
                    response = get_book_info("The Name of the Wind")
                    print(json.loads(response.content))
                except json.JSONDecodeError:
                    print("The model produced invalid JSON")
            ```


!!! warning "Beyond JSON Validation"

    While this example catches errors for invalid JSON, there's always a chance that the LLM returns valid JSON that doesn't conform to your expected schema (such as missing fields or incorrect types).

    For more robust validation, we recommend using [Response Models](./response_models.md) for easier structuring and validation of LLM outputs.

## Next Steps

By leveraging JSON Mode, you can create more robust and data-driven applications that efficiently process and utilize LLM outputs. This approach allows for easy integration with databases, APIs, or user interfaces, demonstrating the power of JSON Mode in creating robust, data-driven applications.

Next, we recommend reading the section on [Output Parsers](./output_parsers.md) to see how to engineer prompts with specific output structures and parse the outputs automatically on every call.
