# Evaluating Web Search Agent with LLM

In this recipe, we will be using taking our [Web Search Agent Cookbook](../agents/web_search_agent.md) and running evaluations on the LLM call. We will be exploring writing a context relevance test since that is one of the most important aspects of web search.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Tools](../../learn/tools.md)
    - [Async](../../learn/async.md)
    - [Evals](../../learn/evals.md)

??? note "Check out the Web Search Agent Cookbook"

    We will be using our `WebAssistantAgent` for our evaluations. For a detailed explanation regarding this code snippet, refer to the [Web Search Agent Cookbook](../agents/web_search_agent.md).

## Basic Evaluations

Let's start off with some basic evaluations to know whether our agent is working in general. Given that updates to prompts can significantly influence LLM behavior, it's crucial to test each component of our agent individually.

### Evaluating `_web_search` tool

Our goal is to ensure that the LLM consistently utilizes the web search tool, rather than relying on its inherent knowledge base to generate responses. We've intentionally refrained from explicitly instructing the agent to always utilize the web search tool, as some user queries may be more conversational in nature and not necessitate web searches. However, for user queries that are more information-seeking, the agent should always leverage the web search tool.

```python
import pytest

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_query",
    [
        "How is the weather in New York?",
        "What is the capital of France?",
        "Who is the president of the United States?",
        "What is the population of India?",
        "What is an apple?",
    ],
)
async def test_web_search(user_query: str):
    """Tests that the web search agent always uses the web search tool."""
    web_assistant = WebAssistant()
    response = await web_assistant._stream(user_query)
    tools = []
    async for _, tool in response:
        if tool:
            tools.append(tool)
    assert len(tools) == 1 and tools[0]._name() == "_web_search"
```

It's recommended to continually expand our golden dataset until we can confidently assert that the LLM uses web search when appropriate.

### Evaluating `extract_content` tool

Our agent has been prompt engineered to utilize the extract_content tool at its discretion. Given the non-deterministic nature of this test, we'll implement a basic verification to ensure that the `extract_content` tool is invoked at least once per user query. We'll employ the same golden dataset used in the `test_web_search`, allowing us to assume that `test_extract_content` will always have a functional `_web_search`.

```python
messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "arguments": '{"queries":["capital of France","capital city of France","France","Paris","France capital"]}',
                    "name": "_web_search",
                },
                "id": "call_1",
            }
        ],
    },
    {"role": "tool", "content": "..."},
]

@pytest.mark.asyncio
async def test_extract_content():
    """Tests that the extract content tool gets called once."""
    user_query = "What is the capital of France?"
    web_assistant = WebAssistant(messages=messages)
    response = await web_assistant._stream(user_query)
    tools = []
    async for _, tool in response:
        if tool:
            tools.append(tool)
    assert len(tools) == 1 and tools[0]._name() == "extract_content"
```

For brevity, we've included just one example from our golden dataset, as the full messages array would be too lengthy to show.

Now that we have our simple tests, let's take a look at a more complex evaluation-based test.

## Evaluating context relevance of LLM-generated queries

LLMs can easily answer detailed queries, but real-world scenarios often involve vague questions from users who may not fully understand what they're seeking. Just as many people struggle to master advanced search techniques despite years of using search engines, becoming proficient at formulating effective queries for LLMs is equally challenging.

```python
from pydantic import BaseModel, Field

from mirascope.core import (
    anthropic,
    prompt_template,
)

class ContextRelevant(BaseModel):
    is_context_relevant: bool = Field(
        description="Whether the LLM-generated query is context-relevant"
    )
    explanation: str = Field(description="The reasoning for the context relevance")


@anthropic.call(
    model="claude-3-5-sonnet-20240620", response_model=ContextRelevant, json_mode=True
)
@prompt_template(
    """
    Given:

    Search history: {search_history}
    User query: {user_query}
    LLM-generated query: {llm_query}

    Evaluate if the LLM-generated query is context-relevant using the following criteria:

    Bridging Relevance:

    Does {llm_query} effectively bridge the gap between {search_history} and {user_query}?
    Does it incorporate elements from both {search_history} and {user_query} meaningfully?


    Intent Preservation:

    Does {llm_query} maintain the apparent intent of {user_query}?
    Does it also consider the broader context established by {search_history}?


    Topical Consistency:

    Is {llm_query} consistent with the overall topic or theme of {search_history}?
    If there's a shift in topic from {search_history} to {user_query}, does {llm_query} handle this transition logically?


    Specificity and Relevance:

    Is {llm_query} specific enough to be useful, considering both {search_history} and {user_query}?
    Does it avoid being overly broad or tangential?


    Contextual Enhancement:

    Does {llm_query} add value by incorporating relevant context from {search_history}?
    Does it expand on {user_query} in a way that's likely to yield more relevant results?


    Handling of Non-Sequiturs:

    If {user_query} is completely unrelated to {search_history}, does {llm_query} appropriately pivot to the new topic?
    Does it still attempt to maintain any relevant context from {search_history}, if possible?


    Semantic Coherence:

    Do the terms and concepts in {llm_query} relate logically to both {search_history} and {user_query}?
    Is there a clear semantic path from {search_history} through {user_query} to {llm_query}?



    Evaluation:

    Assess {llm_query} against each criterion, noting how well it performs.
    Consider the balance between maintaining context from {search_history} and addressing the specific intent of {user_query}.
    Evaluate how {llm_query} handles any topic shift between {search_history} and {user_query}.

    Provide a final assessment of whether {llm_query} is context-relevant, with a brief explanation of your reasoning.
    """
)
async def check_context_relevance(
    search_history: list[str], user_query: str, llm_query: str
): ...
```

