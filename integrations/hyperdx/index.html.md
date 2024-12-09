# HyperDX

Mirascope provides out-of-the-box integration with [HyperDX](https://www.hyperdx.io/).

You can install the necessary packages directly or using the `hyperdx` extras flag:

```python
pip install "mirascope[hyperdx]"
```

You can then use the `with_hyperdx` decorator to automatically log calls:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call(model="claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book."


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import mistral
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import gemini
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import groq
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import cohere
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import litellm
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import azure
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import vertex
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call(model="claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book."


                print(recommend_book("fantasy"))
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call(model="claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book.")


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, mistral
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, gemini
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, groq
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, cohere
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, litellm
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, azure
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, vertex
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call(model="claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book.")


                print(recommend_book("fantasy"))
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call(model="claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import mistral, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import gemini, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import groq, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import cohere, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import litellm, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import azure, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import prompt_template, vertex
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic, prompt_template
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call(model="claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call(model="claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, anthropic
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, mistral
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, gemini
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, groq
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, cohere
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, litellm
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, azure
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, vertex
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, bedrock
                from mirascope.integrations.otel import with_hyperdx


                @with_hyperdx()
                @bedrock.call(model="claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


                print(recommend_book("fantasy"))
            ```


This decorator is a simple wrapper on top of our [OpenTelemetry integration](./otel.md)
