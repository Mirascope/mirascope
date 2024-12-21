# Evaluating Generating SQL with LLM

In this recipe, we will be using taking our [SQL Agent](../../agents/sql_agent) example and running evaluations on LLM call. We will be exploring various different evaluations we can run to ensure quality and expected behavior.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/tools/">Tools</a></li>
<li><a href="../../../learn/async/">Async</a></li>
<li><a href="../../../learn/evals/">Evals</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Check out the SQL Agent Tutorial</p>
<p>
We will be using our <code>LibrarianAgent</code> for our evaluations. For a detailed explanation regarding this code snippet, refer to the <a href="../../agents/sql_agent/">SQL Agent Tutorial</a>.
</p>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[openai]"
!pip install pytest ipytest pytest-asyncio
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Evaluating the prompt using a golden dataset

One effective approach is to establish a golden dataset that the prompt must successfully pass. We'll leverage `pytest` for this purpose, as it offers numerous testing conveniences.


```python
import sqlite3
from typing import ClassVar
from unittest.mock import MagicMock

import ipytest
import pytest
from mirascope.core import BaseMessageParam, openai, prompt_template
from pydantic import BaseModel, ConfigDict

ipytest.autoconfig(run_in_thread=True)


class Librarian(BaseModel):
    con: ClassVar[sqlite3.Connection] = sqlite3.connect("database.db")
    messages: list[BaseMessageParam | openai.OpenAIMessageParam] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run_query(self, query: str) -> str:
        """A SELECT query to run."""
        print(query)
        try:
            cursor = self.con.cursor()
            cursor.execute(query)
            res = cursor.fetchall()
            return str(res)
        except sqlite3.Error as e:
            return str(e)

    def _execute_query(self, query: str) -> str:
        """An INSERT, UPDATE, or DELETE query to execute."""
        print(query)
        try:
            cursor = self.con.cursor()
            cursor.execute(query)
            rows_affected = cursor.rowcount
            self.con.commit()
            if rows_affected > 0:
                return f"Query executed successfully, {rows_affected} row(s) were updated/inserted."
            else:
                return "No rows were updated/inserted."
        except sqlite3.Error as e:
            print(e)
            return str(e)

    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM:
        You are a friendly and knowledgeable librarian named Mira. Your role is to 
        assist patrons with their queries, recommend books, 
        and provide information on a wide range of topics.

        Personality:
            - Warm and approachable, always ready with a kind word
            - Patient and understanding, especially with those who are hesitant or confused
            - Enthusiastic about books and learning
            - Respectful of all patrons, regardless of their background or level of knowledge

        Services:
            - Keep track of patrons' reading lists using a SQLite database. Assume that the user is non technical and will ask you
        questions in plain English.
            - Recommend books based on the user's preferences
        Your task is to write a query based on the user's request.

        The database schema is as follows:

        TABLE ReadingList (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT CHECK(status IN ('Not Started', 'In Progress', 'Complete')) NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        );

        You must interpret the user's request and write the appropriate SQL query to
        pass in the tools.

        Example interactions:
            1. Select
                - USER: "Show me all books."
                - ASSISTANT: "SELECT * FROM ReadingList;"
            2. Insert
                - USER: "Add Gone with the Wind to my reading list."
                - ASSISTANT: "INSERT INTO ReadingList (title, status) VALUES ('Gone with the Wind', 'Not Started');"
            3. Update
                - USER: "I just finished Gone with the Wind, can you update the status, and give it 5 stars??"
                - ASSISTANT: "UPDATE ReadingList SET status = 'Complete' and rating = 5 WHERE title = 'Gone with the Wind';"
            4. Delete
                - USER: "Remove Gone with the Wind from my reading list."
                - ASSISTANT: "DELETE FROM ReadingList WHERE title = 'Gone with the Wind';"

        If field are not mentioned, omit them from the query.
        All queries must end with a semicolon.

        You have access to the following tools:
        - `_run_query`: When user asks for recommendations, you can use this tool to see what they have read.
        - `_execute_query`: Use the query generated to execute an 
            INSERT, UPDATE, or DELETE query.

        You must use these tools to interact with the database.

        MESSAGES: {self.messages}
        USER: {query}
        """
    )
    async def _stream(self, query: str) -> openai.OpenAIDynamicConfig:
        return {"tools": [self._run_query, self._execute_query]}

    async def _step(self, question: str):
        response = await self._stream(question)
        tools_and_outputs = []
        async for chunk, tool in response:
            if tool:
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
            print("(Assistant): ", end="", flush=True)
            await self._step(question)
            print()


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
    response = await mock_librarian._stream(select_query)
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
    response = await mock_librarian._stream(insert_query)
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
        "Can you mark Gone with the Wind as read?",
        "I just finished Gone with the Wind, can you update the status?",
    ],
)
async def test_update_query(update_query: str, mock_librarian: Librarian):
    response = await mock_librarian._stream(update_query)
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
    response = await mock_librarian._stream(delete_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert query == "DELETE FROM ReadingList WHERE title = 'Gone with the Wind';"


ipytest.run()
```


