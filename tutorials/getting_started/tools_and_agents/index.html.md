# Tools & Agents

Tools and Agents are two key concepts in building advanced AI systems, particularly those involving Large Language Models (LLMs):

- **Tools**: Functions that extend the capabilities of LLMs, allowing them to perform specific tasks or access external data.
- **Agents**: Autonomous or semi-autonomous entities that use LLMs and Tools to perform complex tasks or interact with users.

In this notebook we'll implement a `WebSearchAgent` to demonstrate how to built Agents in Mirascope using Tools.

For more detailed information on these concepts, refer to the following Mirascope documentation:

- [Tools documentation](../../../learn/tools)
- [Agents documentation](../../../learn/agents)

## Setting Up the Environment

First, let's set up our environment by installing Mirascope and other necessary libraries.


```python
!pip install "mirascope[openai]" duckduckgo_search beautifulsoup4 requests
```


```python
import os

os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

For more information on setting up Mirascope and its dependencies, see the [Mirascope getting started guide](../quickstart).

## Building a Basic Chatbot

Before we dive into Tools and Agents, let's start by building a basic chatbot. This will help us understand the fundamental concepts of state management and conversation flow in Mirascope.


```python
from mirascope.core import Messages, openai
from pydantic import BaseModel


class BasicChatbot(BaseModel):
    messages: list[openai.OpenAIMessageParam] = []

    @openai.call(model="gpt-4o-mini")
    async def chat(self, user_input: str) -> openai.OpenAIDynamicConfig:
        messages = [
            Messages.System(
                "You are a friendly chatbot assistant. Engage in a conversation with the user."
            ),
            *self.messages,
            Messages.User(user_input),
        ]
        return {"messages": messages}

    async def run(self):
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break
            response = await self.chat(user_input)
            print(f"User: {user_input}")
            print(f"Chatbot: {response.content}")
            self.messages.append(response.user_message_param)
            self.messages.append(response.message_param)


# Usage
chatbot = BasicChatbot()
# Run the chatbot in a Jupyter notebook
await chatbot.run()

# Run the chatbot in a Python script
# import asyncio
# asyncio.run(chatbot.run())
```

    User: Hi!
    Chatbot: Hello! How can I assist you today?
    User: What can you help me with?
    Chatbot: I can help with a variety of things! Whether you have questions about general knowledge, need information on a specific topic, want advice, or even just want to chat, I’m here for you. What’s on your mind?


In this basic chatbot implementation, we've created a `BasicChatbot` class that
1. Maintains a conversation history (`messages`)
2. Uses Mirascope's `@openai.call` decorators to interact with the LLM.

Note that the `chat` method can directly access `self.messages` in the template, allowing for easy integration of the conversation history into the prompt.

The `chat` method is where the LLM interaction occurs. It uses the conversation history and the current user input to generate a response. The `run` method manages the main conversation loop, updating the conversation history after each interaction. We give it the `openai.OpenAIDynamicConfig` return type since we will eventually want to insert tool call message parameters into the history, which will be specific to OpenAI.

This sets the foundation for more complex agents that we'll build upon in the following sections.

## Understanding Tools in Mirascope

Tools in Mirascope are functions that extend the capabilities of LLMs. They allow the LLM to perform specific tasks or access external data. Tools are typically used to:

1. Retrieve information from external sources
2. Perform calculations or data processing
3. Interact with APIs or databases
4. Execute specific actions based on the LLM's decisions

Let's start by creating a Tool that extracts content from a webpage:


```python
import re

import requests
from bs4 import BeautifulSoup


def extract_content(url: str) -> str:
    """Extract the main content from a webpage.

    Args:
        url: The URL of the webpage to extract the content from.

    Returns:
        The extracted content as a string.
    """
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        unwanted_tags = ["script", "style", "nav", "header", "footer", "aside"]
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile("content|main"))
        )
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        lines = (line.strip() for line in text.splitlines())
        return "\n".join(line for line in lines if line)
    except Exception as e:
        return f"{type(e)}: Failed to extract content from URL {url}"
