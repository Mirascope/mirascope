---
search:
  boost: 2
---

# Output Parsers

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Output Parsers in Mirascope provide a flexible way to process and structure the raw output from Large Language Models (LLMs). They allow you to transform the LLM's response into a more usable format, enabling easier integration with your application logic and improving the overall reliability of your LLM-powered features.

## Basic Usage and Syntax

??? api "API Documentation"

    [`mirascope.core.openai.call.output_parser`](../api/core/openai/call.md?h=output_parser)
    [`mirascope.core.anthropic.call.output_parser`](../api/core/anthropic/call.md?h=output_parser)
    [`mirascope.core.mistral.call.output_parser`](../api/core/mistral/call.md?h=output_parser)
    [`mirascope.core.gemini.call.output_parser`](../api/core/gemini/call.md?h=output_parser)
    [`mirascope.core.groq.call.output_parser`](../api/core/groq/call.md?h=output_parser)
    [`mirascope.core.cohere.call.output_parser`](../api/core/cohere/call.md?h=output_parser)
    [`mirascope.core.litellm.call.output_parser`](../api/core/litellm/call.md?h=output_parser)
    [`mirascope.core.azure.call.output_parser`](../api/core/azure/call.md?h=output_parser)
    [`mirascope.core.vertex.call.output_parser`](../api/core/vertex/call.md?h=output_parser)
    [`mirascope.core.bedrock.call.output_parser`](../api/core/bedrock/call.md?h=output_parser)

Output Parsers are functions that take the call response object as input and return an output of a specified type. When you supply an output parser to a `call` decorator, it modifies the return type of the decorated function to match the output type of the parser.

Let's take a look at a basic example:

