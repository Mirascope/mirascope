# Generate SQL with LLM

In this recipe, we will be using OpenAI GPT-4o-mini to act as a co-pilot for a Database Admin. While LLMs are powerful and do pretty well at transforming laymen queries into SQL queries, it is still dangerous to do so without supervision. This recipe will have no guardrails for mutable operations and is purely for getting started.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Tools](../../learn/tools.md)
    - [Response Models](../../learn/response_models.md)
    - [Agents](../../learn/agents.md)

## Setup

We will be using SQLite but this example will work for any common SQL dialect, such as PostgreSQL, MySQL, MSSQL, and more.

```python
pip install sqlite3
```

## Setup SQL Database

Replace this part with whichever SQL dialect you are using, or skip if you have a database setup already.

```python
import sqlite3
con = sqlite3.connect("tutorial.db")
cur = con.cursor()
# ONE TIME SETUP
cur.execute(
    "CREATE TABLE movie(id INTEGER AUTO_INCREMENT PRIMARY KEY, title, year, score)"
)
cur.execute(
    "CREATE TABLE actor(id INTEGER AUTO_INCREMENT PRIMARY KEY, movie_id, name, age)"
)
cur.execute("""
    INSERT INTO movie (title, year, score) VALUES
        ('Monty Python and the Holy Grail', 1975, 8.2),
        ('And Now for Something Completely Different', 1971, 7.5)
""")
con.commit()
```

This will be our playground example.

## Write your Database Assistant

We will be creating an Agent that will take non-technical queries and translate them into SQL queries that will be executed. There will be two tools, `run_query` and `execute_query` , which will be a read operation and write operations respectively. Our agent will call the tools depending on what the user query is and return a response after running the query.

```python
import sqlite3

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, SkipValidation

from mirascope.core import openai, prompt_template

con = sqlite3.connect("database.db")
cur = con.cursor()

def run_query(query: str):
    """A SELECT query to run."""
    try:
        cur.execute(query)
        res = cur.fetchall()
        return res
    except sqlite3.Error as e:
        return str(e)

def execute_query(query: str):
    """An INSERT, UPDATE, or DELETE query to execute."""
    try:
        cur.execute(query)
        con.commit()
        return "Query executed successfully."
    except sqlite3.Error as e:
        return str(e)

class DatabaseAdministrator(BaseModel):
    messages: SkipValidation[list[ChatCompletionMessageParam]]

    @openai.call(model="gpt-4o-mini", tools=[run_query, execute_query])
    @prompt_template(
        """
        SYSTEM:
        You are a database admin that is an expert at writing SQLite queries.

        Your schema is as follows:
        TABLE movie(id, title, year, score)
        TABLE actor(id, movie_id, name, age)

        Translate the following text into a SQLite query. If the table or columns do not exist,
        return None. Then execute the query and return the results.

        Example:
        text: Show me the titles of all movies.
        query: SELECT title FROM movie;

        Example:
        text: Add Gone with the Wind to the movie table.
        query: INSERT INTO movie (title) VALUES ('Gone with the Wind', 1939, 8.1);

        MESSAGES: {self.messages}

        USER:
        {text}
        """
    )
    def _step(self, text: str): ...

    def _get_response(self, question: str = ""):
        response = self._step(question)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                output = tool.call()
                tools_and_outputs.append((tool, str(output)))
        else:
            print("(Assistant):", response.content)
            return
        if response.user_message_param:
            self.messages.append(response.user_message_param)
        self.messages += [
            response.message_param,
            *response.tool_message_params(tools_and_outputs),
        ]
        return self._get_response("")

    def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            self._get_response(question)

DatabaseAdministrator(messages=[]).run()

# (User): Can you grab my list of movies
# (Assistant): Here is your list of movies:

# 1. **Monty Python and the Holy Grail** (1975) - Score: 8.2
# 2. **And Now for Something Completely Different** (1971) - Score: 7.5
# (User): From my list of movies, can you populate my list of actor with actors that played in each movie
# (Assistant): I have successfully populated your list of actors for each movie. Each actor relevant to your movies has been added to the actor table. If you need any further assistance, feel free to ask!
# (User): Can you grab my list of actors and their respective movies
# (Assistant): Here is your list of actors along with their respective movies:

# 1. Graham Chapman - Monty Python and the Holy Grail
# 2. John Cleese - Monty Python and the Holy Grail
# 3. Terry Jones - Monty Python and the Holy Grail
# 4. Michael Palin - Monty Python and the Holy Grail
# 5. Eric Idle - Monty Python and the Holy Grail
# 6. Graham Chapman - And Now for Something Completely Different
# 7. John Cleese - And Now for Something Completely Different
# 8. Terry Jones - And Now for Something Completely Different
# 9. Michael Palin - And Now for Something Completely Different
# 10. Terry Gilliam - And Now for Something Completely Different
```

The below queries were called to generate the response for the user flow above.

```sql
SELECT * FROM movie;

INSERT INTO actor (movie_id, name, age) VALUES (1, 'Graham Chapman', 48);
INSERT INTO actor (movie_id, name, age) VALUES (1, 'John Cleese', 84);
INSERT INTO actor (movie_id, name, age) VALUES (1, 'Terry Jones', 75);
INSERT INTO actor (movie_id, name, age) VALUES (1, 'Michael Palin', 80);
INSERT INTO actor (movie_id, name, age) VALUES (1, 'Eric Idle', 80);
INSERT INTO actor (movie_id, name, age) VALUES (2, 'Graham Chapman', 48);
INSERT INTO actor (movie_id, name, age) VALUES (2, 'John Cleese', 84);
INSERT INTO actor (movie_id, name, age) VALUES (2, 'Michael Palin', 80);
INSERT INTO actor (movie_id, name, age) VALUES (2, 'Terry Gilliam', 81);

SELECT actor.name, movie.title FROM actor JOIN movie ON actor.movie_id = movie.id;
```

!!! tip "Additional Real-World Examples"
    - **Operations Assistant**: A read-only agent that retrieves data from databases, requiring no technical expertise.
    - **SQL Query Optimization**: Provide the agent with your data retrieval goals, and have it generate an efficient SQL query to meet your needs.
    - **Data Generation for Testing**: Request the agent to create and populate your database with realistic sample data to support development and testing processes.

When adapting this recipe to your specific use-case, consider the following:

- Experiment with the prompt, by adding query planning or other prompting techniques to break down a complex request.
- Experiment with different model providers to balance quality and speed.
- Use in a development or sandbox environment for rapid development.
