# Generate SQL with LLM

In this recipe, we will be using OpenAI GPT-4o-mini to act as a co-pilot for a Database Admin. While LLMs are powerful and do pretty well at transforming laymen queries into SQL queries, it is still dangerous to do so without supervision. This recipe will have no guardrails for mutable operations and is purely for getting started.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/tools/">Tools</a></li>
<li><a href="../../../learn/async/">Async</a></li>
<li><a href="../../../learn/agents/">Agents</a></li>
</ul>
</div>

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

## Setup SQL Database

We will be using SQLite, but this example will work for any common SQL dialect, such as PostgreSQL, MySQL, MSSQL, and more.

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

from mirascope.core import BaseMessageParam, openai
from pydantic import BaseModel, ConfigDict


class LibrarianBase(BaseModel):
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
```


Now that we have our tools setup it is time to engineer our prompt

## Prompt Engineering

Knowing what tools are available is crucial when prompt engineering, so that we can tell the LLM when and how the tools should be used.

Now we will take our `Librarian` and add our `@openai.call`:



```python
from mirascope.core import prompt_template


class Librarian(LibrarianBase):
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
librarian = Librarian()
await librarian.run()
```

    (Assistant): SELECT * FROM ReadingList;
    It looks like your reading list is currently empty. If you're interested in fantasy books, I can recommend some excellent titles to get you started! Would you like some suggestions?
    (Assistant): Here are some fantastic fantasy books that you might enjoy:
    
    1. **"The Hobbit" by J.R.R. Tolkien** - A classic tale of adventure and friendship that follows a hobbit named Bilbo Baggins as he embarks on a quest to help a group of dwarves reclaim their homeland from a dragon.
    
    2. **"Harry Potter and the Sorcerer's Stone" by J.K. Rowling** - The beginning of a beloved series about a young boy discovering he is a wizard and attending Hogwarts School of Witchcraft and Wizardry.
    
    3. **"The Name of the Wind" by Patrick Rothfuss** - This is the first book in the "Kingkiller Chronicle" series, following the story of Kvothe, a gifted young man who grows up to become a legendary figure.
    
    4. **"A Darker Shade of Magic" by V.E. Schwab** - A captivating story set in a universe with parallel Londons, where only a few can travel between them and magic is a rare commodity.
    
    5. **"The Priory of the Orange Tree" by Samantha Shannon** - An epic standalone fantasy with a richly built world that features dragons, a matriarchal society, and diverse characters.
    
    If any of these titles pique your interest, just let me know and I can add them to your reading list!



Note that the SQL statements in the dialogue are there for development purposes.

Having established that we can have a quality conversation with our `Librarian`, we can now enhance our prompt. However, we must ensure that these improvements don't compromise the Librarian's core functionality. Check out [Evaluating SQL Agent](../../evals/evaluating_sql_agent) for an in-depth guide on how we evaluate the quality of our prompt.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Examples</p>
<ul>
<li><b>Operations Assistant</b>: A read-only agent that retrieves data from databases, requiring no technical expertise.</li>
<li><b>SQL Query Optimization</b>: Provide the agent with your data retrieval goals, and have it generate an efficient SQL query to meet your needs.</li>
<li><b>Data Generation for Testing</b>: Request the agent to create and populate your database with realistic sample data to support development and testing processes.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:

- Experiment with the prompt, by adding query planning or other prompting techniques to break down a complex request.
- Experiment with different model providers to balance quality and speed.
- Use in a development or sandbox environment for rapid development.