The golden dataset serves as our test fixtures, allowing us to verify basic text-to-SQL conversions and ensure our Agent maintains this functionality.

As we expand our tools or enhance our prompt, we should consistently implement additional prompt regression tests to maintain quality and functionality.

<div class="admonition note">
<p class="admonition-title">Tip</p>
<p>
SQL queries can get complex so be sure to add very specific tests, especially for mutable operations like INSERTS, UPDATES, and DELETES.
</p>
</div>


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
    response = await mock_librarian._stream("Can you add it to my reading list?")
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert (
            query
            == "INSERT INTO ReadingList (title, status) VALUES ('The Name of the Wind', 'Not Started');"
        )


ipytest.run()
```

    /Users/koudai/PycharmProjects/mirascope/.venv_notebook/lib/python3.12/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
    The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"
    
      warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))


    [32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[33m                                                                                 [100%][0m
    [33m========================================= warnings summary =========================================[0m
    ../../../.venv_notebook/lib/python3.12/site-packages/_pytest/config/__init__.py:1277
      /Users/koudai/PycharmProjects/mirascope/.venv_notebook/lib/python3.12/site-packages/_pytest/config/__init__.py:1277: PytestAssertRewriteWarning: Module already imported so cannot be rewritten: anyio
        self._mark_plugins_for_rewrite(hook)
    
    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    [33m[32m12 passed[0m, [33m[1m1 warning[0m[33m in 13.13s[0m[0m





    <ExitCode.OK: 0>




We expect that the LLM understands what "it" means in this case. If history was not working, then the LLM would not know what "it" refers to and would not be able to use the tool properly. This is particular useful because we can now test user flows easily to make sure certain flows behave properly.

Next, we'll be taking a look at using LLMs as judges for testing the tone we expect the LLM to take.

## LLMs as judges

With tools, it's easy to do an equality comparison to check that the LLM outputs proper SQL, but tone is a bit more complex. Thankfully, using LLMs makes this much simpler. We can use the LLM to evaluate the `friendliness` of the LLM and adjust the prompt as necessary.



```python
import asyncio

from mirascope.core import BasePrompt, anthropic
from openai.types.chat import ChatCompletionToolMessageParam
from pydantic import Field


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
    response = await mock_librarian._stream("")
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


ipytest.run()
```

    /Users/koudai/PycharmProjects/mirascope/.venv_notebook/lib/python3.12/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
    The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"
    
      warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))


    [32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[33m                                                                                [100%][0m
    [33m========================================= warnings summary =========================================[0m
    ../../../.venv_notebook/lib/python3.12/site-packages/_pytest/config/__init__.py:1277
      /Users/koudai/PycharmProjects/mirascope/.venv_notebook/lib/python3.12/site-packages/_pytest/config/__init__.py:1277: PytestAssertRewriteWarning: Module already imported so cannot be rewritten: anyio
        self._mark_plugins_for_rewrite(hook)
    
    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    [33m[32m13 passed[0m, [33m[1m1 warning[0m[33m in 17.07s[0m[0m





    <ExitCode.OK: 0>




 Similar to the conversations test, we simulate a user interaction by passing a messages array to a mock librarian. To assess the friendliness of this response, we utilize a custom `FriendlinessEvaluator`, which is a Mirascope `BasePrompt` that scores friendliness on a scale from 1 to 5 based on specific criteria. Leveraging Mirascope's model-agnostic capabilities, we send this evaluation prompt to both GPT-4 and Claude 3.5 Sonnet and average out these results.


 When adapting this recipe to your specific use-case, consider the following:

- Experiment with the prompt, add specific examples to the `FriendlinessEvaluator` for more accurate evaluations
- Experiment with the call prompt, add more examples of friendly conversation or persona.
- Add evaluations for retrieval if you're using RAG, or evaluations for business metrics.
e

