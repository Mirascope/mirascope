---
search:
  boost: 2
---

# Chaining

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Chaining in Mirascope allows you to combine multiple LLM calls or operations in a sequence to solve complex tasks. This approach is particularly useful for breaking down complex problems into smaller, manageable steps.

Before diving into Mirascope's implementation, let's understand what chaining means in the context of LLM applications:

1. **Problem Decomposition**: Breaking a complex task into smaller, manageable steps.
2. **Sequential Processing**: Executing these steps in a specific order, where the output of one step becomes the input for the next.
3. **Data Flow**: Passing information between steps to build up a final result.

## Basic Usage and Syntax

### Function Chaining

Mirascope is designed to be Pythonic. Since calls are defined as functions, chaining them together is as simple as chaining the function calls as you would normally:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @openai.call("gpt-4o-mini")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @anthropic.call("claude-3-5-sonnet-20240620")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Mistral"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @mistral.call("mistral-large-latest")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Gemini"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @gemini.call("gemini-1.5-flash")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Groq"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @groq.call("llama-3.1-70b-versatile")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Cohere"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import cohere


                @cohere.call("command-r-plus")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @cohere.call("command-r-plus")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @litellm.call("gpt-4o-mini")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @azure.call("gpt-4o-mini")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @vertex.call("gemini-1.5-flash")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def translate(text: str, language: str) -> str:
                    return f"Translate this text to {language}: {text}"


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @openai.call("gpt-4o-mini")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @anthropic.call("claude-3-5-sonnet-20240620")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Mistral"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @mistral.call("mistral-large-latest")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Gemini"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @gemini.call("gemini-1.5-flash")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Groq"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @groq.call("llama-3.1-70b-versatile")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Cohere"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @cohere.call("command-r-plus")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @litellm.call("gpt-4o-mini")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @azure.call("gpt-4o-mini")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @vertex.call("gemini-1.5-flash")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 10 14-15"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def translate(text: str, language: str) -> Messages.Type:
                    return Messages.User(f"Translate this text to {language}: {text}")


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @openai.call("gpt-4o-mini")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Anthropic"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Mistral"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @mistral.call("mistral-large-latest")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Gemini"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Groq"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Cohere"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @cohere.call("command-r-plus")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "LiteLLM"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @litellm.call("gpt-4o-mini")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Azure AI"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @azure.call("gpt-4o-mini")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Vertex AI"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Bedrock"

            ```python hl_lines="6 11 14-15"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Translate this text to {language}: {text}")
                def translate(text: str, language: str): ...


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @openai.call("gpt-4o-mini")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @anthropic.call("claude-3-5-sonnet-20240620")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Mistral"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @mistral.call("mistral-large-latest")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Gemini"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @gemini.call("gemini-1.5-flash")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Groq"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @groq.call("llama-3.1-70b-versatile")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Cohere"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @cohere.call("command-r-plus")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @litellm.call("gpt-4o-mini")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @azure.call("gpt-4o-mini")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @vertex.call("gemini-1.5-flash")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 10 19-20"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def translate(text: str, language: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {text}",
                        )
                    ]


                summary = summarize("Long English text here...")
                translation = translate(summary.content, "french")
                print(translation.content)
            ```

One benefit of this approach is that you can chain your calls together any which way since they are just functions. You can then always wrap these functional chains in a parent function that operates as the single call to the chain.

### Nested Chains