!!! mira ""

    === "Shorthand"

        === "OpenAI"
            ```python hl_lines="9 15"
                from mirascope.core import openai


                def parse_recommendation(response: openai.OpenAICallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @openai.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Anthropic"
            ```python hl_lines="9 15"
                from mirascope.core import anthropic


                def parse_recommendation(response: anthropic.AnthropicCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @anthropic.call("claude-3-5-sonnet-20240620", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Mistral"
            ```python hl_lines="9 15"
                from mirascope.core import mistral


                def parse_recommendation(response: mistral.MistralCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @mistral.call("mistral-large-latest", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Gemini"
            ```python hl_lines="9 15"
                from mirascope.core import gemini


                def parse_recommendation(response: gemini.GeminiCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @gemini.call("gemini-1.5-flash", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Groq"
            ```python hl_lines="9 15"
                from mirascope.core import groq


                def parse_recommendation(response: groq.GroqCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @groq.call("llama-3.1-70b-versatile", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Cohere"
            ```python hl_lines="9 15"
                from mirascope.core import cohere


                def parse_recommendation(response: cohere.CohereCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @cohere.call("command-r-plus", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "LiteLLM"
            ```python hl_lines="9 15"
                from mirascope.core import litellm


                def parse_recommendation(response: litellm.LiteLLMCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @litellm.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Azure AI"
            ```python hl_lines="9 15"
                from mirascope.core import azure


                def parse_recommendation(response: azure.AzureCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @azure.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Vertex AI"
            ```python hl_lines="9 15"
                from mirascope.core import vertex


                def parse_recommendation(response: vertex.VertexCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @vertex.call("gemini-1.5-flash", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Bedrock"
 
            ```python hl_lines="10 17"
                from mirascope.core import bedrock


                def parse_recommendation(response: bedrock.BedrockCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", output_parser=parse_recommendation
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book. Output only Title by Author"


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```

    === "Messages"

        === "OpenAI"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, openai


                def parse_recommendation(response: openai.OpenAICallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @openai.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Anthropic"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, anthropic


                def parse_recommendation(response: anthropic.AnthropicCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @anthropic.call("claude-3-5-sonnet-20240620", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Mistral"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, mistral


                def parse_recommendation(response: mistral.MistralCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @mistral.call("mistral-large-latest", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Gemini"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, gemini


                def parse_recommendation(response: gemini.GeminiCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @gemini.call("gemini-1.5-flash", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Groq"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, groq


                def parse_recommendation(response: groq.GroqCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @groq.call("llama-3.1-70b-versatile", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Cohere"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, cohere


                def parse_recommendation(response: cohere.CohereCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @cohere.call("command-r-plus", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "LiteLLM"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, litellm


                def parse_recommendation(response: litellm.LiteLLMCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @litellm.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Azure AI"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, azure


                def parse_recommendation(response: azure.AzureCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @azure.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Vertex AI"
            ```python hl_lines="9 15"
                from mirascope.core import Messages, vertex


                def parse_recommendation(response: vertex.VertexCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @vertex.call("gemini-1.5-flash", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Bedrock"
 
            ```python hl_lines="10 17"
                from mirascope.core import Messages, bedrock


                def parse_recommendation(response: bedrock.BedrockCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", output_parser=parse_recommendation
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book. Output only Title by Author")


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```

    === "String Template"

        === "OpenAI"
            ```python hl_lines="9 15"
                from mirascope.core import openai, prompt_template


                def parse_recommendation(response: openai.OpenAICallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @openai.call("gpt-4o-mini", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Anthropic"
            ```python hl_lines="9 15"
                from mirascope.core import anthropic, prompt_template


                def parse_recommendation(response: anthropic.AnthropicCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @anthropic.call("claude-3-5-sonnet-20240620", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Mistral"
            ```python hl_lines="9 15"
                from mirascope.core import mistral, prompt_template


                def parse_recommendation(response: mistral.MistralCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @mistral.call("mistral-large-latest", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Gemini"
            ```python hl_lines="9 15"
                from mirascope.core import gemini, prompt_template


                def parse_recommendation(response: gemini.GeminiCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @gemini.call("gemini-1.5-flash", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Groq"
            ```python hl_lines="9 15"
                from mirascope.core import groq, prompt_template


                def parse_recommendation(response: groq.GroqCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @groq.call("llama-3.1-70b-versatile", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Cohere"
            ```python hl_lines="9 15"
                from mirascope.core import cohere, prompt_template


                def parse_recommendation(response: cohere.CohereCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @cohere.call("command-r-plus", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "LiteLLM"
            ```python hl_lines="9 15"
                from mirascope.core import litellm, prompt_template


                def parse_recommendation(response: litellm.LiteLLMCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @litellm.call("gpt-4o-mini", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Azure AI"
            ```python hl_lines="9 15"
                from mirascope.core import azure, prompt_template


                def parse_recommendation(response: azure.AzureCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @azure.call("gpt-4o-mini", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Vertex AI"
            ```python hl_lines="9 15"
                from mirascope.core import prompt_template, vertex


                def parse_recommendation(response: vertex.VertexCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @vertex.call("gemini-1.5-flash", output_parser=parse_recommendation)
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Bedrock"
 
            ```python hl_lines="10 17"
                from mirascope.core import bedrock, prompt_template


                def parse_recommendation(response: bedrock.BedrockCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", output_parser=parse_recommendation
                )
                @prompt_template("Recommend a {genre} book. Output only Title by Author")
                def recommend_book(genre: str): ...


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```

    === "BaseMessageParam"

        === "OpenAI"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, openai


                def parse_recommendation(response: openai.OpenAICallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @openai.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Anthropic"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, anthropic


                def parse_recommendation(response: anthropic.AnthropicCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @anthropic.call("claude-3-5-sonnet-20240620", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Mistral"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, mistral


                def parse_recommendation(response: mistral.MistralCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @mistral.call("mistral-large-latest", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Gemini"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, gemini


                def parse_recommendation(response: gemini.GeminiCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @gemini.call("gemini-1.5-flash", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Groq"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, groq


                def parse_recommendation(response: groq.GroqCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @groq.call("llama-3.1-70b-versatile", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Cohere"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, cohere


                def parse_recommendation(response: cohere.CohereCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @cohere.call("command-r-plus", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "LiteLLM"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, litellm


                def parse_recommendation(response: litellm.LiteLLMCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @litellm.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Azure AI"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, azure


                def parse_recommendation(response: azure.AzureCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @azure.call("gpt-4o-mini", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Vertex AI"
            ```python hl_lines="9 20"
                from mirascope.core import BaseMessageParam, vertex


                def parse_recommendation(response: vertex.VertexCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @vertex.call("gemini-1.5-flash", output_parser=parse_recommendation)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```
        === "Bedrock"
            ```python hl_lines="10 22"
                from mirascope.core import BaseMessageParam, bedrock


                def parse_recommendation(response: bedrock.BedrockCallResponse) -> tuple[str, str]:
                    title, author = response.content.split(" by ")
                    return (title, author)


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", output_parser=parse_recommendation
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Recommend a {genre} book. Output only Title by Author",
                        )
                    ]


                print(recommend_book("fantasy"))
                # Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
            ```


## Additional Examples

There are many different ways to structure and parse LLM outputs, ranging from XML parsing to using regular expressions.

Here are a few examples:

!!! mira ""

    === "Regular Expression"

        ```python hl_lines="7 14 17 18"
            import re

            from mirascope.core import openai, prompt_template


            def parse_cot(response: openai.OpenAICallResponse) -> str:
                pattern = r"<thinking>.?*</thinking>.*?<output>(.*?)</output>"
                match = re.search(pattern, response.content, re.DOTALL)
                if not match:
                    return response.content
                return match.group(1).strip()


            @openai.call("gpt-4o-mini", output_parser=parse_cot)
            @prompt_template(
                """
                First, output your thought process in <thinking> tags.
                Then, provide your final output in <output> tags.

                Question: {question}
                """
            )
            def chain_of_thought(question: str): ...


            question = "Roger has 5 tennis balls. He buys 2 cans of 3. How many does he have now?"
            output = chain_of_thought(question)
            print(output)
        ```

    === "XML"

        ```python hl_lines="14-28 31 35-40"
            import xml.etree.ElementTree as ET

            from mirascope.core import anthropic, prompt_template
            from pydantic import BaseModel


            class Book(BaseModel):
                title: str
                author: str
                year: int
                summary: str


            def parse_book_xml(response: anthropic.AnthropicCallResponse) -> Book | None:
                try:
                    root = ET.fromstring(response.content)
                    if (node := root.find("title")) is None or not (title := node.text):
                        raise ValueError("Missing title")
                    if (node := root.find("author")) is None or not (author := node.text):
                        raise ValueError("Missing author")
                    if (node := root.find("year")) is None or not (year := node.text):
                        raise ValueError("Missing year")
                    if (node := root.find("summary")) is None or not (summary := node.text):
                        raise ValueError("Missing summary")
                    return Book(title=title, author=author, year=int(year), summary=summary)
                except (ET.ParseError, ValueError) as e:
                    print(f"Error parsing XML: {e}")
                    return None


            @anthropic.call(model="claude-3-5-sonnet-20240620", output_parser=parse_book_xml)
            @prompt_template(
                """
                Recommend a {genre} book. Provide the information in the following XML format:
                <book>
                    <title>Book Title</title>
                    <author>Author Name</author>
                    <year>Publication Year</year>
                    <summary>Brief summary of the book</summary>
                </book>
                 
                Output ONLY the XML and no other text.
                """
            )
            def recommend_book(genre: str): ...


            book = recommend_book("science fiction")
            if book:
                print(f"Title: {book.title}")
                print(f"Author: {book.author}")
                print(f"Year: {book.year}")
                print(f"Summary: {book.summary}")
            else:
                print("Failed to parse the recommendation.")
        ```

    === "JSON Mode"

        ```python hl_lines="7-9 12"
            import json

            from mirascope.core import anthropic


            def only_json(response: anthropic.AnthropicCallResponse) -> str:
                json_start = response.content.index("{")
                json_end = response.content.rfind("}")
                return response.content[json_start : json_end + 1]


            @anthropic.call("claude-3-5-sonnet-20240620", json_mode=True, output_parser=only_json)
            def json_extraction(text: str, fields: list[str]) -> str:
                return f"Extract {fields} from the following text: {text}"


            json_response = json_extraction(
                text="The capital of France is Paris",
                fields=["capital", "country"],
            )
            print(json.loads(json_response))
        ```

## Next Steps

By leveraging Output Parsers effectively, you can create more robust and reliable LLM-powered applications, ensuring that the raw model outputs are transformed into structured data that's easy to work with in your application logic.

Next, we recommend taking a look at the section on [Tools](./tools.md) to learn how to extend the capabilities of LLMs with custom functions.
