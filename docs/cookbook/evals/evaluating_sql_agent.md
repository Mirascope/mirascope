# Evaluating Generating SQL with LLM

In this recipe, we will be using taking our [SQL Agent](../agents/sql_agent.md) example and running evaluations on LLM call. We will be exploring various different evaluations we can run to ensure quality and expected behavior.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Tools](../../learn/tools.md)
    - [Async](../../learn/async.md)
    - [Evals](../../learn/evals.md)

??? note "Check out the SQL Agent Cookbook"

    We will be using our `LibrarianAgent` for our evaluations. For a detailed explanation regarding this code snippet, refer to the [SQL Agent Cookbook](../agents/sql_agent.md).

## Evaluating the prompt using a golden dataset

One effective approach is to establish a golden dataset that the prompt must successfully pass. We'll leverage `pytest` for this purpose, as it offers numerous testing conveniences.

```python
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_librarian():
    class MockLibrarian(Librarian):
        con: ClassVar[sqlite3.Connection] = MagicMock()

    return MockLibrarian()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "select_query",
    [
        "Get all books",
        "Get every single book",
        "Show me all books",
        "List all books",
        "Display all books",
    ],
)
async def test_select_query(select_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(select_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert query == "SELECT * FROM ReadingList;"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "insert_query",
    [
        "Please add Gone with the Wind to my reading list",
        "You recently recommended Gone with the Wind, can you add it to my reading list.",
    ],
)
async def test_insert_query(insert_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(insert_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert (
            query
            == "INSERT INTO ReadingList (title, status) VALUES ('Gone with the Wind', 'Not Started');"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_query",
    [
        "Can you mark Gone with the Wind as read.",
        "I just finished Gone with the Wind, can you update the status?",
    ],
)
async def test_update_query(update_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(update_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert (
            query
            == "UPDATE ReadingList SET status = 'Complete' WHERE title = 'Gone with the Wind';"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "delete_query",
    [
        "Can you remove Gone with the Wind from my reading list?",
        "Can you delete Gone with the Wind?",
    ],
)
async def test_delete_query(delete_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(delete_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert query == "DELETE FROM ReadingList WHERE title = 'Gone with the Wind';"
```

The golden dataset serves as our test fixtures, allowing us to verify basic text-to-SQL conversions and ensure our Agent maintains this functionality.

As we expand our tools or enhance our prompt, we should consistently implement additional prompt regression tests to maintain quality and functionality.

!!! note "Tip"

    SQL queries can get complex so be sure to add very specific tests, especially for mutable operations like INSERTS, UPDATES, and DELETES.

## Evaluating conversations

With the above techniques, we've shown how to evaluate simple input and output pairs, but we also want to test conversations with history. We can define some messages we want the LLM to have and get some expected output, like so:

```python
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionUserMessageParam,
)


@pytest.mark.asyncio
async def test_conversation(mock_librarian: Librarian):
    mock_librarian.messages = [
        ChatCompletionUserMessageParam(
            role="user", content="Can you recommend me a fantasy book?"
        ),
        ChatCompletionAssistantMessageParam(
            role="assistant",
            content="I would recommend 'The Name of the Wind' by Patrick Rothfuss. It’s the first book in 'The Kingkiller Chronicle' series and features a beautifully written story about a gifted young man who grows up to be a legendary figure. It's filled with magic, adventure, and rich character development. I believe you'll enjoy it! Would you like to add it to your reading list?",
        ),
    ]
    response = await mock_librarian._step("Can you add it to my reading list?")
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert (
            query
            == "INSERT INTO ReadingList (title, status) VALUES ('The Name of the Wind', 'Not Started');"
        )
```

We expect that the LLM understands what "it" means in this case. If history was not working, then the LLM would not know what "it" refers to and would not be able to use the tool properly. This is particular useful because we can now test user flows easily to make sure certain flows behave properly.

Next, we'll be taking a look at using LLMs as judges for testing the tone we expect the LLM to take.

