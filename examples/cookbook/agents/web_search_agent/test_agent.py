import pytest
from pydantic import BaseModel, Field

from examples.cookbook.agents.web_search_agent.agent import WebAssistant
from examples.cookbook.agents.web_search_agent.messages import (
    test_conversation_messages,
    test_extract_content_messages,
)
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


@pytest.mark.asyncio
async def test_conversation():
    """Tests that in a conversation setting, the llm generated query is context-relevant."""
    web_assistant = WebAssistant(
        search_history=[
            "best LLM development tools",
            "top libraries for LLM development",
            "LLM libraries for software engineers",
            "LLM dev tools for machine learning",
            "most popular libraries for LLM development",
        ],
        messages=test_conversation_messages,
    )
    response = await web_assistant._stream("What is mirascope library?")
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


@pytest.mark.asyncio
async def test_extract_content():
    """Tests that the extract content tool gets called once."""
    user_query = "What is the capital of France?"
    web_assistant = WebAssistant(messages=test_extract_content_messages)
    response = await web_assistant._stream(user_query)
    tools = []
    async for _, tool in response:
        if tool:
            tools.append(tool)
    assert len(tools) == 1 and tools[0]._name() == "extract_content"
