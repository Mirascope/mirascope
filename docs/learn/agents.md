# Agents

Agents, in the context of Large Language Models (LLMs), are autonomous or semi-autonomous entities that can perform tasks, make decisions, and interact with their environment based on natural language inputs and outputs. Mirascope provides a powerful framework for building such agents, allowing developers to create sophisticated AI applications that can engage in complex interactions and perform a variety of tasks.

Agents built with Mirascope can maintain state, use tools, make decisions, and carry out multi-step tasks. They combine the language understanding capabilities of LLMs with custom logic and external integrations, enabling a wide range of applications from conversational assistants to automated task executors.

Key benefits of using agents with Mirascope include:

1. **State Management**: Easily maintain and update agent state using Pydantic models and agent-specific Mirascope features.
2. **Tool Integration**: Seamlessly incorporate external tools and APIs into your agent's capabilities.
3. **Flexible Configuration**: Dynamically adjust the agent's behavior and available tools based on context.
4. **Provider Agnostic**: Build agents that can work with multiple LLM providers without changing core logic.
5. **Streaming Support**: Create responsive agents that can provide real-time feedback and handle long-running tasks.

## Basic Agent Structure

Let's start by creating a simple agent using Mirascope. We'll build a basic Librarian agent that can engage in conversations and maintain a history of interactions.

```python
from mirascope.core import openai, prompt_template
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM: You are a helpful librarian assistant.
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str) -> openai.OpenAIDynamicConfig:
        ...

    def run(self):
        while True:
            query = input("User: ")
            if query.lower() == "exit":
                break

            response = self._call(query)
            print(f"Librarian: {response.content}")

            if response.user_message_param:
                self.history.append(response.user_message_param)
            self.history.append(response.message_param)


librarian = Librarian()
librarian.run()
```

This basic structure demonstrates some key concepts we've covered in previous sections:

- **State Management**: We use a Pydantic `BaseModel` to define our agent's state, in this case, the chat history as a list of message parameters.
- **Core Logic**: The `_call` method encapsulates the main logic of our agent. It uses the `@openai.call` decorator to interface with the LLM.
- **Prompt Engineering**: We use a multi-part prompt that includes a system message, conversation history, and the current user query.
- **Accessed Attribute Injection**: We directly access and inject the `self.history` messages list.
- **Conversation Loop**: The `run` method implements a simple loop that takes user input, processes it through the `_call` method, and updates the conversation history.

This basic agent can engage in conversations about books, maintaining context through its history. However, it doesn't yet have any special capabilities beyond what the base LLM can do. In the next section, we'll enhance our Librarian by adding tools, allowing it to perform more specific tasks related to book management.

## Integrating Tools into Agents

To make our Librarian agent more capable, we'll add tools that allow it to manage a book collection. This will demonstrate how to integrate tools into an agent, use the `tool_message_param` method, and reinsert tool results in a provider-agnostic way.

Let's define a `Book` class and some corresponding tools for our Librarian to use:

```python
from mirascope.core import openai, prompt_template
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class Librarian(BaseModel):
    history: list[ChatCompletionMessageParam] = []
    books: dict[str, str] = {}

    def add_book(self, book: Book) -> str:
        """Adds a book to the collection."""
        self.books[book.title] = book.author
        return f"Added '{book.title}' by {book.author} to the collection."

    def remove_book(self, book: Book) -> str:
        """Removes a book from the collection."""
        self.books.pop(book.title, None)
        return f"Removed '{book.title}' by {book.author} from the collection."

    @openai.call(model="gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM:
        You are a helpful librarian assistant. You have access to the following tools:
        - `add_book`: Adds a book to your collection of books.
        - `remove_book`: Removes a book from your collection of books.
        You should use these tools to update your book collection according to the user.
        For example, if the user mentions that they recently read a book that they liked, consider adding it to the collection.
        If the user didn't like a book, consider removing it from the collection.

        You currently have the following books in your collection:
        {self.books}

        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str) -> openai.OpenAIDynamicConfig:
        return {"tools": [self.add_book, self.remove_book]}

    def _step(self, query: str) -> str:
        response = self._call(query)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                tools_and_outputs.append((tool, tool.call()))

        if response.user_message_param:
            self.history.append(response.user_message_param)
        self.history.append(response.message_param)
        if tools_and_outputs:
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step("")
        else:
            return response.content

    def run(self):
        while True:
            query = input("User: ")
            if query.lower() == "exit":
                break

            result = self._step(query)
            print(f"Librarian: {result}")


librarian = Librarian()
librarian.run()
```

This updated Librarian agent demonstrates several important concepts for integrating tools:

