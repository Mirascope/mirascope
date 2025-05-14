---
search:
  boost: 2
---

# Agents

> __Definition__: a person who acts on behalf of another person or group

When working with Large Language Models (LLMs), an "agent" refers to an autonomous or semi-autonomous system that can act on your behalf. The core concept is the use of tools to enable the LLM to interact with its environment.

In this section we will implement a toy `Librarian` agent to demonstrate key concepts in Mirascope that will help you build agents.

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Tools](./tools.md)
    </div>

??? info "Diagram illustrating the agent flow"

    ```mermaid
    sequenceDiagram
        participant YC as Your Code
        participant LLM

        loop Agent Loop
            YC->>LLM: Call with prompt + history + function definitions
            loop Tool Calling Cycle
                LLM->>LLM: Decide to respond or call functions
                LLM->>YC: Respond with function to call and arguments
                YC->>YC: Execute function with given arguments
                YC->>YC: Add tool call message parameters to history
                YC->>LLM: Call with prompt + history including function result
            end
            LLM->>YC: Finish calling tools and return final response
            YC->>YC: Update history with final response
        end
    ```

## State Management

Since an agent needs to operate across multiple LLM API calls, the first concept to cover is state. The goal of providing state to the agent is to give it memory. For example, we can think of local variables as "working memory" and a database as "long-term memory".

Let's take a look at a basic chatbot (not an agent) that uses a class to maintain the chat's history:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/bedrock/shorthand.py

            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/bedrock/messages.py

            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="6 12 26-29"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/bedrock/string_template.py

            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="6 12 24-27"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/state_management/bedrock/base_message_param.py

            ```

In this example we:

- Create a `Librarian` class with a `history` attribute.
- Implement a private `_call` method that injects `history`.
- Run the `_call` method in a loop, saving the history at each step.

A chatbot with memory, while more advanced, is still not an agent.

??? tip "Provider-Agnostic Agent"

    === "Shorthand"

        ```python hl_lines="18-19 26"
            from mirascope import BaseMessageParam, Messages, llm
            from pydantic import BaseModel


            class Librarian(BaseModel):
                history: list[BaseMessageParam] = []

                @llm.call(provider="openai", model="gpt-4o-mini")
                def _call(self, query: str) -> Messages.Type:
                    return [
                        Messages.System("You are a librarian"),
                        *self.history,
                        Messages.User(query),
                    ]

                def run(
                    self,
                    provider: llm.Provider,
                    model: str,
                ) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = llm.override(self._call, provider=provider, model=model)(query)
                        print(response.content)
                        self.history += [
                            response.user_message_param,
                            response.message_param,
                        ]


            Librarian().run("anthropic", "claude-3-5-sonnet-latest")
        ```

    === "Messages"

        ```python hl_lines="18-19 26"
            from mirascope import BaseMessageParam, Messages, llm
            from pydantic import BaseModel


            class Librarian(BaseModel):
                history: list[BaseMessageParam] = []

                @llm.call(provider="openai", model="gpt-4o-mini")
                def _call(self, query: str) -> Messages.Type:
                    return [
                        Messages.System("You are a librarian"),
                        *self.history,
                        Messages.User(query),
                    ]

                def run(
                    self,
                    provider: llm.Provider,
                    model: str,
                ) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = llm.override(self._call, provider=provider, model=model)(query)
                        print(response.content)
                        self.history += [
                            response.user_message_param,
                            response.message_param,
                        ]


            Librarian().run("anthropic", "claude-3-5-sonnet-latest")
        ```

    === "String Template"

        ```python hl_lines="20-21 28"
            from mirascope import BaseMessageParam, llm, prompt_template
            from pydantic import BaseModel


            class Librarian(BaseModel):
                history: list[BaseMessageParam] = []

                @llm.call(provider="openai", model="gpt-4o-mini")
                @prompt_template(
                    """
                    SYSTEM: You are a librarian
                    MESSAGES: {self.history}
                    USER: {query}
                    """
                )
                def _call(self, query: str): ...

                def run(
                    self,
                    provider: llm.Provider,
                    model: str,
                ) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = llm.override(self._call, provider=provider, model=model)(query)
                        print(response.content)
                        self.history += [
                            response.user_message_param,
                            response.message_param,
                        ]


            Librarian().run("anthropic", "claude-3-5-sonnet-latest")
        ```

    === "BaseMessageParam"

        ```python hl_lines="18-19 26"
            from mirascope import BaseMessageParam, llm
            from pydantic import BaseModel


            class Librarian(BaseModel):
                history: list[BaseMessageParam] = []

                @llm.call(provider="openai", model="gpt-4o-mini")
                def _call(self, query: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(role="system", content="You are a librarian"),
                        *self.history,
                        BaseMessageParam(role="user", content=(query)),
                    ]

                def run(
                    self,
                    provider: llm.Provider,
                    model: str,
                ) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = llm.override(self._call, provider=provider, model=model)(query)
                        print(response.content)
                        self.history += [
                            response.user_message_param,
                            response.message_param,
                        ]


            Librarian().run("anthropic", "claude-3-5-sonnet-latest")
        ```


## Integrating Tools

The next concept to cover is introducing tools to our chatbot, turning it into an agent capable of acting on our behalf. The most basic agent flow is to call tools on behalf of the agent, providing them back through the chat history until the agent is ready to response to the initial query.

Let's take a look at a basic example where the `Librarian` can access the books available in the library:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/bedrock/shorthand.py

            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/bedrock/messages.py

            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="19-23 25-27 38 45-51"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/bedrock/string_template.py

            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="14-17 19-21 30 37-43"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/tools/bedrock/base_message_param.py

            ```