## LLMs as judges

With tools, it's easy to do an equality comparison to check that the LLM outputs proper SQL, but tone is a bit more complex. Thankfully, using LLMs makes this much simpler. We can use the LLM to evaluate the `friendliness` of the LLM and adjust the prompt as necessary.

```python
import asyncio

from openai.types.chat import ChatCompletionToolMessageParam
from pydantic import BaseModel, Field

from mirascope.core import (
    BasePrompt,
    anthropic,
    openai,
    prompt_template,
)

@prompt_template(
    """
    Evaluate the friendliness of generated text on a continuous scale from 1 to 5.
    A generation is friendly (score > 1) if it contains content that is:

    - Warm, welcoming, and positive in tone
    - Respectful, considerate, and empathetic towards others
    - Encouraging, supportive, or promotes kindness
    - Inclusive and mindful of diverse perspectives

    Provide a brief reasoning for your assigned score.
    Make sure to highlight the specific aspects that impacted your score.

    Use the following friendliness scale:

    1 - No friendliness; cold, distant, or neutral tone
    2 - Mild friendliness; slightly warm or polite language
    3 - Moderate friendliness; noticeably kind and welcoming content
    4 - High friendliness; very warm, supportive, and empathetic language
    5 - Extreme friendliness; exceptionally kind, caring, and uplifting content

    Input Query: {input_query}
    Output Content: {output_content}
    """
)
class FriendlinessEvaluator(BasePrompt):
    input_query: str
    output_content: str

@pytest.mark.asyncio
async def test_friendliness(mock_librarian: Librarian):
    input_query = "Can you add gone with the wind"
    mock_librarian.messages = [
        ChatCompletionUserMessageParam(role="user", content=input_query),
        ChatCompletionAssistantMessageParam(
            role="assistant",
            tool_calls=[
                {
                    "type": "function",
                    "function": {
                        "arguments": "{\"query\":\"INSERT INTO ReadingList (title, status) VALUES ('Gone with the Wind', 'Not Started');\"}",
                        "name": "_execute_query",
                    },
                    "id": "1",
                }
            ],
        ),
        ChatCompletionToolMessageParam(
            role="tool",
            content="Query executed successfully, 1 row(s) were updated/inserted.",
            tool_call_id="1",
        ),
    ]
    response = await mock_librarian._step("")
    output_content = ""
    async for chunk, _ in response:
        output_content += chunk.content
    prompt = FriendlinessEvaluator(
        input_query=input_query, output_content=output_content
    )

    class Eval(BaseModel):
        score: float = Field(..., description="A score between [1.0, 5.0]")
        reasoning: str = Field(..., description="The reasoning for the score")

    async def run_evals() -> list[Eval]:
        judges = [
            openai.call(
                "gpt-4o-mini",
                response_model=Eval,
                json_mode=True,
            ),
            anthropic.call(
                "claude-3-5-sonnet-20240620",
                response_model=Eval,
                json_mode=True,
            ),
        ]
        calls = [prompt.run_async(judge) for judge in judges]
        return await asyncio.gather(*calls)

    evals = await run_evals()
    total_score = sum(eval.score for eval in evals)
    average_score = total_score / len(evals)
    assert average_score > 2
```

 Similar to the conversations test, we simulate a user interaction by passing a messages array to a mock librarian. To assess the friendliness of this response, we utilize a custom `FriendlinessEvaluator`, which is a Mirascope `BasePrompt` that scores friendliness on a scale from 1 to 5 based on specific criteria. Leveraging Mirascope's model-agnostic capabilities, we send this evaluation prompt to both GPT-4 and Claude 3.5 Sonnet and average out these results.


 When adapting this recipe to your specific use-case, consider the following:

- Experiment with the prompt, add specific examples to the `FriendlinessEvaluator` for more accurate evaluations
- Experiment with the call prompt, add more examples of friendly conversation or persona.
- Add evaluations for retrieval if you're using RAG, or evaluations for business metrics.
e
