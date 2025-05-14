# Why Use Mirascope?

Trusted by founders and engineers building the next generation of AI-native applications:

<div class="grid cards" markdown>

-   __Jake Duth__

    ---

    Co-Founder & CTO / Reddy

    ---

    "Mirascope's simplicity made it the natural next step from OpenAI's API — all without fighting the unnecessary complexity of tools like LangChain. We have all the bells and whistles we need for production while maintaining exceptional ease of use."

-   __Vince Trost__

    ---

    Co-Founder / Plastic Labs

    ---

    "The Pydantic inspired LLM toolkit the space has been missing. Simple, modular, extensible...helps where you need it, stays out of your way when you don't."

-   __Skylar Payne__

    ---

    VP of Engineering & DS / Health Rhythms

    ---

    "Mirascope's 'abstractions that aren't obstructions' tagline rings true – I was up and running in minutes, with seamless switching between AI providers. The type system catches any schema issues while I iterate, letting me focus entirely on crafting the perfect prompts."

-   __Off Sornsoontorn__

    ---

    Senior AI & ML Engineer / Six Atomic

    ---

    "LangChain required learning many concepts and its rigid abstractions made LLM behavior hard to customize. Mirascope lets us easily adapt LLM behaviors to any UI/UX design, so we can focus on innovation rather than working around limitations."

-   __William Profit__

    ---

    Co-Founder / Callisto

    ---

    "After trying many alternatives, we chose Mirascope for our large project and haven't looked back. It's simple, lean, and gets the job done without getting in the way. The team & community are super responsive, making building even easier."

-   __Rami Awar__

    ---

    Founder / DataLine

    ---

    "Migrating DataLine to Mirascope feels like I was rid of a pebble in my shoe that I never knew existed. This is what good design should feel like. Well done."

</div>

## Abstractions That Aren't Obstructions

Mirascope provides powerful abstractions that simplify LLM interactions without hiding the underlying mechanics. This approach gives you the convenience of high-level APIs while maintaining full control and transparency.

### Everything Beyond The Prompt Is Boilerplate

By eliminating boilerplate, Mirascope allows you to focus on what matter most: your prompt.

Let's compare structured outputs using Mirascope vs. the official SDKs:

!!! mira "Mirascope"

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

!!! note "Official SDK"

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

        ```python hl_lines="20-60 65"
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

        ```python hl_lines="17-48 53"
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


Reducing this boilerplate becomes increasingly important as the number and complexity of your calls grows beyond a single basic example. Furthermore, the Mirascope interface works across all of our various supported providers, so you don't need to learn the intracacies of each provider to use them the same way.

### Functional, Modular Design

Mirascope's functional approach promotes modularity and reusability. You can easily compose and chain LLM calls, creating complex workflows with simple, readable code:

!!! mira ""

    === "Separate Calls"

        === "OpenAI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="5 10 14-15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/function_chaining/bedrock/shorthand.py

            ```

    === "Nested Calls"

        === "OpenAI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="5 11-12 15"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/chaining/nested_chains/bedrock/shorthand.py

            ```

The goal of our design approach is to remain __Pythonic__ so you can __build your way__.

### Provider-Agnostic When Wanted, Specific When Needed

We understand the desire for easily switching between various LLM providers. We also understand the (common) need to engineer a prompt for a specific provider (and model).

By implementing our LLM API call functionality as decorators, Mirascope makes implementing any and all of these paths straightforward and easy:

!!! mira ""

    === "Provider-Specific"

        ```python hl_lines="4-5 9-10 14 17"
        from mirascope.core import anthropic, openai


        @openai.call("gpt-4o-mini")
        def openai_recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"


        @anthropic.call("claude-3-5-sonnet-20240620")
        def anthropic_recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"


        openai_response = openai_recommend_book("fantasy")
        print(openai_response.content)

        anthropic_response = anthropic_recommend_book("fantasy")
        print(anthropic_response.content)
        ```

    === "Provider-Agnostic"

        ```python hl_lines="4-5 11-12 17-18"
        from mirascope.core import anthropic, openai, prompt_template


        @prompt_template()
        def recommend_book_prompt(genre: str) -> str:
            return f"Recommend a {genre} book"


        # OpenAI
        openai_model = "gpt-4o-mini"
        openai_recommend_book = openai.call(openai_model)(recommend_book_prompt)
        openai_response = openai_recommend_book("fantasy")
        print(openai_response.content)

        # Anthropic
        anthropic_model = "claude-3-5-sonnet-20240620"
        anthropic_recommend_book = anthropic.call(anthropic_model)(recommend_book_prompt)
        anthropic_response = anthropic_recommend_book("fantasy")
        print(anthropic_response.content)
        ```

### Type Hints & Editor Support

<div class="grid cards" markdown>

- :material-shield-check: __Type Safety__ to catch errors before runtime during lint
- :material-lightbulb-auto: __Editor Support__ for rich autocomplete and inline documentation

</div>

<video src="https://github.com/user-attachments/assets/174acc23-a026-4754-afd3-c4ca570a9dde" controls="controls" style="max-width: 730px;"></video>

## Who Should Use Mirascope?

Mirascope is __designed for everyone__ to use!

However, we believe that the value of Mirascope will shine in particular for:

- __Professional Developers__: Who need fine-grained control and transparency in their LLM interactions.
- __AI Application Builders__: Looking for a tool that can grow with their project from prototype to production.
- __Teams__: Who value clean, maintainable code and want to avoid the "black box" problem of many AI frameworks.
- __Researchers and Experimenters__: Who need the flexibility to quickly try out new ideas without fighting their tools.

## Getting Started

[:material-clock-fast: Getting Started](./index.md){: .md-button }
[:material-school: Learn](./learn/index.md){: .md-button }
[:material-account-group: Join Our Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA){: .md-button }

By choosing Mirascope, you're opting for a tool that respects your expertise as a developer while providing the conveniences you need to work efficiently and effectively with LLMs.

We believe the best tools get out of your way and let you focus on building great applications.