In some cases you'll want to prompt engineer an entire chain rather than just chaining together individual calls. You can do this simply by calling the subchain inside the function body of the parent:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @openai.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @mistral.call("mistral-large-latest")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @gemini.call("gemini-1.5-flash")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @groq.call("llama-3.1-70b-versatile")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import cohere


                @cohere.call("command-r-plus")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @cohere.call("command-r-plus")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @litellm.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @azure.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @vertex.call("gemini-1.5-flash")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize(text: str) -> str:
                    return f"Summarize this text: {text}"


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize_and_translate(text: str, language: str) -> str:
                    summary = summarize(text)
                    return f"Translate this text to {language}: {summary.content}"


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @openai.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @mistral.call("mistral-large-latest")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @gemini.call("gemini-1.5-flash")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @groq.call("llama-3.1-70b-versatile")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @cohere.call("command-r-plus")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @litellm.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @azure.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @vertex.call("gemini-1.5-flash")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 11-12 15"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize(text: str) -> Messages.Type:
                    return Messages.User(f"Summarize this text: {text}")


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize_and_translate(text: str, language: str) -> Messages.Type:
                    summary = summarize(text)
                    return Messages.User(f"Translate this text to {language}: {summary.content}")


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, openai, prompt_template


                @openai.call("gpt-4o-mini")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @openai.call("gpt-4o-mini")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, mistral, prompt_template


                @mistral.call("mistral-large-latest")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @mistral.call("mistral-large-latest")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, gemini, prompt_template


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @gemini.call("gemini-1.5-flash")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, groq, prompt_template


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @groq.call("llama-3.1-70b-versatile")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @cohere.call("command-r-plus")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, litellm, prompt_template


                @litellm.call("gpt-4o-mini")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @litellm.call("gpt-4o-mini")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @azure.call("gpt-4o-mini")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, prompt_template, vertex


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @vertex.call("gemini-1.5-flash")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="6 10 12 15"
                from mirascope.core import BaseDynamicConfig, bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Summarize this text: {text}")
                def summarize(text: str): ...


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Translate this text to {language}: {summary}")
                def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                    return {"computed_fields": {"summary": summarize(text)}}


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @openai.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Anthropic"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @anthropic.call("claude-3-5-sonnet-20240620")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Mistral"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @mistral.call("mistral-large-latest")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Gemini"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @gemini.call("gemini-1.5-flash")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Groq"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @groq.call("llama-3.1-70b-versatile")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Cohere"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @cohere.call("command-r-plus")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "LiteLLM"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @litellm.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Azure AI"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @azure.call("gpt-4o-mini")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Vertex AI"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @vertex.call("gemini-1.5-flash")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```
        === "Bedrock"

            ```python hl_lines="5 11 15 20"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize(text: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
                    summary = summarize(text)
                    return [
                        BaseMessageParam(
                            role="user",
                            content=f"Translate this text to {language}: {summary.content}",
                        )
                    ]


                response = summarize_and_translate("Long English text here...", "french")
                print(response.content)
            ```

We recommend using nested chains for better observability when using tracing tools or applications.