```

This `extract_content` function is a Tool that takes a URL as input and returns the main content of the webpage as a string. It uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) to parse the HTML and extract the relevant text content.

When this function is passed to a Mirascope `call` decorator, it is automatically converted into a `BaseTool` class. This conversion process generates a schema that the LLM API uses to understand and interact with the tool.

Let's take a look at what this schema looks like:


```python
from mirascope.core.openai import OpenAITool

tool_type = OpenAITool.type_from_fn(extract_content)
print(tool_type.tool_schema())
```

    {'function': {'name': 'extract_content', 'description': 'Extract the main content from a webpage.\n\nArgs:\n    url: The URL of the webpage to extract the content from.\n\nReturns:\n    The extracted content as a string.', 'parameters': {'properties': {'url': {'description': 'The URL of the webpage to extract the content from.', 'type': 'string'}}, 'required': ['url'], 'type': 'object'}}, 'type': 'function'}


This schema provides the LLM with information about the tool's name, description, and expected input parameters. The LLM uses this information to determine when and how to use the tool during its reasoning process.

For more details on implementing and using Tools in Mirascope, see the [Tools documentation](../../../learn/tools).

## Tools With Access To Agent State

Now, let's create a more complex Tool that performs web searches using the DuckDuckGo search engine. We'll implement this tool as a method within our agent class to demonstrate how tools can access the agent's state:


```python
from duckduckgo_search import DDGS


class WebSearchAgentBase(BaseModel):
    messages: list[openai.OpenAIMessageParam] = []
    search_history: list[str] = []
    max_results_per_query: int = 2

    def web_search(self, queries: list[str]) -> str:
        """Performs web searches for given queries and returns URLs.

        Args:
            queries: List of search queries.

        Returns:
            str: Newline-separated URLs from search results or error messages.

        Raises:
            Exception: If web search fails entirely.
        """
        try:
            urls = []
            for query in queries:
                results = DDGS(proxies=None).text(
                    query, max_results=self.max_results_per_query
                )
                for result in results:
                    link = result["href"]
                    try:
                        urls.append(link)
                    except Exception as e:
                        urls.append(
                            f"{type(e)}: Failed to parse content from URL {link}"
                        )
            self.search_history.extend(queries)
            return "\n\n".join(urls)
        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"
```

This `web_search` method is a more complex Tool that takes a list of search queries and returns a string of newline-separated URLs from the search results. It uses the DuckDuckGo search API to perform the searches and updates the agent's `search_history`. Luckily, the DuckDuckGo search API does not require an API key, making it easy to use in this example.

By implementing this tool as a method within our `WebSearchAgent` class, we can access and update the agent's state (like `search_history`) directly. This approach allows for more integrated and stateful tool usage within our agent.

## Implementing the WebSearchAgent

Now that we have our custom tools, let's implement the full WebSearchAgent by adding the LLM interaction and main execution flow. Since the prompt is now rather long, we opt to use a string template for enhanced readability:


```python
from datetime import datetime

from mirascope.core import prompt_template


