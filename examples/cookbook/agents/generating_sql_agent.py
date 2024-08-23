import sqlite3

from dotenv import load_dotenv
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, SkipValidation

from mirascope.core import openai, prompt_template

con = sqlite3.connect("database.db")
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
# END OF ONE TIME SETUP
load_dotenv()


def run_query(query: str):
    """A SELECT query to run."""
    print(query)
    try:
        cur.execute(query)
        res = cur.fetchall()
        return res
    except sqlite3.Error as e:
        return str(e)


def execute_query(query: str):
    """An INSERT, UPDATE, or DELETE query to execute."""
    print(query)
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