??? tip "Improved tracing through computed fields"

    If you use computed fields in your nested chains, you can always access the computed field in the response. This provides improved tracing for your chains from a single call:

    !!! mira ""

        === "Shorthand"

            === "OpenAI"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, openai


                    @openai.call(model="gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @openai.call(model="gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Anthropic"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, anthropic


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Mistral"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, mistral


                    @mistral.call("mistral-large-latest")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @mistral.call("mistral-large-latest")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Gemini"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, gemini


                    @gemini.call("gemini-1.5-flash")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @gemini.call("gemini-1.5-flash")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Groq"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, groq


                    @groq.call("llama-3.1-70b-versatile")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @groq.call("llama-3.1-70b-versatile")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Cohere"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, cohere


                    @cohere.call("command-r-plus")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @cohere.call("command-r-plus")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "LiteLLM"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, litellm


                    @litellm.call("gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @litellm.call("gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Azure AI"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, azure


                    @azure.call("gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @azure.call("gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Vertex AI"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, vertex


                    @vertex.call("gemini-1.5-flash")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @vertex.call("gemini-1.5-flash")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Bedrock"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, bedrock


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
        === "Messages"

            === "OpenAI"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, openai


                    @openai.call(model="gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @openai.call(model="gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Anthropic"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, anthropic


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Mistral"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, mistral


                    @mistral.call("mistral-large-latest")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @mistral.call("mistral-large-latest")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Gemini"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, gemini


                    @gemini.call("gemini-1.5-flash")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @gemini.call("gemini-1.5-flash")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Groq"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, groq


                    @groq.call("llama-3.1-70b-versatile")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @groq.call("llama-3.1-70b-versatile")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Cohere"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, cohere


                    @cohere.call("command-r-plus")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @cohere.call("command-r-plus")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "LiteLLM"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, litellm


                    @litellm.call("gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @litellm.call("gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Azure AI"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, azure


                    @azure.call("gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @azure.call("gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Vertex AI"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, vertex


                    @vertex.call("gemini-1.5-flash")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @vertex.call("gemini-1.5-flash")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Bedrock"

                ```python hl_lines="16 23-24"
                    from mirascope.core import BaseDynamicConfig, Messages, bedrock


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                Messages.User(f"Translate this text to {language}: {summary.content}")
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
        === "String Template"

            === "OpenAI"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, openai, prompt_template


                    @openai.call(model="gpt-4o-mini")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @openai.call(model="gpt-4o-mini")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Anthropic"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, anthropic, prompt_template


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Mistral"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, mistral, prompt_template


                    @mistral.call("mistral-large-latest")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @mistral.call("mistral-large-latest")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Gemini"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, gemini, prompt_template


                    @gemini.call("gemini-1.5-flash")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @gemini.call("gemini-1.5-flash")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Groq"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, groq, prompt_template


                    @groq.call("llama-3.1-70b-versatile")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @groq.call("llama-3.1-70b-versatile")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Cohere"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, cohere, prompt_template


                    @cohere.call("command-r-plus")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @cohere.call("command-r-plus")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "LiteLLM"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, litellm, prompt_template


                    @litellm.call("gpt-4o-mini")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @litellm.call("gpt-4o-mini")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Azure AI"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, azure, prompt_template


                    @azure.call("gpt-4o-mini")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @azure.call("gpt-4o-mini")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Vertex AI"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, prompt_template, vertex


                    @vertex.call("gemini-1.5-flash")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @vertex.call("gemini-1.5-flash")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Bedrock"

                ```python hl_lines="12 18-19"
                    from mirascope.core import BaseDynamicConfig, bedrock, prompt_template


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    @prompt_template("Summarize this text: {text}")
                    def summarize(text: str): ...


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    @prompt_template("Translate this text to {language}: {summary}")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        return {"computed_fields": {"summary": summarize(text)}}


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
        === "BaseMessageParam"

            === "OpenAI"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, openai


                    @openai.call(model="gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @openai.call(model="gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Anthropic"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, anthropic


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Mistral"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, mistral


                    @mistral.call("mistral-large-latest")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @mistral.call("mistral-large-latest")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Gemini"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, gemini


                    @gemini.call("gemini-1.5-flash")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @gemini.call("gemini-1.5-flash")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Groq"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, groq


                    @groq.call("llama-3.1-70b-versatile")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @groq.call("llama-3.1-70b-versatile")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Cohere"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, cohere


                    @cohere.call("command-r-plus")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @cohere.call("command-r-plus")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "LiteLLM"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, litellm


                    @litellm.call("gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @litellm.call("gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Azure AI"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, azure


                    @azure.call("gpt-4o-mini")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @azure.call("gpt-4o-mini")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Vertex AI"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, vertex


                    @vertex.call("gemini-1.5-flash")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @vertex.call("gemini-1.5-flash")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```
            === "Bedrock"

                ```python hl_lines="19 26-27"
                    from mirascope.core import BaseDynamicConfig, BaseMessageParam, bedrock


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    def summarize(text: str) -> str:
                        return f"Summarize this text: {text}"


                    @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
                    def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
                        summary = summarize(text)
                        return {
                            "messages": [
                                BaseMessageParam(
                                    role="user",
                                    content=f"Translate this text to {language}: {summary.content}",
                                )
                            ],
                            "computed_fields": {"summary": summary},
                        }


                    response = summarize_and_translate("Long English text here...", "french")
                    print(response.content)
                    print(
                        response.model_dump()["computed_fields"]
                    )  # This will contain the `summarize` response
                ```

## Advanced Chaining Techniques

There are many different ways to chain calls together, often resulting in breakdowns and flows that are specific to your task.

Here are a few examples:

!!! mira ""

    === "Conditional"

        ```python
            from enum import Enum

            from mirascope.core import openai, prompt_template


            class Sentiment(str, Enum):
                POSITIVE = "positive"
                NEGATIVE = "negative"


            @openai.call(model="gpt-4o", response_model=Sentiment)
            def sentiment_classifier(review: str) -> str:
                return f"Is the following review positive or negative? {review}"


            @openai.call("gpt-4o-mini")
            @prompt_template(
                """
                SYSTEM:
                Your task is to respond to a review.
                The review has been identified as {sentiment}.
                Please write a {conditional_review_prompt}.

                USER: Write a response for the following review: {review}
                """
            )
            def review_responder(review: str) -> openai.OpenAIDynamicConfig:
                sentiment = sentiment_classifier(review=review)
                conditional_review_prompt = (
                    "thank you response for the review."
                    if sentiment == Sentiment.POSITIVE
                    else "response addressing the review."
                )
                return {
                    "computed_fields": {
                        "conditional_review_prompt": conditional_review_prompt,
                        "sentiment": sentiment,
                    }
                }


            positive_review = "This tool is awesome because it's so flexible!"
            response = review_responder(review=positive_review)
            print(response)
            print(response.dynamic_config)
        ```

    === "Parallel"

        ```python
            import asyncio

            from mirascope.core import openai, prompt_template
            from pydantic import BaseModel


            @openai.call(model="gpt-4o-mini")
            @prompt_template(
                """
                Please identify a chef who is well known for cooking with {ingredient}.
                Respond only with the chef's name.
                """
            )
            async def chef_selector(ingredient: str): ...


            class IngredientsList(BaseModel):
                ingredients: list[str]


            @openai.call(model="gpt-4o-mini", response_model=IngredientsList)
            @prompt_template(
                """
                Given a base ingredient {ingredient}, return a list of complementary ingredients.
                Make sure to exclude the original ingredient from the list.
                """
            )
            async def ingredients_identifier(ingredient: str): ...


            @openai.call(model="gpt-4o-mini")
            @prompt_template(
                """
                SYSTEM:
                Your task is to recommend a recipe. Pretend that you are chef {chef}.

                USER:
                Recommend recipes that use the following ingredients:
                {ingredients}
                """
            )
            async def recipe_recommender(ingredient: str) -> openai.OpenAIDynamicConfig:
                chef, ingredients = await asyncio.gather(
                    chef_selector(ingredient), ingredients_identifier(ingredient)
                )
                return {"computed_fields": {"chef": chef, "ingredients": ingredients}}


            async def run():
                response = await recipe_recommender(ingredient="apples")
                print(response.content)


            asyncio.run(run())
        ```

    === "Iterative"

        ```python
            from mirascope.core import openai, prompt_template
            from pydantic import BaseModel, Field


            class SummaryFeedback(BaseModel):
                """Feedback on summary with a critique and review rewrite based on said critique."""

                critique: str = Field(..., description="The critique of the summary.")
                rewritten_summary: str = Field(
                    ...,
                    description="A rewritten summary that takes the critique into account.",
                )


            @openai.call(model="gpt-4o")
            def summarizer(original_text: str) -> str:
                return f"Summarize the following text into one sentence: {original_text}"


            @openai.call(model="gpt-4o", response_model=SummaryFeedback)
            @prompt_template(
                """
                Original Text: {original_text}
                Summary: {summary}

                Critique the summary of the original text.
                Then rewrite the summary based on the critique. It must be one sentence.
                """
            )
            def resummarizer(original_text: str, summary: str): ...


            def rewrite_iteratively(original_text: str, summary: str, depth=2):
                text = original_text
                for _ in range(depth):
                    text = resummarizer(original_text=text, summary=summary).rewritten_summary
                return text


            original_text = """
            In the heart of a dense forest, a boy named Timmy pitched his first tent, fumbling with the poles and pegs.
            His grandfather, a seasoned camper, guided him patiently, their bond strengthening with each knot tied.
            As night fell, they sat by a crackling fire, roasting marshmallows and sharing tales of old adventures.
            Timmy marveled at the star-studded sky, feeling a sense of wonder he'd never known.
            By morning, the forest had transformed him, instilling a love for the wild that would last a lifetime.
            """

            summary = summarizer(original_text=original_text).content
            print(f"Summary: {summary}")
            # > Summary: In the dense forest, Timmy's first tent-pitching experience with his seasoned camper grandfather deepened their bond and ignited a lifelong love for the wild.
            rewritten_summary = rewrite_iteratively(original_text, summary)
            print(f"Rewritten Summary: {rewritten_summary}")
            # > Rewritten Summary: In the dense forest, Timmy's first tent-pitching experience with his seasoned camper grandfather, filled with roasting marshmallows and sharing tales by the fire, deepened their bond, filled him with wonder at the starry sky, and ignited a lifelong love for the wild.
        ```

[Response Models](./response_models.md) are a great way to add more structure to your chains, and [parallel async calls](./async.md#parallel-async-calls) can be particularly powerful for making your chains more efficient.

For inspiration on even more ways you can chain calls together, check out our tutorial section on [chaining-based prompt engineering](../tutorials/prompt_engineering/chaining_based/self_refine.ipynb), which covers many advanced chaining techniques used to apply prompt engineering concepts.

## Next Steps

By mastering Mirascope's chaining techniques, you can create sophisticated LLM-powered applications that tackle complex, multi-step problems with greater accuracy, control, and observability.

Next, we recommend taking a look at the [Response Models](./response_models.md) documentation, which shows you how to generate structured outputs.
