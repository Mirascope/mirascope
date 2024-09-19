# Agents

??? api "API Documentation"
    [`mirascope.core.base.tool`](../api/core/base/tool.md)
    [`mirascope.core.base.toolkit`](../api/core/base/toolkit.md)

When working with Large Language Models (LLMs), an "agent" refers to an autonomous or semi-autonomous system that can perform tasks, make decisions, and interact with its environment based on natural language inputs and outputs. Agents combine the language understanding capabilities of LLMs with custom logic, external integrations, and often a sense of "memory" or state.

Let's look at a basic example of what an agent might look like in code:

```python hl_lines="5-6 16 25"
from mirascope.core import BaseMessageParam, openai, prompt_template
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []

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

In this example:

1. The `Librarian` class defines the basic structure of an agent.
2. It maintains a `history` of interactions, which serves as the agent's "memory".
3. The `_call` method uses an LLM to generate responses based on the user's query and the conversation history.
4. The `run` method implements a simple interaction loop, allowing the agent to engage in a conversation.

This is a very basic agent. More sophisticated agents might include:

- Multiple LLM calls for different purposes (e.g., planning, execution, reflection)
- Integration with external tools or APIs
- More complex state management
- Ability to learn and adapt over time

Agents are particularly useful for creating interactive AI systems that can perform complex tasks, maintain context over long conversations, and integrate with various external systems and data sources. They're commonly used in applications such as:

- Chatbots and virtual assistants
- Automated customer service systems
- AI-powered tutoring systems
- Task planning and execution systems
- Game NPCs (Non-Player Characters)

In the following sections, we'll explore how to build more advanced agents using Mirascope, including how to integrate tools, manage state, implement streaming for real-time responses, and apply best practices for robust and efficient agent design.

## Real-World Example: Customer Support Agent

To better understand how agents can be applied in practical scenarios, let's consider a customer support system for an e-commerce platform. An agent in this context could perform the following tasks:

1. Answer product-related queries
2. Process returns and refunds
3. Escalate complex issues to human support
4. Update order status
5. Provide personalized product recommendations

Here's a basic implementation of such an agent using Mirascope:

```python hl_lines="10 11 13 19 35-38"
from mirascope.core import BaseMessageParam, openai, prompt_template
from pydantic import BaseModel

class Order(BaseModel):
    order_id: str
    status: str
    items: list[str]

