# Logfire

[Logfire](https://docs.pydantic.dev/logfire/), a new tool from Pydantic, is built on OpenTelemetry. Since Pydantic powers many of Mirascope's features, it's appropriate for us to ensure seamless integration with them.

You can install the necessary packages directly or using the `logfire` extras flag:

```python
pip install "mirascope[logfire]"
```

You can then use the `with_logfire` decorator to automatically log calls:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import openai
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @openai.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book."


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import anthropic
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import mistral
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @mistral.call("mistral-large-latest", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import gemini
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @gemini.call("gemini-1.5-flash", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import groq
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import cohere
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @cohere.call("command-r-plus", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import litellm
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @litellm.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import azure
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @azure.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import vertex
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @vertex.call("gemini-1.5-flash", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import bedrock
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book."


                print(recommend_book("fantasy"))
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, openai
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @openai.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book.")


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, anthropic
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, mistral
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @mistral.call("mistral-large-latest", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, gemini
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @gemini.call("gemini-1.5-flash", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, groq
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, cohere
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @cohere.call("command-r-plus", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, litellm
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @litellm.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, azure
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @azure.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, vertex
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @vertex.call("gemini-1.5-flash", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import Messages, bedrock
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book.")


                print(recommend_book("fantasy"))
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import openai, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @openai.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import anthropic, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import mistral, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @mistral.call("mistral-large-latest", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import gemini, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @gemini.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import groq, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import cohere, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @cohere.call("command-r-plus", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import litellm, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @litellm.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import azure, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @azure.call("gpt-4o-mini", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import prompt_template, vertex
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @vertex.call("gemini-1.5-flash", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import bedrock, prompt_template
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, openai
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @openai.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, anthropic
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, mistral
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @mistral.call("mistral-large-latest", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Gemini"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, gemini
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @gemini.call("gemini-1.5-flash", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, groq
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @groq.call("llama-3.1-70b-versatile", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, cohere
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @cohere.call("command-r-plus", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, litellm
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @litellm.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, azure
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @azure.call("gpt-4o-mini", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Vertex AI"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, vertex
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @vertex.call("gemini-1.5-flash", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="1 3 6 14"
                import logfire
                from mirascope.core import BaseMessageParam, bedrock
                from mirascope.integrations.logfire import with_logfire
                from pydantic import BaseModel

                logfire.configure()


                class Book(BaseModel):
                    title: str
                    author: str


                @with_logfire()
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


                print(recommend_book("fantasy"))
            ```


This will give you:

* A span called `recommend_book` that captures items like the prompt template, templating properties and fields, and input/output attributes
* Human-readable display of the conversation with the agent
* Details of the response, including the number of tokens used

??? info "Example log"

    ![logfire-call](../assets/logfire-response-model.png)

??? note "Handling streams"

    When logging streams, the span will not be logged until the stream has been exhausted. This is a function of how streaming works.

    You will also need to set certain `call_params` for usage to be tracked for certain providers (such as OpenAI).