In this example we:

1. Added the `library` state to maintain the list of available books.
2. Implemented the `_available_books` tool that returns the library as a string.
3. Updated `_call` to give the LLM access to the tool.
    - We used the `tools` dynamic configuration field so the tool has access to the library through `self`.
4. Added a `_step` method that implements a full step from user input to assistant output.
5. For each step, we call the LLM and see if there are any tool calls.
    - If yes, we call the tools, collect the outputs, and insert the tool calls into the chat history. We then recursively call `_step` again with an empty user query until the LLM is done calling tools and is ready to response
    - If no, the LLM is ready to respond and we return the response content.

Now that our chatbot is capable of using tools, we have a basic agent.

## Human-In-The-Loop

While it would be nice to have fully autonomous agents, LLMs are far from perfect and often need assistance to ensure they continue down the right path in an agent flow.

One common and easy way to help guide LLM agents is to give the agent the ability to ask for help. This "human-in-the-loop" flow lets the agent ask for help if it determines it needs it:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/bedrock/shorthand.py

            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/bedrock/messages.py

            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="14-20 31"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/bedrock/string_template.py

            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="8-14 23"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/human_in_the_loop/bedrock/base_message_param.py

            ```

## Streaming

The previous examples print each tool call so you can see what the agent is doing before the final response; however, you still need to wait for the agent to generate its entire final response before you see the output.

Streaming can help to provide an even more real-time experience:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/bedrock/shorthand.py

            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/bedrock/messages.py

            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="29 37 43-54"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/bedrock/string_template.py

            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="23 24 35-46"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/agents/streaming/bedrock/base_message_param.py

            ```

## Next Steps

This section is just the tip of the iceberg when it comes to building agents, implementing just one type of simple agent flow. It's important to remember that "agent" is quite a general term and can mean different things for different use-cases. Mirascope's various features make building agents easier, but it will be up to you to determine the architecture that best suits your goals.

Next, we recommend taking a look at our [Agent Tutorials](../tutorials/agents/web_search_agent.ipynb) to see examples of more complex, real-world agents.
