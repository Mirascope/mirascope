# Generate SQL with LLM

In this recipe, we will be using OpenAI GPT-4o-mini to act as a co-pilot for a Database Admin. While LLMs are powerful and do pretty well at transforming laymen queries into SQL queries, it is still dangerous to do so without supervision. This recipe will have no guardrails for mutable operations and is purely for getting started.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Tools](../../learn/tools.md)
    - [Dynamic Configuration](../../learn/dynamic_configuration.md)
    - [Async](../../learn/async.md)
    - [Agents](../../learn/agents.md)

## Setup

We will be using SQLite, but this example will work for any common SQL dialect, such as PostgreSQL, MySQL, MSSQL, and more.

```python
pip install sqlite3
```

## Setup SQL Database

Replace this part with whichever SQL dialect you are using, or skip if you have a database set up already.

```python
import sqlite3
con = sqlite3.connect("database.db")
cur = con.cursor()
# ONE TIME SETUP
cur.execute("""
    CREATE TABLE ReadingList (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Not Started', 'In Progress', 'Complete')),
        rating INTEGER CHECK(rating BETWEEN 1 AND 5)
    )
""")
con.commit()
```

This will be our playground example.

## Write your Database Assistant

We will be creating an Agent that will take non-technical queries and translate them into SQL queries that will be executed. The first step will be to create our two tools, `_run_query` and `_execute_query` , which will be read and write operations respectively.

```python
import sqlite3
from typing import ClassVar

from mirascope.core import openai, prompt_template
from pydantic import BaseModel, ConfigDict

class Librarian(BaseModel):
    con: ClassVar[sqlite3.Connection] = sqlite3.connect("database.db")

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
                return "Query executed successfully, {rows_affected} row(s) were updated/inserted."
            else:
                return "No rows were updated/inserted."
        except sqlite3.Error as e:
            print(e)
            return str(e)
```

Now that we have our tools setup it is time to engineer our prompt

## Prompt Engineering

Knowing what tools are available is crucial when prompt engineering, so that we can tell the LLM when and how the tools should be used.

Now we will take our `Librarian` and add our `@openai.call`:

```python
from openai.types.chat import ChatCompletionMessageParam


class Librarian(BaseModel):
    con: ClassVar[sqlite3.Connection] = sqlite3.connect("database.db")
    messages: list[ChatCompletionMessageParam] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

    ...

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
```

Let's break down the prompt:

1. We give the LLM a friendly personality, which is an optional but crucial feature for user-facing applications.
2. We provide the LLM with knowledge of the database schema that it will operate on.
3. We give example interactions to reinforce how the LLM should operate.
4. We give more fine-tuned instructions and constraints
5. We tell the LLM how to use its tools

After writing our prompt, we go through our agent loop and we can now use our Librarian.

```python
import asyncio

asyncio.run(Librarian().run())
# (User): Can you recommend me a fantasy book?
# (Assistant): I recommend "The Name of the Wind" by Patrick Rothfuss. It's the first book in the "Kingkiller Chronicle" series and follows the story of Kvothe, a gifted young man who grows up to be a notorious musician and magician. The storytelling is beautifully crafted, and it's a wonderful journey into a rich, imaginative world.

# If you're interested in more recommendations, just let me know!
# (User): Oh, I have not read that yet, can you add it to my list?
# (Assistant): INSERT INTO ReadingList (title, status) VALUES ('The Name of the Wind', 'Not Started');
# I've added "The Name of the Wind" to your reading list with the status set to "Not Started." Enjoy your reading adventure! If you need any more recommendations or assistance, just let me know.
# (User): I just finished reading The Name of the Wind and I really enjoyed it
# (Assistant): That's wonderful to hear! I'm glad you enjoyed "The Name of the Wind." Would you like me to update the status to "Complete" and add a rating for it? If so, how many stars would you like to give it?
# (User): Yes, I would. Can you give it 5 stars?
# (Assistant): UPDATE ReadingList SET status = 'Complete', rating = 5 WHERE title = 'The Name of the Wind';
# I've updated the status of "The Name of the Wind" to "Complete" and gave it a rating of 5 stars! If you're looking for your next great read or need any more assistance, feel free to ask. Happy reading!
```

Note that the SQL statements in the dialogue are there for development purposes.

Having established that we can have a quality conversation with our `Librarian`, we can now enhance our prompt. However, we must ensure that these improvements don't compromise the Librarian's core functionality. Check out [Evaluating SQL Agent](../evals/evaluating_sql_agent.md) for an in-depth guide on how we evaluate the quality of our prompt.



!!! tip "Additional Real-World Examples"
    - **Operations Assistant**: A read-only agent that retrieves data from databases, requiring no technical expertise.
    - **SQL Query Optimization**: Provide the agent with your data retrieval goals, and have it generate an efficient SQL query to meet your needs.
    - **Data Generation for Testing**: Request the agent to create and populate your database with realistic sample data to support development and testing processes.

When adapting this recipe to your specific use-case, consider the following:

- Experiment with the prompt, by adding query planning or other prompting techniques to break down a complex request.
- Experiment with different model providers to balance quality and speed.
- Use in a development or sandbox environment for rapid development.
