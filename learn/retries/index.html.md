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
                from mirascope.core import openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                from mirascope.core import anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                from mirascope.core import mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Google"

            ```python hl_lines="2 5-8"
                from mirascope.core import google
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @google.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                from mirascope.core import groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                from mirascope.core import cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                from mirascope.core import litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                from mirascope.core import azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                from mirascope.core import bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                print(recommend_book("fantasy"))
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Google"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, google
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @google.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                from mirascope.core import Messages, bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                print(recommend_book("fantasy"))
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="2 5-8"
                from mirascope.core import openai, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                from mirascope.core import anthropic, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                from mirascope.core import mistral, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Google"

            ```python hl_lines="2 5-8"
                from mirascope.core import google, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @google.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                from mirascope.core import groq, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                from mirascope.core import cohere, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                from mirascope.core import litellm, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @litellm.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                from mirascope.core import azure, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                from mirascope.core import bedrock, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @openai.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Anthropic"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @anthropic.call("claude-3-5-sonnet-20240620")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Mistral"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @mistral.call("mistral-large-latest")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Google"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, google
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @google.call("gemini-1.5-flash")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Groq"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @groq.call("llama-3.1-70b-versatile")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Cohere"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @cohere.call("command-r-plus")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "LiteLLM"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @litellm.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Azure AI"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @azure.call("gpt-4o-mini")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
            ```
        === "Bedrock"

            ```python hl_lines="2 5-8"
                from mirascope.core import BaseMessageParam, bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                print(recommend_book("fantasy"))
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
                from mirascope.core import openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                from mirascope.core import anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Mistral"

            ```python hl_lines="10-14"
                from mirascope.core import mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Google"

            ```python hl_lines="10-14"
                from mirascope.core import google
                from tenacity import retry, stop_after_attempt, wait_exponential


                @google.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Groq"

            ```python hl_lines="10-14"
                from mirascope.core import groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Cohere"

            ```python hl_lines="10-14"
                from mirascope.core import cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                from mirascope.core import litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                from mirascope.core import azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                from mirascope.core import bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Mistral"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Google"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, google
                from tenacity import retry, stop_after_attempt, wait_exponential


                @google.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Groq"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Cohere"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                from mirascope.core import Messages, bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="10-14"
                from mirascope.core import openai, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @openai.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                from mirascope.core import anthropic, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Mistral"

            ```python hl_lines="10-14"
                from mirascope.core import mistral, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @mistral.call("mistral-large-latest", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Google"

            ```python hl_lines="10-14"
                from mirascope.core import google, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @google.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Groq"

            ```python hl_lines="10-14"
                from mirascope.core import groq, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @groq.call("llama-3.1-70b-versatile", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Cohere"

            ```python hl_lines="10-14"
                from mirascope.core import cohere, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @cohere.call("command-r-plus", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                from mirascope.core import litellm, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @litellm.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                from mirascope.core import azure, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @azure.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                from mirascope.core import bedrock, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Anthropic"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Mistral"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Google"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, google
                from tenacity import retry, stop_after_attempt, wait_exponential


                @google.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Groq"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Cohere"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "LiteLLM"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Azure AI"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```
        === "Bedrock"

            ```python hl_lines="10-14"
                from mirascope.core import BaseMessageParam, bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def stream():
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)


                stream()
            ```


### Tools

When using tools, `ValidationError` errors won't happen until you attempt to construct the tool (either when calling `response.tools` or iterating through a stream with tools).

You need to handle retries in this case the same way as streams:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="19-23"
                from mirascope.core import openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @openai.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                from mirascope.core import anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Mistral"

            ```python hl_lines="19-23"
                from mirascope.core import mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @mistral.call("mistral-large-latest", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Google"

            ```python hl_lines="19-23"
                from mirascope.core import google
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @google.call("gemini-1.5-flash", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Groq"

            ```python hl_lines="19-23"
                from mirascope.core import groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @groq.call("llama-3.1-70b-versatile", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Cohere"

            ```python hl_lines="19-23"
                from mirascope.core import cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @cohere.call("command-r-plus", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                from mirascope.core import litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @litellm.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                from mirascope.core import azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @azure.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                from mirascope.core import bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[get_book_author])
                def identify_author(book: str) -> str:
                    return f"Who wrote {book}?"


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @openai.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Mistral"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @mistral.call("mistral-large-latest", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Google"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, google
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @google.call("gemini-1.5-flash", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Groq"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @groq.call("llama-3.1-70b-versatile", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Cohere"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @cohere.call("command-r-plus", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @litellm.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @azure.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                from mirascope.core import Messages, bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[get_book_author])
                def identify_author(book: str) -> Messages.Type:
                    return Messages.User(f"Who wrote {book}?")


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="19-23"
                from mirascope.core import openai, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @openai.call("gpt-4o-mini", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                from mirascope.core import anthropic, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Mistral"

            ```python hl_lines="19-23"
                from mirascope.core import mistral, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @mistral.call("mistral-large-latest", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Google"

            ```python hl_lines="19-23"
                from mirascope.core import google, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @google.call("gemini-1.5-flash", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Groq"

            ```python hl_lines="19-23"
                from mirascope.core import groq, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @groq.call("llama-3.1-70b-versatile", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Cohere"

            ```python hl_lines="19-23"
                from mirascope.core import cohere, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @cohere.call("command-r-plus", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                from mirascope.core import litellm, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @litellm.call("gpt-4o-mini", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                from mirascope.core import azure, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @azure.call("gpt-4o-mini", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                from mirascope.core import bedrock, prompt_template
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[get_book_author])
                @prompt_template("Who wrote {book}?")
                def identify_author(book: str): ...


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, openai
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @openai.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Anthropic"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, anthropic
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @anthropic.call("claude-3-5-sonnet-20240620", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Mistral"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, mistral
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @mistral.call("mistral-large-latest", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Google"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, google
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @google.call("gemini-1.5-flash", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Groq"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, groq
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @groq.call("llama-3.1-70b-versatile", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Cohere"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, cohere
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @cohere.call("command-r-plus", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "LiteLLM"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, litellm
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @litellm.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Azure AI"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, azure
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @azure.call("gpt-4o-mini", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```
        === "Bedrock"

            ```python hl_lines="19-23"
                from mirascope.core import BaseMessageParam, bedrock
                from tenacity import retry, stop_after_attempt, wait_exponential


                def get_book_author(title: str) -> str:
                    if title == "The Name of the Wind":
                        return "Patrick Rothfuss"
                    elif title == "Mistborn: The Final Empire":
                        return "Brandon Sanderson"
                    else:
                        return "Unknown"


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[get_book_author])
                def identify_author(book: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Who wrote {book}?")]


                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=4, max=10),
                )
                def run():
                    response = identify_author("The Name of the Wind")
                    if tool := response.tool:
                        print(tool.call())
                        print(f"Original tool call: {tool.tool_call}")
                    else:
                        print(response.content)


                run()
            ```


### Error Reinsertion

Every example above simply retries after a failed attempt without making any updates to the call. This approach can be sufficient for some use-cases where we can safely expect the call to succeed on subsequent attempts (e.g. rate limits).

However, there are some cases where the LLM is likely to make the same mistake over and over again. For example, when using tools or response models, the LLM may return incorrect or missing arguments where it's highly likely the LLM will continuously make the same mistake on subsequent calls. In these cases, it's important that we update subsequent calls based on resulting errors to improve the chance of success on the next call.

To make it easier to make such updates, Mirascope provides a `collect_errors` handler that can collect any errors of your choice and insert them into subsequent calls through an `errors` keyword argument.

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import openai
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @openai.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Anthropic"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import anthropic
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @anthropic.call(
                    "claude-3-5-sonnet-20240620",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Mistral"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import mistral
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @mistral.call(
                    "mistral-large-latest",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Google"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import google
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @google.call(
                    "gemini-1.5-flash",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Groq"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import groq
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @groq.call(
                    "llama-3.1-70b-versatile",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Cohere"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import cohere
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @cohere.call(
                    "command-r-plus",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "LiteLLM"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import litellm
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @litellm.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Azure AI"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import azure
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @azure.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Bedrock"

            ```python hl_lines="4 14 19 33"
                from typing import Annotated

                from mirascope.core import bedrock
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        return f"Previous Error: {errors}\n\nWho wrote {book}?"
                    return f"Who wrote {book}?"


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, openai
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @openai.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Anthropic"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, anthropic
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @anthropic.call(
                    "claude-3-5-sonnet-20240620",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Mistral"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, mistral
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @mistral.call(
                    "mistral-large-latest",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Google"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, google
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @google.call(
                    "gemini-1.5-flash",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Groq"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, groq
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @groq.call(
                    "llama-3.1-70b-versatile",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Cohere"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, cohere
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @cohere.call(
                    "command-r-plus",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "LiteLLM"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, litellm
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @litellm.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Azure AI"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, azure
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @azure.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Bedrock"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import Messages, bedrock
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> Messages.Type:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return Messages.User(content)


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, openai, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @openai.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Anthropic"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, anthropic, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @anthropic.call(
                    "claude-3-5-sonnet-20240620",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Mistral"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, mistral, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @mistral.call(
                    "mistral-large-latest",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Google"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, google, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @google.call(
                    "gemini-1.5-flash",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Groq"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, groq, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @groq.call(
                    "llama-3.1-70b-versatile",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Cohere"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, cohere, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @cohere.call(
                    "command-r-plus",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "LiteLLM"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, litellm, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @litellm.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Azure AI"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, azure, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @azure.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Bedrock"

            ```python hl_lines="4 14 27 42"
                from typing import Annotated

                from mirascope.core import BaseDynamicConfig, bedrock, prompt_template
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                @prompt_template(
                    """
                    {previous_errors}

                    Who wrote {book}?
                    """
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> BaseDynamicConfig:
                    previous_errors = None
                    if errors:
                        previous_errors = f"Previous Errors: {errors}"
                        print(previous_errors)
                    return {"computed_fields": {"previous_errors": previous_errors}}


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, openai
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @openai.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Anthropic"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, anthropic
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @anthropic.call(
                    "claude-3-5-sonnet-20240620",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Mistral"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, mistral
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @mistral.call(
                    "mistral-large-latest",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Google"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, google
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @google.call(
                    "gemini-1.5-flash",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Groq"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, groq
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @groq.call(
                    "llama-3.1-70b-versatile",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Cohere"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, cohere
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @cohere.call(
                    "command-r-plus",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "LiteLLM"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, litellm
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @litellm.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Azure AI"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, azure
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @azure.call(
                    "gpt-4o-mini",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
            ```
        === "Bedrock"

            ```python hl_lines="4 14 20 37"
                from typing import Annotated

                from mirascope.core import BaseMessageParam, bedrock
                from mirascope.retries.tenacity import collect_errors
                from pydantic import AfterValidator, ValidationError
                from tenacity import retry, stop_after_attempt


                def is_upper(v: str) -> str:
                    assert v.isupper(), "Must be uppercase"
                    return v


                @retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
                )
                def identify_author(
                    book: str, *, errors: list[ValidationError] | None = None
                ) -> list[BaseMessageParam]:
                    previous_errors = None
                    if errors:
                        print(previous_errors)
                        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
                    else:
                        content = f"Who wrote {book}?"
                    return [BaseMessageParam(role="user", content=content)]


                author = identify_author("The Name of the Wind")
                print(author)
                # Previous Errors: [1 validation error for str
                # value
                #   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
                #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
                # PATRICK ROTHFUSS
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
            @llm.call("openai", "gpt-4o-minis")
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