class CustomerSupportAgent(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []
    orders: dict[str, Order] = {}

    def update_order_status(self, order_id: str, new_status: str) -> str:
        if order_id in self.orders:
            self.orders[order_id].status = new_status
            return f"Order {order_id} status updated to {new_status}"
        return f"Order {order_id} not found"

    def get_order_status(self, order_id: str) -> str:
        if order_id in self.orders:
            return f"Order {order_id} status: {self.orders[order_id].status}"
        return f"Order {order_id} not found"

    @openai.call(model="gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM: You are a customer support agent for an e-commerce platform.
        Your tasks include answering product queries, processing returns,
        and updating order statuses. Use the provided tools when necessary.

        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str) -> openai.OpenAIDynamicConfig:
        return {
            "tools": [self.update_order_status, self.get_order_status]
        }

    def run(self):
        while True:
            query = input("Customer: ")
            if query.lower() == "exit":
                break
            response = self._call(query)
            print(f"Agent: {response.content}")
            if response.tools:
                for tool in response.tools:
                    print(f"Tool used: {tool.name}")
                    print(f"Result: {tool.call()}")
            self.history.append(response.user_message_param)
            self.history.append(response.message_param)

agent = CustomerSupportAgent()
agent.run()
```

This CustomerSupportAgent demonstrates several key features of a practical agent:

1. **State Management**: The agent maintains a history of interactions and a database of orders.
2. **Tool Integration**: It includes tools for updating and retrieving order statuses.
3. **Contextual Responses**: The agent uses conversation history to provide context-aware responses.
4. **Task-Specific Prompt**: The system prompt clearly defines the agent's role and capabilities.

In a real-world scenario, this agent would be further enhanced with more sophisticated tools, integration with actual e-commerce systems, and possibly more advanced natural language processing capabilities.

This example illustrates how agents can be designed to handle specific, real-world tasks while maintaining a conversation flow and leveraging external tools and data sources.

## Integrating Tools into Agents

In this section, we'll explore how to enhance our agents by integrating tools. We'll cover:
- Defining and implementing tools within an agent
- Configuring an agent to use tools
- Executing tool calls and handling their results
- Reinserting tool results into the conversation flow

This will demonstrate how to significantly expand an agent's capabilities beyond simple text generation.

To make our Librarian agent more capable, we'll add tools that allow it to manage a book collection. This will demonstrate how to integrate tools into an agent, use the `tool_message_param` method, and reinsert tool results in a provider-agnostic way.

Let's define a `Book` class and some corresponding tools for our Librarian to use:

```python hl_lines="12 42 43 50"
from mirascope.core import BaseMessageParam, openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class Librarian(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []
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
        print(f"Your book collection: {self.books}")

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

Under the hood, Mirascope is doing the following:

1. Converting the `add_book` and `remove_book` methods into `BaseTool` instances.
2. Generating a tool schema for each tool based on the method's signature and docstring.
3. Including these tool schemas in the API call to the LLM.
4. Parsing the LLM's response to identify and execute tool calls.

## Streaming in Agents

This section focuses on implementing streaming responses in our agents. We'll discuss:

Configuring an agent for streaming
Handling streamed responses and tool calls in real-time
Benefits and use cases of streaming in agent interactions

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

```python hl_lines="4-8"
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

```python hl_lines="8"
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

- **Improved User Experience**: Users receive immediate feedback, creating a more engaging and interactive conversation.
- **Efficient Processing of Long Responses**: For lengthy responses, streaming allows for processing and displaying content as it's generated, rather than waiting for the entire response.
- **Real-time Tool Integration**: Tools can be called and their results processed as soon as they're identified in the stream, allowing for more dynamic and responsive agent behavior.
- **Reduced Latency**: The perceived response time is shorter as users see content immediately, even if the full response takes longer to generate.
- **Opportunity for Early Termination**: In cases where the initial part of a response is sufficient, the stream can be terminated early, saving processing time and resources.

By implementing streaming, we've made our Librarian agent more interactive and responsive. In the next section, we'll explore how to dynamically configure the tools available to our agent based on the current context or state.

## Stateful Agents: Dynamic Configuration of Tools

Dynamic configuration allows our agent to adapt its behavior and available tools based on the current context, state, or user preferences. This flexibility enhances the agent's capabilities and relevance. We'll update our Librarian agent to dynamically configure its tools based on it's state, which it can also update using its tools.

Let's implement a toolkit for making recommendations and modify our Librarian class to support dynamic tool configuration:

```python hl_lines="15-21 64"
from typing import Literal

from mirascope.core import (
    BaseMessageParam,
    BaseToolKit,
    openai,
    prompt_template,
    toolkit_tool,
)
from pydantic import BaseModel

...


class RecommendationTools(BaseToolKit):
    reading_level: str

    @toolkit_tool
    def recommend_book(self, book: Book) -> str:
        """Recommend a {self.reading_level} book."""
        return f"{book.title} by {book.author} is a great {self.reading_level} book!"


class Librarian(BaseModel):
    history: list[BaseMessageParam | openai.OpenAIMessageParam] = []
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

1. Automatically converting the `RecommendationTools` class into a set of tools with dynamically injected properties (like `reading_level`).
2. Dynamically updating the available tools for each LLM call based on the agent's current state.
3. Generating and including the appropriate tool schemas in the API call to the LLM.

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
  ```mermaid
  graph TD
      A[Main Agent] --> B[Sub-Agent 1: Query Understanding]
      A --> C[Sub-Agent 2: Task Planning]
      A --> D[Sub-Agent 3: Execution]
      B --> E[Natural Language Processing]
      C --> F[Task Breakdown]
      C --> G[Resource Allocation]
      D --> H[Tool Selection]
      D --> I[Action Execution]
  ```

- **Adaptive Behavior**: Implement mechanisms for your agent to learn from interactions and adjust its behavior over time, such as fine-tuning prompts or adjusting tool selection strategies.
  ```mermaid
  graph LR
      A[User Input] --> B[Agent Processing]
      B --> C[Response Generation]
      C --> D[User Feedback]
      D --> E[Performance Evaluation]
      E --> F[Behavior Adjustment]
      F -->|Update| G[Prompt Templates]
      F -->|Modify| H[Tool Selection Strategy]
      F -->|Refine| I[Response Style]
      G --> B
      H --> B
      I --> C
  ```

By following these best practices and leveraging advanced techniques, you can create sophisticated, reliable, and efficient agent systems with Mirascope. Remember to continuously test and refine your agents based on real-world performance and user feedback.

As you explore more complex agent architectures, consider implementing safeguards, such as content filtering or output validation, to ensure your agents behave ethically and produce appropriate responses. Always monitor your agents' performance and be prepared to make adjustments as needed.
