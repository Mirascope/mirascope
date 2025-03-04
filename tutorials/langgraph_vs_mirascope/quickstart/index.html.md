# LangGraph Quickstart using Mirascope

We'll implement the [LangGraph Quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/) using Mirascope. We'll build a chatbot with a web search tool, conversation history, and human-in-the-loop functionality. Throughout the process, we'll apply Mirascope best practices, which align with general Python best practices. This approach will demonstrate how straightforward it is to create a sophisticated conversational AI system using Mirascope.

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[openai]"
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Part 1: Building a Basic Chatbot

A chatbot must possess at least two key capabilities to be considered as such:

* The ability to engage in conversation with a user
* The capacity to retain and reference information from the ongoing dialogue

Let's take a look at how that looks using Mirascope:


```python
from mirascope.core import BaseMessageParam, openai, prompt_template
from pydantic import BaseModel


class Chatbot(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []

    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM: You are a helpful assistant.
        MESSAGES: {self.history}
        USER: {question}
        """
    )
    def _call(self, question: str): ...

    def run(self):
        while True:
            question = input("(User): ")
            if question in ["quit", "exit"]:
                print("(Assistant): Have a great day!")
                break
            stream = self._call(question)
            print(f"(User): {question}", flush=True)
            print("(Assistant): ", end="", flush=True)
            for chunk, _ in stream:
                print(chunk.content, end="", flush=True)
            print("")
            if stream.user_message_param:
                self.history.append(stream.user_message_param)
            self.history.append(stream.message_param)


Chatbot().run()
```

    (User): Hi there! My name is Will
    (Assistant): Hi Will! How can I assist you today?
    (User): Remember my name?
    (Assistant): Yes, your name is Will! What would you like to talk about today?
    (Assistant): Have a great day!



The `run` method serves as the entry point for our Chatbot. It implements a continuous loop that:

1. Prompts the user for input
2. Processes the user's message
3. Generates and streams the assistant's response for a real time feel
4. Updates the conversation history

This loop persists until the user chooses to exit. After each interaction, both the user's input and the assistant's response are appended to the history list. This accumulation of context allows the language model to maintain continuity and relevance in future conversations.

While this basic chatbot demonstrates core functionality, we can enhance its capabilities by incorporating tools.

## Part 2: Enhancing the Chatbot with Tools

Tools enable language models to extend beyond their training data and access real-time information. Let's implement a `WebSearch` tool that allows the LLM to query the internet for current and relevant data.

Here are a few search tools you can use.

### DuckDuckGo

#### DuckDuckGo Setup