We use an LLM to evaluate context-awareness and define a series of questions the LLM will answer to determine if the `llm_query` generated makes sense given the `user_query`.

### Examples

We can write some simple examples to verify if the evaluation is working properly, like so:

```python
import asyncio

async def run(search_history: list[str], user_query: str, llm_query: str):
    return await check_context_relevance(search_history, user_query, llm_query)
search_history = ["Best beaches in Thailand", "Thai cuisine must-try dishes"]
user_query = "How to book flights?"
llm_query = "How to book flights to Thailand for a beach and culinary vacation"
asyncio.run(run())
# is_context_relevant=True explanation="The LLM-generated query effectively bridges the gap between the search history and the user query. It incorporates elements from both the search history (Thailand, beaches, cuisine) and the user's intent to book flights. The query maintains the original intent while adding relevant context from the search history, creating a coherent and specific request that aligns with the user's apparent travel interests. It successfully handles the topic shift by integrating the flight booking aspect with the previously established context of Thai beaches and cuisine, resulting in a semantically coherent and contextually enhanced query."
```

Now let's update our `llm_query`:

```python
llm_query = "General steps for booking flights online"
asyncio.run(run())
# is_context_relevant=False explanation="The LLM-generated query 'General steps for booking flights online' is not context-relevant. It addresses the user's specific question about booking flights but fails to incorporate any context from the search history about Thai beaches and cuisine. The query represents a complete topic shift without attempting to maintain relevance to the previous searches, missing an opportunity to provide more tailored advice such as booking flights to Thailand specifically."
```

We can verify that the `llm_query` does not mention anything related to the `search_history`, and therefore is properly labeled as context irrelevant.

However, it's important to note that not all user queries need to be context-relevant to previous searches. Users may intentionally shift topics or ask unrelated questions in succession, which is a natural part of chatbot interactions.

## Implementing the test

Now that we have our evaluation, we can write our test.

```python
import json

search_history = [
    "best LLM development tools",
    "top libraries for LLM development",
    "LLM libraries for software engineers",
    "LLM dev tools for machine learning",
    "most popular libraries for LLM development",
]
messages = [
    {"role": "user", "content": "I am a SWE looking for a LLM dev tool library"},
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "arguments": json.dumps({"queries": search_history}),
                    "name": "_web_search",
                },
                "id": "call_1",
            }
        ],
    },
    {
        "role": "tool",
        "content": "..."
    }
]

@pytest.mark.asyncio
async def test_conversation():
    web_assistant = WebAssistant(
        search_history=search_history,
        messages=messages,
    )
    response = await web_assistant._call("What is mirascope library?")
    async for _, tool in response:
        queries = tool.args.get("queries", "") if tool else ""
        is_context_relevant = False
        for query in queries:
            context_relevant = await check_context_relevance(
                web_assistant.search_history, "What is mirascope library?", query
            )
            is_context_relevant = context_relevant.is_context_relevant
            if is_context_relevant:
                break
        assert is_context_relevant
```

A few things to note:

- Messages are appended to reduce testing time and token usage. Check [messages.py](https://github.com/Mirascope/mirascope/tree/dev/examples/cookbook/agents/web_search_agent/messages.py) for the full history used.
- Our test asserts at least one of the llm queries generated must be context-relevant.

Evaluating context relevance is just of the crucial steps towards enhancing LLM-powered search systems, enabling them to provide more coherent, personalized, and valuable results across diverse user interactions.

When adapting this recipe to your specific use-case, consider the following:

- Use `pytest.mark.parametrize` and add more examples from user queries to further identify areas of improvement.
- Implement context relevance call in to the agent to generate a feedback loop for the agent to ask a better search query.
- Context-relevance is not always what the user is asking for. The challenge lies in distinguishing between unintentional context loss and intentional topic shifts. This can be addressed by implementing a like/dislike answer feature and using that feedback to refine its search.
