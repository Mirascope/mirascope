---
search:
  boost: 2
---

# Async

Asynchronous programming is a crucial concept when building applications with LLMs (Large Language Models) using Mirascope. This feature allows for efficient handling of I/O-bound operations (e.g., API calls), improving application responsiveness and scalability. Mirascope utilizes the [asyncio](https://docs.python.org/3/library/asyncio.html) library to implement asynchronous processing.

!!! tip "Best Practices"

    - **Use asyncio for I/O-bound tasks**: Async is most beneficial for I/O-bound operations like API calls. It may not provide significant benefits for CPU-bound tasks.
    - **Avoid blocking operations**: Ensure that you're not using blocking operations within async functions, as this can negate the benefits of asynchronous programming.
    - **Consider using connection pools**: When making many async requests, consider using connection pools to manage and reuse connections efficiently.
    - **Be mindful of rate limits**: While async allows for concurrent requests, be aware of API rate limits and implement appropriate throttling if necessary.
    - **Use appropriate timeouts**: Implement timeouts for async operations to prevent hanging in case of network issues or unresponsive services.
    - **Test thoroughly**: Async code can introduce subtle bugs. Ensure comprehensive testing of your async implementations.
    - **Leverage async context managers**: Use async context managers (async with) for managing resources that require setup and cleanup in async contexts.

??? info "Diagram illustrating the flow of asynchronous processing"

    ```mermaid
    sequenceDiagram
        participant Main as Main Process
        participant API1 as API Call 1
        participant API2 as API Call 2
        participant API3 as API Call 3

        Main->>+API1: Send Request
        Main->>+API2: Send Request
        Main->>+API3: Send Request
        API1-->>-Main: Response
        API2-->>-Main: Response
        API3-->>-Main: Response
        Main->>Main: Process All Responses
    ```

## Key Terms

- `async`: Keyword used to define a function as asynchronous
- `await`: Keyword used to wait for the completion of an asynchronous operation
- `asyncio`: Python library that supports asynchronous programming

## Basic Usage and Syntax

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

To use async in Mirascope, simply define the function as async and use the `await` keyword when calling it. Here's a basic example:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import openai


                @openai.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import litellm


                @litellm.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import azure


                @azure.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, openai


                @openai.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, litellm


                @litellm.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, azure


                @azure.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import Messages, bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import openai, prompt_template


                @openai.call(model="gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import litellm, prompt_template


                @litellm.call(model="gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import azure, prompt_template


                @azure.call(model="gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="8 12"
                import asyncio

                from mirascope.core import bedrock, prompt_template


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, openai


                @openai.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, litellm


                @litellm.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, azure


                @azure.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="7 12"
                import asyncio

                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    print(response.content)


                asyncio.run(main())
            ```


In this example we:

1. Define `recommend_book` as an asynchronous function.
2. Create a `main` function that calls `recommend_book` and awaits it.
3. Use `asyncio.run(main())` to start the asynchronous event loop and run the main function.

## Parallel Async Calls

One of the main benefits of asynchronous programming is the ability to run multiple operations concurrently. Here's an example of making parallel async calls:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import openai


                @openai.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import litellm


                @litellm.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import azure


                @azure.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, openai


                @openai.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, litellm


                @litellm.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, azure


                @azure.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import Messages, bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import openai, prompt_template


                @openai.call(model="gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import litellm, prompt_template


                @litellm.call(model="gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import azure, prompt_template


                @azure.call(model="gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="8 13-14"
                import asyncio

                from mirascope.core import bedrock, prompt_template


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, openai


                @openai.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, litellm


                @litellm.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, azure


                @azure.call(model="gpt-4o-mini")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="7 13-14"
                import asyncio

                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    genres = ["fantasy", "scifi", "mystery"]
                    tasks = [recommend_book(genre) for genre in genres]
                    results = await asyncio.gather(*tasks)

                    for genre, response in zip(genres, results):
                        print(f"({genre}):\n{response.content}\n")


                asyncio.run(main())
            ```


We are using `asyncio.gather` to run and await multiple asynchronous tasks concurrently, printing the results for each task one all are completed.

## Async Streaming

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Streams](./streams.md)
    </div>

Streaming with async works similarly to synchronous streaming, but you use `async for` instead of a regular `for` loop:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import openai


                @openai.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import cohere


                @cohere.call("command-r-plus", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import litellm


                @litellm.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import azure


                @azure.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, openai


                @openai.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, litellm


                @litellm.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, azure


                @azure.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import Messages, bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import openai, prompt_template


                @openai.call(model="gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import litellm, prompt_template


                @litellm.call(model="gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import azure, prompt_template


                @azure.call(model="gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="6 8 12-13"
                import asyncio

                from mirascope.core import bedrock, prompt_template


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, openai


                @openai.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, litellm


                @litellm.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, azure


                @azure.call(model="gpt-4o-mini", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="6 7 12-13"
                import asyncio

                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    stream = await recommend_book("fantasy")
                    async for chunk, _ in stream:
                        print(chunk.content, end="", flush=True)


                asyncio.run(main())
            ```


## Async Tools

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Tools](./tools.md)
    </div>

When using tools asynchronously, you can make the `call` method of a tool async:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, openai


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @openai.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, anthropic


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, mistral


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @mistral.call("mistral-large-latest", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, gemini


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @gemini.call("gemini-1.5-flash", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, groq


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @groq.call("llama-3.1-70b-versatile", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, cohere


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @cohere.call("command-r-plus", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, litellm


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @litellm.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, azure


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @azure.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, vertex


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @vertex.call("gemini-1.5-flash", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, bedrock


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", tools=[FormatBook])
                async def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, openai


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @openai.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, anthropic


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, mistral


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @mistral.call("mistral-large-latest", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, gemini


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @gemini.call("gemini-1.5-flash", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, groq


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @groq.call("llama-3.1-70b-versatile", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, cohere


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @cohere.call("command-r-plus", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, litellm


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @litellm.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, azure


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @azure.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, vertex


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @vertex.call("gemini-1.5-flash", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseTool, Messages, bedrock


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", tools=[FormatBook])
                async def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, openai, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @openai.call(model="gpt-4o-mini", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, anthropic, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, mistral, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @mistral.call("mistral-large-latest", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, gemini, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @gemini.call("gemini-1.5-flash", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, groq, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @groq.call("llama-3.1-70b-versatile", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, cohere, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @cohere.call("command-r-plus", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, litellm, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @litellm.call(model="gpt-4o-mini", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, azure, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @azure.call(model="gpt-4o-mini", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, prompt_template, vertex


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @vertex.call("gemini-1.5-flash", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="10 16 18 24-25"
                import asyncio

                from mirascope.core import BaseTool, bedrock, prompt_template


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", tools=[FormatBook])
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str): ...


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, openai


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @openai.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Anthropic"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, anthropic


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Mistral"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, mistral


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @mistral.call("mistral-large-latest", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Gemini"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, gemini


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @gemini.call("gemini-1.5-flash", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Groq"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, groq


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @groq.call("llama-3.1-70b-versatile", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Cohere"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, cohere


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @cohere.call("command-r-plus", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "LiteLLM"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, litellm


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @litellm.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Azure AI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, azure


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @azure.call(model="gpt-4o-mini", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Vertex AI"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, vertex


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @vertex.call("gemini-1.5-flash", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```
        === "Bedrock"

            ```python hl_lines="10 16 17 24-25"
                import asyncio

                from mirascope.core import BaseMessageParam, BaseTool, bedrock


                class FormatBook(BaseTool):
                    title: str
                    author: str

                    async def call(self) -> str:
                        # Simulating an async API call
                        await asyncio.sleep(1)
                        return f"{self.title} by {self.author}"


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", tools=[FormatBook])
                async def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                async def main():
                    response = await recommend_book("fantasy")
                    if tool := response.tool:
                        if isinstance(tool, FormatBook):
                            output = await tool.call()
                            print(output)
                    else:
                        print(response.content)


                asyncio.run(main())
            ```


It's important to note that in this example we use `isinstance(tool, FormatBook)` to ensure the `call` method can be awaited safely. This also gives us proper type hints and editor support.

## Custom Client

When using custom clients with async calls, it's crucial to use the asynchronous version of the client. You can provide the async client either through the decorator or dynamic configuration:

__Decorator Parameter:__

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Gemini"

            ```python hl_lines="1 5"
                from google.generativeai import GenerativeModel
                from mirascope.core import gemini


                @gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", client=AsyncGroq())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import cohere


                @cohere.call("command-r-plus", client=AsyncClient())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import Messages, mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Gemini"

            ```python hl_lines="1 5"
                from google.generativeai import GenerativeModel
                from mirascope.core import Messages, gemini


                @gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", client=AsyncGroq())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", client=AsyncClient())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import Messages, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import Messages, bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai, prompt_template
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import mistral, prompt_template
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
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
                async def recommend_book_async(genre: str): ...
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", client=AsyncGroq())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", client=AsyncClient())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, prompt_template


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import prompt_template, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import bedrock, prompt_template
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import BaseMessageParam, mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Gemini"

            ```python hl_lines="1 5"
                from google.generativeai import GenerativeModel
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", client=AsyncGroq())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", client=AsyncClient())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import BaseMessageParam, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Vertex AI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, vertex
                from vertexai.generative_models import GenerativeModel


                @vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import BaseMessageParam, bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```


__Dynamic Configuration:__

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="2 9"
                from mirascope.core import openai, Messages
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic, Messages


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"  
                import os

                from mirascope.core import mistral, Messages
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Gemini"

            ```python hl_lines="1 9"
                from google.generativeai import GenerativeModel
                from mirascope.core import gemini, Messages


                @gemini.call("")
                async def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import AsyncGroq
                from mirascope.core import groq, Messages


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncGroq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import AsyncClient
                from mirascope.core import cohere, Messages


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, Messages


                @azure.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncChatCompletionsClient(
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

            ```python hl_lines="5-8 15"
                from mirascope.core import bedrock, Messages
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": await get_async_client(),
                    }
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="2 9"
                from mirascope.core import Messages, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import AsyncAnthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"  
                import os

                from mirascope.core import Messages, mistral
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Gemini"

            ```python hl_lines="1 9"
                from google.generativeai import GenerativeModel
                from mirascope.core import Messages, gemini


                @gemini.call("")
                async def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import AsyncGroq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncGroq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import AsyncClient
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncChatCompletionsClient(
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

            ```python hl_lines="5-8 15"
                from mirascope.core import bedrock, Messages
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": await get_async_client(),
                    }
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="2 9"
                from mirascope.core import openai, prompt_template
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"  
                import os

                from mirascope.core import mistral, prompt_template
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Gemini"

            ```python hl_lines="1 9"
                from google.generativeai import GenerativeModel
                from mirascope.core import gemini, prompt_template


                @gemini.call("")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import AsyncGroq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "client": AsyncGroq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import AsyncClient
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "client": AsyncChatCompletionsClient(
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

            ```python hl_lines="5-8 15"
                from mirascope.core import bedrock, prompt_template
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "client": await get_async_client(),
                    }
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="2 11"
                from mirascope.core import BaseMessageParam, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 11"
                from anthropic import AsyncAnthropic
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 15"
                import os

                from mirascope.core import BaseMessageParam, mistral
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Gemini"

            ```python hl_lines="1 11"
                from google.generativeai import GenerativeModel
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("")
                async def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": GenerativeModel(model_name="gemini-1.5-flash"),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 11"
                from groq import AsyncGroq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncGroq(),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 11"
                from cohere import AsyncClient
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 12-14"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncChatCompletionsClient(
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

            ```python hl_lines="5-8 17"
                from mirascope.core import BaseMessageParam, bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": await get_async_client(),
                    }
            ```


!!! warning "Synchronous vs Asynchronous Clients"
    Make sure to use the appropriate asynchronous client class (e.g., `AsyncOpenAI` instead of `OpenAI`) when working with async functions. Using a synchronous client in an async context can lead to blocking operations that defeat the purpose of async programming.

## Next Steps

By leveraging these async features in Mirascope, you can build more efficient and responsive applications, especially when working with multiple LLM calls or other I/O-bound operations.

This section concludes the core functionality Mirascope supports. If you haven't already, we recommend taking a look at any previous sections you've missed to learn about what you can do with Mirascope.

You can also check out the section on [Provider-Specific Features](./provider_specific_features/openai.md) to learn about how to use features that only certain providers support, such as OpenAI's structured outputs.
