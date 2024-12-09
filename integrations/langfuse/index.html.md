# Langfuse

Mirascope provides out-of-the-box integration with [Langfuse](https://langfuse.com/).

You can install the necessary packages directly or using the `langfuse` extras flag:

```python
pip install "mirascope[langfuse]"
```

You can then use the `with_langfuse` decorator to automatically log calls:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book."


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import mistral
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import gemini
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import groq
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import cohere
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import litellm
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import azure
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import vertex
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import bedrock
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book."


                print(recommend_book("fantasy"))
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, openai
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book.")


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, anthropic
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, mistral
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, gemini
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, groq
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, cohere
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, litellm
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, azure
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, vertex
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, bedrock
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book.")


                print(recommend_book("fantasy"))
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import anthropic, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import mistral, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import gemini, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import groq, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import cohere, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import litellm, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import azure, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import prompt_template, vertex
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import bedrock, prompt_template
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, openai
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, anthropic
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, mistral
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, gemini
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @gemini.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, groq
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, cohere
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, litellm
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, azure
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, vertex
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @vertex.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, bedrock
                from mirascope.integrations.langfuse import with_langfuse


                @with_langfuse()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


                print(recommend_book("fantasy"))
            ```


This will give you:

* A trace around the `recommend_book` function that captures items like the prompt template, and input/output attributes and more.
* Human-readable display of the conversation with the agent
* Details of the response, including the number of tokens used

??? info "Example trace"

    ![logfire-call](../assets/langfuse-call.png)

??? note "Handling streams"

    When logging streams, the span will not be logged until the stream has been exhausted. This is a function of how streaming works.

    You will also need to set certain `call_params` for usage to be tracked for certain providers (such as OpenAI).
