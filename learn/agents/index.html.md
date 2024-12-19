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
                from mirascope.core import Messages, openai
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, anthropic
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, mistral
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, gemini
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, groq
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, cohere
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, litellm
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, azure
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, bedrock
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, openai
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, anthropic
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, mistral
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, gemini
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, groq
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, cohere
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, litellm
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, azure
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import Messages, bedrock
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> Messages.Type:
                        return [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, openai, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    @openai.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, anthropic, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, mistral, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    @mistral.call("mistral-large-latest")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, gemini, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    @gemini.call("gemini-1.5-flash")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, groq, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    @groq.call("llama-3.1-70b-versatile")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, cohere, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    @cohere.call("command-r-plus")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, litellm, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    @litellm.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, azure, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    @azure.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, prompt_template, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    @vertex.call("gemini-1.5-flash")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="6 12 26-29"
                from mirascope.core import Messages, bedrock, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str): ...

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                Messages.User(query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, openai
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> list[openai.OpenAIMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> list[anthropic.AnthropicMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, mistral
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> list[mistral.MistralMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, gemini
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> list[gemini.GeminiMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, groq
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> list[groq.GroqMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, cohere
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> list[cohere.CohereMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, litellm
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> list[litellm.LiteLLMMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, azure
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> list[azure.AzureMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> list[vertex.VertexMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="6 12 24-27"
                from mirascope.core import BaseMessageParam, bedrock
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> list[bedrock.BedrockMessageParam]:
                        return [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            response = self._call(query)
                            print(response.content)
                            self.history += [
                                BaseMessageParam(role="user", content=query),
                                response.message_param,
                            ]


                Librarian().run()
            ```

In this example we:

- Create a `Librarian` class with a `history` attribute.
- Implement a private `_call` method that injects `history`.
- Run the `_call` method in a loop, saving the history at each step.

A chatbot with memory, while more advanced, is still not an agent.

??? tip "Provider-agnostic agent"

    === "Shorthand"

        ```python hl_lines="15-16 27-34"
            from typing import Literal

            from mirascope.core import (
                BaseMessageParam,
                Messages,
                anthropic,
                openai,
                prompt_template,
            )
            from mirascope.core.base import BaseCallResponse
            from pydantic import BaseModel


            class Librarian(BaseModel):
                provider: Literal["openai", "anthropic"]
                model: Literal["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
                history: list[BaseMessageParam] = []

                @prompt_template()
                def _prompt(self, query: str) -> Messages.Type:
                    return [
                        Messages.System("You are a librarian"),
                        *self.history,
                        Messages.User(query),
                    ]

                def _call(self, query: str) -> BaseCallResponse:
                    if self.provider == "openai":
                        call = openai.call(self.model)(self._prompt)
                    elif self.provider == "anthropic":
                        call = anthropic.call(self.model)(self._prompt)
                    else:
                        raise ValueError(f"Unsupported provider: {self.provider}")
                    return call(query)

                def run(self) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = self._call(query)
                        print(response.content)
                        self.history += [
                            Messages.User(query),
                            response.message_param,
                        ]


            Librarian(provider="openai", model="gpt-4o-mini").run()
        ```

    === "Messages"

        ```python hl_lines="15-16 27-34"
            from typing import Literal

            from mirascope.core import (
                BaseMessageParam,
                Messages,
                anthropic,
                openai,
                prompt_template,
            )
            from mirascope.core.base import BaseCallResponse
            from pydantic import BaseModel


            class Librarian(BaseModel):
                provider: Literal["openai", "anthropic"]
                model: Literal["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
                history: list[BaseMessageParam] = []

                @prompt_template()
                def _prompt(self, query: str) -> Messages.Type:
                    return [
                        Messages.System("You are a librarian"),
                        *self.history,
                        Messages.User(query),
                    ]

                def _call(self, query: str) -> BaseCallResponse:
                    if self.provider == "openai":
                        call = openai.call(self.model)(self._prompt)
                    elif self.provider == "anthropic":
                        call = anthropic.call(self.model)(self._prompt)
                    else:
                        raise ValueError(f"Unsupported provider: {self.provider}")
                    return call(query)

                def run(self) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = self._call(query)
                        print(response.content)
                        self.history += [
                            Messages.User(query),
                            response.message_param,
                        ]


            Librarian(provider="openai", model="gpt-4o-mini").run()
        ```

    === "String Template"

        ```python hl_lines="15-16 28-35"
            from typing import Literal

            from mirascope.core import (
                BaseMessageParam,
                Messages,
                anthropic,
                openai,
                prompt_template,
            )
            from mirascope.core.base import BaseCallResponse
            from pydantic import BaseModel


            class Librarian(BaseModel):
                provider: Literal["openai", "anthropic"]
                model: Literal["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
                history: list[BaseMessageParam] = []

                @prompt_template(
                    """
                    SYSTEM: You are a librarian
                    MESSAGES: {self.history}
                    USER: {query}
                    """
                )
                def _prompt(self, query: str): ...

                def _call(self, query: str) -> BaseCallResponse:
                    if self.provider == "openai":
                        call = openai.call(self.model)(self._prompt)
                    elif self.provider == "anthropic":
                        call = anthropic.call(self.model)(self._prompt)
                    else:
                        raise ValueError(f"Unsupported provider: {self.provider}")
                    return call(query)

                def run(self) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = self._call(query)
                        print(response.content)
                        self.history += [
                            Messages.User(query),
                            response.message_param,
                        ]


            Librarian(provider="openai", model="gpt-4o-mini").run()
        ```

    === "BaseMessageParam"

        ```python hl_lines="9-10 21-28"
            from typing import Literal

            from mirascope.core import BaseMessageParam, anthropic, openai, prompt_template
            from mirascope.core.base import BaseCallResponse
            from pydantic import BaseModel


            class Librarian(BaseModel):
                provider: Literal["openai", "anthropic"]
                model: Literal["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
                history: list[BaseMessageParam] = []

                @prompt_template()
                def _prompt(self, query: str) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(role="system", content="You are a librarian"),
                        *self.history,
                        BaseMessageParam(role="user", content=(query)),
                    ]

                def _call(self, query: str) -> BaseCallResponse:
                    if self.provider == "openai":
                        call = openai.call(self.model)(self._prompt)
                    elif self.provider == "anthropic":
                        call = anthropic.call(self.model)(self._prompt)
                    else:
                        raise ValueError(f"Unsupported provider: {self.provider}")
                    return call(query)

                def run(self) -> None:
                    while True:
                        query = input("(User): ")
                        if query in ["exit", "quit"]:
                            break
                        print("(Assistant): ", end="", flush=True)
                        response = self._call(query)
                        print(response.content)
                        self.history += [
                            BaseMessageParam(role="user", content=query),
                            response.message_param,
                        ]


            Librarian(provider="openai", model="gpt-4o-mini").run()
        ```


## Integrating Tools

The next concept to cover is introducing tools to our chatbot, turning it into an agent capable of acting on our behalf. The most basic agent flow is to call tools on behalf of the agent, providing them back through the chat history until the agent is ready to response to the initial query.

Let's take a look at a basic example where the `Librarian` can access the books available in the library:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, openai, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, anthropic, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, mistral, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, gemini, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, groq, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, cohere, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, litellm, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, azure, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, prompt_template, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="14-17 19-21 32 39-45"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, bedrock, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="14-17 19-21 30 37-43"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
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
                from mirascope.core import BaseDynamicConfig, Messages, openai
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, anthropic
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, mistral
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, gemini
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, groq
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, cohere
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, litellm
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, azure
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, bedrock
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, openai
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, anthropic
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, mistral
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, gemini
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, groq
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, cohere
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, litellm
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, azure
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, Messages, bedrock
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, openai, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @openai.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, anthropic, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, mistral, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @mistral.call("mistral-large-latest")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, gemini, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @gemini.call("gemini-1.5-flash")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, groq, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @groq.call("llama-3.1-70b-versatile")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, cohere, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @cohere.call("command-r-plus")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, litellm, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @litellm.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, azure, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @azure.call("gpt-4o-mini")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, prompt_template, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @vertex.call("gemini-1.5-flash")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="8-14 25"
                from mirascope.core import BaseDynamicConfig, Messages, bedrock, prompt_template
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _call(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(Messages.User(query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, openai
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @openai.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @anthropic.call("claude-3-5-sonnet-20240620")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, mistral
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @mistral.call("mistral-large-latest")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, gemini
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @gemini.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, groq
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @groq.call("llama-3.1-70b-versatile")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, cohere
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @cohere.call("command-r-plus")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, litellm
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @litellm.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, azure
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @azure.call("gpt-4o-mini")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, vertex
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @vertex.call("gemini-1.5-flash")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="8-14 23"
                from mirascope.core import BaseDynamicConfig, BaseMessageParam, bedrock
                from pydantic import BaseModel


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []

                    def _ask_for_help(self, question: str) -> str:
                        """Asks for help from an expert."""
                        print("[Assistant Needs Help]")
                        print(f"[QUESTION]: {question}")
                        answer = input("[ANSWER]: ")
                        print("[End Help]")
                        return answer

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                    def _call(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._ask_for_help]}

                    def _step(self, query: str) -> str:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        response = self._call(query)
                        self.history.append(response.message_param)
                        tools_and_outputs = []
                        if tools := response.tools:
                            for tool in tools:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            self.history += response.tool_message_params(tools_and_outputs)
                            return self._step("")
                        else:
                            return response.content

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            step_output = self._step(query)
                            print(step_output)


                Librarian().run()
            ```

## Streaming

The previous examples print each tool call so you can see what the agent is doing before the final response; however, you still need to wait for the agent to generate its entire final response before you see the output.

Streaming can help to provide an even more real-time experience:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
    === "Messages"

        === "OpenAI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, bedrock
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            Messages.System("You are a librarian"),
                            *self.history,
                            Messages.User(query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
    === "String Template"

        === "OpenAI"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, openai, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, anthropic, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, mistral, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, gemini, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, groq, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, cohere, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, litellm, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, azure, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, prompt_template, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="23 31 37-48"
                import json

                from mirascope.core import BaseDynamicConfig, Messages, bedrock, prompt_template
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                    @prompt_template(
                        """
                        SYSTEM: You are a librarian
                        MESSAGES: {self.history}
                        USER: {query}
                        """
                    )
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        return {"tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(Messages.User(query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, openai
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[openai.OpenAIMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @openai.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Anthropic"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, anthropic
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[anthropic.AnthropicMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Mistral"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, mistral
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[mistral.MistralMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @mistral.call("mistral-large-latest", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Gemini"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, gemini
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[gemini.GeminiMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @gemini.call("gemini-1.5-flash", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Groq"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, groq
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[groq.GroqMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @groq.call("llama-3.1-70b-versatile", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Cohere"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, cohere
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[cohere.CohereMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @cohere.call("command-r-plus", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "LiteLLM"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, litellm
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[litellm.LiteLLMMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @litellm.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Azure AI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, azure
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[azure.AzureMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @azure.call("gpt-4o-mini", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Vertex AI"

            ```python hl_lines="23 24 35-46"
                import json

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, vertex
                from pydantic import BaseModel


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[vertex.VertexMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @vertex.call("gemini-1.5-flash", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += stream.tool_message_params(tools_and_outputs)
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```
        === "Bedrock"

            ```python hl_lines="23 24 35-46"
                import json
                from typing import cast

                from mirascope.core import BaseDynamicConfig, BaseMessageParam, bedrock
                from pydantic import BaseModel

                from mirascope.core.bedrock._types import ToolResultBlockMessageTypeDef


                class Book(BaseModel):
                    title: str
                    author: str


                class Librarian(BaseModel):
                    history: list[bedrock.BedrockMessageParam] = []
                    library: list[Book] = [
                        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
                        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
                    ]

                    def _available_books(self) -> str:
                        """Returns the list of books available in the library."""
                        return json.dumps([book.model_dump() for book in self.library])

                    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                    def _stream(self, query: str) -> BaseDynamicConfig:
                        messages = [
                            BaseMessageParam(role="system", content="You are a librarian"),
                            *self.history,
                            BaseMessageParam(role="user", content=query),
                        ]
                        return {"messages": messages, "tools": [self._available_books]}

                    def _step(self, query: str) -> None:
                        if query:
                            self.history.append(BaseMessageParam(role="user", content=query))
                        stream = self._stream(query)
                        tools_and_outputs = []
                        for chunk, tool in stream:
                            if tool:
                                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                                tools_and_outputs.append((tool, tool.call()))
                            else:
                                print(chunk.content, end="", flush=True)
                        self.history.append(stream.message_param)
                        if tools_and_outputs:
                            self.history += cast(
                                list[ToolResultBlockMessageTypeDef],
                                stream.tool_message_params(tools_and_outputs),
                            )
                            self._step("")

                    def run(self) -> None:
                        while True:
                            query = input("(User): ")
                            if query in ["exit", "quit"]:
                                break
                            print("(Assistant): ", end="", flush=True)
                            self._step(query)
                            print()


                Librarian().run()
            ```

## Next Steps

This section is just the tip of the iceberg when it comes to building agents, implementing just one type of simple agent flow. It's important to remember that "agent" is quite a general term and can mean different things for different use-cases. Mirascope's various features make building agents easier, but it will be up to you to determine the architecture that best suits your goals.

Next, we recommend taking a look at our [Agent Tutorials](../tutorials/agents/web_search_agent.ipynb) to see examples of more complex, real-world agents.