- **Tool Definition**: We define tools as functions, which automatically get turned into `BaseTool` types. We can then access the original function through the returned tool's `call` method.
- **Tool Configuration**: In the `_call` method, we return a dictionary with a `"tools"` key, listing the available tools for the LLM to use. This enables us to provide the LLM call with tools that have access to internal attributes through `self`, which makes implementing tools that dynamically update internal state a breeze.
- **Tool Execution**: The `_step` method checks for tool calls in the response and executes them using the `call` method.
- **Tool Result Reinsertion**: We use the `response.tool_message_params` classmethod to format the tool results and append them to the conversation history. This method works across different LLM providers, ensuring our agent remains provider-agnostic.
- **Recursive Handling**: If tools were used, we recursively call `_step` to allow the LLM to process the tool results and potentially use more tools. At each subsequent step we are taking advantage of empty messages to exclude the user message while the LLM is calling tools. When the LLM is done calling tools we return the final response.

This structure allows our Librarian to use tools to manage a book collection while maintaining a coherent conversation. The LLM can decide when to use tools based on the user's query, and the results of those tool uses are fed back into the conversation for further processing.

By integrating tools in this way, we've significantly enhanced our agent's capabilities while keeping the implementation flexible and provider-agnostic. In the next section, we'll explore how to add streaming capabilities to our agent, allowing for more responsive interactions.

## Streaming in Agents

Streaming allows agents to provide real-time responses, which can be particularly nice for long-running tasks. By implementing streaming in our Librarian agent, we can create a more responsive and interactive experience. Let's update our agent to support streaming responses and handle streamed tool calls.

First, we'll modify the `_call` method to enable streaming:

```python hl_lines="4"
class Librarian(BaseModel):
    ...

    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template("...")
    def _call(self, query: str) -> openai.OpenAIDynamicConfig:
        return {"tools": [self.add_book, self.remove_book]}
```

Now, let's update the `_step` method to handle streaming:

```python hl_lines="4 8"
def _step(self, query: str) -> str:
    response = self._call(query)
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
        return self._step("")
    else:
        return response.content
```

Finally, let's update the `run` method to handle the update to `_step`, which now prints the content of each chunk during the stream internally:

```python hl_lines="7 8 9"
def run(self):
    while True:
        query = input("User: ")
        if query.lower() == "exit":
            break

        print("Librarian: ", end="", flush=True)
        self._step(query)
        print("")
```

These changes implement streaming in our Librarian agent:

- **Streaming Configuration**: We add `stream=True` to the `@openai.call` decorator in the `_call` method.
- **Real-time Output**: We print chunk content as it's received, providing immediate feedback to the user.
- **Tool Handling**: Tool calls are processed in real-time as they're received in the stream. The results are collected and can be used for further processing.
- **State Updates**: The agent's state (book collection) is updated in real-time as tools are called.

This streaming implementation offers several benefits:

- **Responsiveness**: Users see the agent's response as it's being generated, providing a more interactive experience.
- **Long-running Tasks**: For complex queries or when using multiple tools, the agent can provide incremental updates rather than making the user wait for the entire response.
- **Efficient Resource Use**: Streaming allows for processing of partial results, which can be more efficient for memory usage and allows for early termination if needed.

By implementing streaming, we've made our Librarian agent more interactive and responsive. In the next section, we'll explore how to dynamically configure the tools available to our agent based on the current context or state.

## Stateful Agents: Dynamic Configuration of Tools

Dynamic configuration allows our agent to adapt its behavior and available tools based on the current context, state, or user preferences. This flexibility enhances the agent's capabilities and relevance. We'll update our Librarian agent to dynamically configure its tools based on it's state, which it can also update using its tools.

Let's implement a toolkit for making recommendations and modify our Librarian class to support dynamic tool configuration:

```python hl_lines="10-16 22 26-31 40-41 54-59"
from typing import Literal

from mirascope.core import BaseToolKit, openai, prompt_template, toolkit_tool
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

...


class RecommendationTools(BaseToolKit):
    reading_level: str

    @toolkit_tool
    def recommend_book(self, book: Book) -> str:
        """Recommend a {self.reading_level} book."""
        return f"{book.title} by {book.author} is a great {self.reading_level} book!"


class Librarian(BaseModel):
    history: list[ChatCompletionMessageParam] = []
    books: dict[str, str] = {}
    user_reading_level: str = "unknown"

    ...

    def update_reading_level(
        self, reading_level: Literal["beginner", "intermediate", "advanced"]
    ) -> str:
        """Updates the reading level of the user."""
        self.user_reading_level = reading_level
        return f"Updated reading level to {reading_level}."

    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM:
        You are a helpful librarian assistant. You have access to the following tools:
        - `add_book`: Adds a book to your collection of books.
        - `remove_book`: Removes a book from your collection of books.
        - `update_reading_level`: Updates the reading level of the user.
        - `recommend_book`: Recommends a book based on the user's reading level. You will only have access to this tool once you determine the user's reading level.
        You should use these tools to update your book collection according to the user.
        For example, if the user mentions that they recently read a book that they liked, consider adding it to the collection.
        If the user didn't like a book, consider removing it from the collection.

        You currently have the following books in your collection:
        {self.books}

        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str) -> openai.OpenAIDynamicConfig:
        tools = [self.add_book, self.remove_book, self.update_reading_level]
        if self.user_reading_level != "unknown":
            tools += RecommendationTools(
                reading_level=self.user_reading_level
            ).create_tools()
        return {"tools": tools}

    ...


librarian = Librarian()
librarian.run()
```