class WebSearchAgent(WebSearchAgentBase):
    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM:
        You are an expert web searcher. Your task is to answer the user's question using the provided tools.
        The current date is {current_date}.

        You have access to the following tools:
        - `web_search`: Search the web when the user asks a question. Follow these steps for EVERY web search query:
            1. There is a previous search context: {self.search_history}
            2. There is the current user query: {question}
            3. Given the previous search context, generate multiple search queries that explores whether the new query might be related to or connected with the context of the current user query. 
                Even if the connection isn't immediately clear, consider how they might be related.
        - `extract_content`: Parse the content of a webpage.

        When calling the `web_search` tool, the `body` is simply the body of the search
        result. You MUST then call the `extract_content` tool to get the actual content
        of the webpage. It is up to you to determine which search results to parse.

        Once you have gathered all of the information you need, generate a writeup that
        strikes the right balance between brevity and completeness based on the context of the user's query.

        MESSAGES: {self.messages}
        USER: {question}
        """
    )
    async def _stream(self, question: str) -> openai.OpenAIDynamicConfig:
        return {
            "tools": [self.web_search, extract_content],
            "computed_fields": {
                "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
        }

    async def _step(self, question: str):
        response = await self._stream(question)
        tools_and_outputs = []
        async for chunk, tool in response:
            if tool:
                print(f"using {tool._name()} tool with args: {tool.args}")
                tools_and_outputs.append((tool, tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        if response.user_message_param:
            self.messages.append(response.user_message_param)
        self.messages.append(response.message_param)
        if tools_and_outputs:
            self.messages += response.tool_message_params(tools_and_outputs)
            await self._step("")

    async def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            print(f"(User): {question}")
            print("(Assistant): ", end="", flush=True)
            await self._step(question)
            print()
```

This implementation includes:

1. The `_stream` method, which sets up the LLM call with the necessary tools and computed fields.
2. The `_step` method, which processes the LLM response, handles tool calls, and updates the conversation history.
3. The `run` method, which implements the main interaction loop for the agent.

The `@openai.call` and `@prompt_template` decorators are used to set up the LLM interaction and define the prompt for the agent. Note that we've explicitly specified the available tools and their usage instructions in the system prompt. We have found that this improves the performance and reliability of tool usage by the LLM.

Note how we're passing `self.web_search` as a tool, which allows the LLM to use our custom web search method that has access to the agent's state.

## Running and Testing the Agent

Now that we have implemented our WebSearchAgent, let's run and test it:


```python
async def main():
    web_assistant = WebSearchAgent()
    await web_assistant.run()


# Run main in a jupyter notebook
await main()

# Run main in a python script
# import asyncio
# asyncio.run(main())
```

    (User): large language models
    (Assistant): using web_search tool with args: {'queries': ['large language models overview', 'applications of large language models', 'latest advancements in large language models', 'large language models ethical concerns', 'large language models future developments']}
    using extract_content tool with args: {'url': 'https://en.wikipedia.org/wiki/Large_language_model'}
    using extract_content tool with args: {'url': 'https://pixelplex.io/blog/llm-applications/'}
    using extract_content tool with args: {'url': 'https://www.ox.ac.uk/news/2023-05-05-tackling-ethical-dilemma-responsibility-large-language-models'}
    using extract_content tool with args: {'url': 'https://research.aimultiple.com/future-of-large-language-models/'}
    Large Language Models (LLMs) like OpenAI's GPT and Google's Gemini represent a significant advancement in artificial intelligence, particularly in natural language processing (NLP). These models excel at generating human-like text, understanding context, and performing various tasks across different domains. Below is an overview of LLMs, their applications, advancements, ethical considerations, and future developments.
    
    ### Overview of Large Language Models (LLMs)
    An LLM is a type of AI model designed to understand and generate text. They are built using deep learning techniques, particularly neural networks with a vast number of parameters. These models learn from extensive datasets, capturing complex patterns of human language. Notable examples include:
    - **GPT-4 (OpenAI)**: A multimodal model capable of processing both text and images, with up to 1.8 trillion parameters.
    - **Claude (Anthropic)**: Known for its impressive context handling, Claude 3 can process up to 100,000 tokens.
    - **BLOOM (BigScience)**: An open-access multilingual model with 176 billion parameters.
    
    ### Applications
    LLMs are used in a variety of fields, including:
    1. **Content Generation**: Automating the creation of written material for blogs, marketing, and social media.
    2. **Translation and Localization**: Providing accurate translations while maintaining cultural context and nuances.
    3. **Search and Recommendation**: Enhancing user search experiences and personalizing recommendations based on individual preferences.
    4. **Virtual Assistants**: Powering functionalities in services like Google Assistant and Amazon Alexa for real-time user interactions.
    5. **Code Development**: Assisting programmers by generating and debugging code, leading to more efficient workflows.
    6. **Sentiment Analysis**: Analyzing customer feedback to gauge public sentiment towards products or services.
    7. **Question Answering**: Responding accurately to user queries across various domains.
    8. **Market Research**: Gathering insights from consumer data and trends for strategic business decisions.
    9. **Education and Tutoring**: Personalizing learning experiences and providing real-time educational support.
    10. **Classification**: Categorizing text for various applications including moderation and customer service.
    
    ### Latest Advancements
    The field is rapidly evolving, with trends including:
    - **Multimodal Learning**: Combining text with images and audio to enhance model capability (as seen in tools like GPT-4 and Gemini).
    - **Self-improving Models**: Some LLMs can generate their own training data, improving their performance without external input.
    - **Sparse Expert Models**: New models are being designed to activate only relevant parts for specific tasks, increasing efficiency.
    
    ### Ethical Concerns
    Despite their efficacy, LLMs face significant ethical challenges:
    - **Bias and Fairness**: These models can reflect and amplify biases present in their training data, which raises concerns about fairness and equality in their outputs.
    - **Misinformation and Hallucination**: LLMs can generate convincing but false information, leading to a phenomenon known as "hallucination."
    - **Data Privacy**: The data used can sometimes include sensitive information, making privacy a critical aspect to address.
    
    ### Future Developments
    Looking forward, several promising directions include:
    - Enhanced **fact-checking** capabilities, integrating real-time data to ensure accuracy.
    - Development of **domain-specific models** tailored to particular industries like healthcare and finance for more relevant outputs.
    - Greater focus on **ethical AI**, with ongoing research into bias mitigation and the development of responsible AI frameworks.
    
    ### Conclusion
    LLMs are at the forefront of AI innovation, driving significant changes across multiple sectors. Their ability to interact in a human-like manner provides vast opportunities for automation and personalization, transforming industries from education to entertainment. However, addressing ethical concerns and ensuring their responsible use will be pivotal as these technologies continue to advance.


To use the WebSearchAgent, run the code above and start interacting with it by typing your questions. The agent will use web searches and content extraction to provide answers. Type 'exit' to end the interaction.

## Advanced Concepts and Best Practices

When working with Tools and Agents in Mirascope, consider the following best practices:

1. **Error Handling**: Implement robust error handling in your Tools and Agent implementation.
2. **Rate Limiting**: Be mindful of rate limits when using external APIs in your Tools.
3. **Caching**: Implement caching mechanisms to improve performance and reduce API calls.
4. **Testing**: Write unit tests for your Tools and integration tests for your Agents.
5. **Modularity**: Design your Tools and Agents to be modular and reusable.
6. **Security**: Be cautious about the information you expose through your Tools and Agents.
7. **Logging**: Implement logging to track the behavior and performance of your Agents.

For more advanced usage, you can explore concepts like:

- Multi-agent systems
- Tool chaining and composition
- Dynamic tool selection
- Memory and state management for long-running agents

For more techniques and best practices in using Mirascope, refer to the following documentation:

- [Tools](../../../learn/tools)
- [Agents](../../../learn/agents)
- [Streams](../../../learn/streams)
- [Chaining](../../../learn/chaining)

## 9. Conclusion

In this notebook, we've explored the basics of creating Tools and implementing Agents in Mirascope. We've built a WebSearchAgent that can perform web searches, extract content from webpages, and use an LLM to generate responses based on the gathered information.

This example demonstrates the power and flexibility of Mirascope in building AI applications that combine LLMs with custom tools and logic. As you continue to work with Mirascope, you'll discover more advanced features and patterns that can help you build even more sophisticated AI agents and applications.

If you like what you've seen so far, [give us a star](https://github.com/Mirascope/mirascope) and [join our community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).