Install the [DuckDuckGo](https://duckduckgo.com/) python library:




```python
!pip install duckduckgo-search beautifulsoup4 requests
```


No API key is required for DuckDuckGo.

#### Define the DuckDuckGo tool



```python
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field


class WebSearch(openai.OpenAITool):
    """Search the web for the given text and parse the paragraphs of the results."""

    query: str = Field(..., description="The text to search for.")

    def call(self) -> str:
        """Search the web for the given text and parse the paragraphs of the results.

        Returns:
            Parsed paragraphs of each of the webpages, separated by newlines.
        """
        try:
            # Search the web for the given text
            results = DDGS(proxy=None).text(self.query, max_results=2)

            # Parse the paragraphs of each resulting webpage
            parsed_results = []
            for result in results:
                link = result["href"]
                try:
                    response = requests.get(link)
                    soup = BeautifulSoup(response.content, "html.parser")
                    parsed_results.append(
                        "\n".join([p.text for p in soup.find_all("p")])
                    )
                except Exception as e:
                    parsed_results.append(
                        f"{type(e)}: Failed to parse content from URL {link}"
                    )

            return "\n\n".join(parsed_results)

        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"
```


### Tavily

#### Tavily Setup

Install the [Tavily](https://tavily.com/) python library:



```python
!pip install tavily-python
```


Then get a free API key to use for the `WebSearch` tool.

#### Define the Tavily tool



```python
import os
from typing import ClassVar

from pydantic import Field
from tavily import TavilyClient


class WebSearch(openai.OpenAITool):  # noqa: F811
    """Search the web for the given text using the TavilyClient."""

    tavily_client: ClassVar[TavilyClient] = TavilyClient(
        api_key=os.environ["TAVILY_API_KEY"]
    )
    query: str = Field(..., description="The text to search for.")

    def call(self) -> str:
        """A web search tool that takes in a query and returns the top 2 search results."""
        return self.tavily_client.get_search_context(query=self.query, max_results=2)
```


### Update Mirascope call

Now that we have our tool defined, we can easily add the tool to our Mirascope call, like so:



```python
class Chatbot(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []

    @openai.call(model="gpt-4o-mini", stream=True, tools=[WebSearch])
    @prompt_template(
        """
        SYSTEM:
        You are an expert web searcher. 
        Your task is to answer the user's question using the provided tools.
        You have access to the following tools:
            - `WebSearch`: Search the web for information.
            - `RequestAssistance`: Request assistance from a human expert if you do not
                know how to answer the question.

        Once you have gathered all of the information you need, generate a writeup that
        strikes the right balance between brevity and completeness. The goal is to
        provide as much information to the writer as possible without overwhelming them.

        MESSAGES: {self.history}
        USER: {question}
        """
    )
    def _call(self, question: str | None = None): ...

    def _step(self, question: str | None = None):
        response = self._call(question)
        tools_and_outputs = []
        for chunk, tool in response:
            if tool:
                tools_and_outputs.append((tool, tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        if response.user_message_param:
            self.history.append(response.user_message_param)
        self.history.append(response.message_param)
        if tools_and_outputs:
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step()
        return response.content

    def run(self):
        while True:
            question = input("(User): ")
            if question in ["quit", "exit"]:
                print("(Assistant): Have a great day!")
                break
            print("(Assistant): ", end="", flush=True)
            self._step(question)
            print("")


Chatbot().run()
# Prompt:
"""
(User): Can you tell me about the Mirascope python library?
(Assistant): The **Mirascope** library is a Python toolkit designed for creating applications using language model (LLM) APIs. Developed by William Bakst and released on August 18, 2024, Mirascope emphasizes simplicity, elegance, and developer experience. Here are some key features and details about the library:

### Key Features
1. **Simplicity and Ease of Use**: Mirascope aims to provide straightforward abstractions that enhance the developer experience without overwhelming complexity. It is designed for ease of onboarding and development.

2. **Type Safety**: One of its strengths is the provision of proper type hints throughout the library. It actively manages Python typings, allowing developers to write their code intuitively while still benefiting from type safety.

3. **Modular Design**: Mirascope is modular and extensible, enabling developers to tailor the library to their specific needs. Most dependencies are optional and provider-specific, so you can include only the components you require.

4. **Core Primitives**: The library offers two main components:
   - **Call and BasePrompt**: These primitives facilitate interactions with LLMs. Developers can create functions that integrate seamlessly with multiple LLM providers through decorators.

5. **Advanced Functionality**: Mirascope supports features like asynchronous function calls, streaming responses, structured data extraction, custom output parsers, and dynamic variable injection.

6. **Integration with FastAPI**: Mirascope includes decorators for wrapping functions into FastAPI routes, making it easier to deploy applications as web services.

7. **Documentation and Examples**: The project comes with extensive usage documentation and example code to help users quickly understand how to utilize its features effectively.

### Installation
To install Mirascope, you can use the following command:
```bash
pip install mirascope
```
### Compatibility
Mirascope is compatible with Python versions 3.10 to 3.11 (not supporting Python 4.0 and above) and is licensed under the MIT License.

### Summary
Mirascope positions itself as a simpler, less cumbersome alternative to other LLM frameworks like LangChain. It focuses on providing essential functionalities without unnecessary complexity, making development enjoyable and productive for software engineers looking to integrate LLMs into their applications.
"""
```


We have enhanced our chatbot's functionality with several key modifications:

* Added a `WebSearch` tool to the tools parameter in the `@openai.call` decorator.
* Refactored the streaming logic and history management into a new `_step` method.
    * This enables calling `_step` iteratively until the agent is done calling tools and is ready to respond.
    * For each `_step` we update the history to include tool usage and outputs.
* Revised the prompt template to instruct the chatbot on how to utilize the new `WebSearch` tool.

## Part 3: Human-in-the-loop

Let us take a look at how we can slot in human input or approval using Mirascope.

### Permission before using tool

Since we are just writing python code, we don't need to setup an `interrupt_before`. We can simply add a function `_interrupt_before` that we call before calling our tool, like so:



```python
class Chatbot(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []

    @openai.call(model="gpt-4o-mini", stream=True, tools=[WebSearch])
    @prompt_template(
        """
        SYSTEM:
        You are an expert web searcher. 
        Your task is to answer the user's question using the provided tools.
        You have access to the following tools:
            - `WebSearch`: Search the web for information.
            - `RequestAssistance`: Request assistance from a human expert if you do not
                know how to answer the question.

        Once you have gathered all of the information you need, generate a writeup that
        strikes the right balance between brevity and completeness. The goal is to
        provide as much information to the writer as possible without overwhelming them.

        MESSAGES: {self.history}
        USER: {question}
        """
    )
    def _call(self, question: str | None = None): ...

    def _interrupt_before(self, tool: openai.OpenAITool) -> openai.OpenAITool | None:
        """Interrupt before the tool is called. Return the modified tool or None."""
        if not isinstance(tool, WebSearch):
            return tool
        response = input(f"Do you want to use the {tool._name()} tool? (y/n): ")
        if response.lower() in ["n", "no"]:
            response = input(
                f"Do you want to modify the {tool._name()} tool's query? (y/n): "
            )
            if response.lower() in ["n", "no"]:
                return None
            else:
                tool.query = input("(Assistant): Enter a new query: ")
                return tool
        else:
            return tool

    def _step(self, question: str | None = None):
        response = self._call(question)
        tools_and_outputs = []
        for chunk, tool in response:
            if tool:
                new_tool = self._interrupt_before(tool)
                if new_tool:
                    tools_and_outputs.append((new_tool, new_tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        if response.user_message_param:
            self.history.append(response.user_message_param)
        self.history.append(response.message_param)
        if tools_and_outputs:
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step()
        return response.content

    def run(self):
        while True:
            question = input("(User): ")
            if question in ["quit", "exit"]:
                print("(Assistant): Have a great day!")
                break
            print("(Assistant): ", end="", flush=True)
            self._step(question)
            print("")
```

Now, before the LLM calls the tool, it will prompt the user requesting permission:



```python
Chatbot().run()
# > (User): Can you tell me about the Mirascope python library?
# > (Assistant): Do you want to use the WebSearch tool? (y/n): y
```

### Human-as-a-tool

We can use prompt engineering techniques to help the LLM make a decision on whether it needs human intervention or not. Let's add a `RequestAssistance` tool and update our prompt so the LLM knows how to use our new tool.




```python
class RequestAssistance(openai.OpenAITool):
    """A tool that requests assistance from a human expert."""

    query: str = Field(
        ...,
        description="The request for assistance needed to properly respond to the user",
    )

    def call(self) -> str:
        """Prompts a human to enter a response."""
        print(f"I am in need of assistance. {self.query}")
        response = input("\t(Human): ")
        return f"Human response: {response}"


class Chatbot(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []

    @openai.call(model="gpt-4o-mini", stream=True, tools=[WebSearch, RequestAssistance])
    @prompt_template(
        """
        SYSTEM:
        You are an expert web searcher. 
        Your task is to answer the user's question using the provided tools.
        You have access to the following tools:
            - `WebSearch`: Search the web for information.
            - `RequestAssistance`: Request assistance from a human expert if you do not
                know how to answer the question.

        Once you have gathered all of the information you need, generate a writeup that
        strikes the right balance between brevity and completeness. The goal is to
        provide as much information to the writer as possible without overwhelming them.

        MESSAGES: {self.history}
        USER: {question}
        """
    )
    def _call(self, question: str | None = None): ...

    def _interrupt_before(self, tool: openai.OpenAITool) -> openai.OpenAITool | None:
        """Interrupt before the tool is called. Return the modified tool or None."""
        if not isinstance(tool, WebSearch):
            return tool
        response = input(f"Do you want to use the {tool._name()} tool? (y/n): ")
        if response.lower() in ["n", "no"]:
            response = input(
                f"Do you want to modify the {tool._name()} tool's query? (y/n): "
            )
            if response.lower() in ["n", "no"]:
                return None
            else:
                tool.query = input("(Assistant): Enter a new query: ")
                return tool
        else:
            return tool

    def _step(self, question: str | None = None):
        response = self._call(question)
        tools_and_outputs = []
        for chunk, tool in response:
            if tool:
                new_tool = self._interrupt_before(tool)
                if new_tool:
                    tools_and_outputs.append((new_tool, new_tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        if response.user_message_param:
            self.history.append(response.user_message_param)
        self.history.append(response.message_param)
        if tools_and_outputs:
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step()
        return response.content

    def run(self):
        while True:
            question = input("(User): ")
            if question in ["quit", "exit"]:
                print("(Assistant): Have a great day!")
                break
            print("(Assistant): ", end="", flush=True)
            self._step(question)
            print("")


Chatbot().run()
# > (User): What is my name?
# > (Assistant): I am in need of assistance. How to identify a user's name in a conversation without them explicitly stating it?
#       (Human): Tell them you don't know their name and would love for them to share it with you
#   I’m not sure what your name is. I would love to know, so please feel free to share it!
# > (User):
```


<div class="admonition note">
<p class="admonition-title">Real-World Difference</p>
<p>
In the above example, we are getting the "Human" input in the console for demonstration purposes. In a real-world use-case, this would be hidden from the user and simply mention that the AI is requesting assistance while actually requesting assistance in the background (where the user would not see this interaction).
</p>
</div>

## Part 4: Time Travel also known as list splicing

In order to revisit previous states, you can take the history list that stores all the messages and manipulate it however you want by basic list splicing.
For example, if you want to "rewind" your state, you can simply remove user and assistant messages and then run your chatbot.



```python
chatbot = Chatbot()
chatbot.run()
# (User): Hi there! My name is Will.
# (Assistant): It's nice to meet you, Will! I'm an AI assistant created by Anthropic. I'm here to help you with any questions or tasks you may have. Please let me know how I can assist you today.


chatbot.run()
# (User): Remember my name?
# (Assistant): Of course, your name is Will. It's nice to meet you again!

chatbot.history = chatbot.history[:-4]
# (User): Remember my name?
# (Assistant): I'm afraid I don't actually have the capability to remember your name. As an AI assistant, I don't have a persistent memory of our previous conversations or interactions. I respond based on the current context provided to me. Could you please restate your name or provide more information so I can try to assist you?
```



While in this example, we are calling the run function multiple times, there is nothing stopping you from updating the history inside the Chatbot. Note that in real-world applications, conversation history is typically stored in a cache, database, or other persistent storage systems, so add `computed_fields` as necessary to retrieve from storage.

<div class="admonition note">
<p class="admonition-title">Dynamic, Relevant History</p>
<p>
We have seen cases where the history is retrieved dynamically from e.g. a vector store. This enables injecting only relevant history along with each call, which can help reduce token usage and keep the assistant's responses more relevant.
</p>
</div>

Congratulations! You've now learned how to create a sophisticated chatbot using Mirascope and simple Python code. This approach demonstrates that powerful AI applications can be built with minimal reliance on complex abstractions or pre-built tools, giving you greater flexibility and control over your project's architecture.