This updated Librarian agent demonstrates several key aspects of dynamic tool configuration:

- **State-Dependent Tool Availability**: The `recommend_book` tool is only made available when the `user_reading_level` is not "unknown". This is achieved in the `_call` method by conditionally adding the tool to the list.
- **Context-Aware Tool Behavior**: The `recommend_book` tool recommends a book according to the user's reading level. This allows for responses that are more tailored based on current state context.
- **Dynamic State Updates**: The `update_reading_level` tool enables the agent to update the `user_reading_level` state whenever it determines the user's reading level. This could be from directly asking or based on the books the user has read.
- **Contextual Prompting**: The system message in the `_call` method includes instructions around how and when to use certain tools. This is important to find success when using various (and possibly many) tools.

By using dynamic configuration in this way, we've created an agent that can adapt its capabilities based on the current state and context of the conversation. This dynamic configuration allows for more nuanced and relevant interactions.

This approach to dynamic configuration makes our Librarian agent more flexible and capable of handling a wider range of user queries and scenarios. As the conversation progresses and the agent's state changes, its capabilities evolve to better serve the user's needs.

## Best Practices and Advanced Techniques

As you develop more sophisticated agents with Mirascope, it's crucial to follow best practices and leverage advanced techniques to create robust, efficient, and scalable agent systems.

### Designing Effective Agent Prompts

- **Clear Instructions**: Provide concise, specific instructions in your system prompts. Clearly define the agent's role, capabilities, and limitations, as well as the tools it has access to and how to use them.
- **Context Awareness**: Include relevant context in your prompts, such as the agent's current state or recent interactions.
- **Consistent Persona**: Maintain a consistent voice and behavior across all prompts for a given agent.

### Managing Agent State and Memory

- **Pydantic Models**: Use Pydantic models to define clear, type-safe state structures for your agents.
- **Efficient History Management**: Implement strategies to manage conversation history, such as keeping only the most recent messages or summarizing older interactions. You can also store conversation history in an external source and retrieve relevant messages to inject as context (e.g. RAG using a VectorStore of messages).
- **State Persistence**: For long-running agents, consider using databases or file storage to maintain state across sessions.
- **Serialization**: Implement methods to serialize and deserialize your agent's state for easy storage and retrieval. Pydantic's `BaseModel` class makes this simple and easy.

### Error Handling and Reliability

- **Graceful Degradation**: Design your agent to handle cases where the LLM response is unexpected or tools fail to execute.
- **Retry Mechanisms**: Implement retry logic for LLM calls and tool executions to handle transient errors. We recommend using [tenacity](../integrations/tenacity.md)
- **Validation**: Use Pydantic's validation capabilities to ensure that tool inputs and outputs meet your expected schema. You can use our [`collect_errors`](../integrations/tenacity.md#error-reinsertion) helper method for easy reinsertion of errors into subsequent retries.
- **Logging**: Implement comprehensive logging to track agent behavior, tool usage, and error states for debugging and improvement.

### Advanced Techniques

- **Asynchronous Operations**: Leverage Python's asyncio to handle multiple operations concurrently, improving efficiency for I/O-bound tasks.
- **Multi-Provider Setups**: Use different LLM providers for specialized tasks within your agent system, taking advantage of each provider's strengths.
- **Dynamic Tool Generation**: Use `BaseToolKit` to generate tools dynamically based on the current state or context of the conversation.
- **Hierarchical Agents**: Implement a hierarchy of agents, with higher-level agents delegating tasks to more specialized sub-agents. Check out our cookbook recipe on implementing a [blog writing agent](../cookbook/agents/blog_writing_agent.md) for an example of how to implement an Agent Executor.
- **Adaptive Behavior**: Implement mechanisms for your agent to learn from interactions and adjust its behavior over time, such as fine-tuning prompts or adjusting tool selection strategies.

By following these best practices and leveraging advanced techniques, you can create sophisticated, reliable, and efficient agent systems with Mirascope. Remember to continuously test and refine your agents based on real-world performance and user feedback.

As you explore more complex agent architectures, consider implementing safeguards, such as content filtering or output validation, to ensure your agents behave ethically and produce appropriate responses. Always monitor your agents' performance and be prepared to make adjustments as needed.
