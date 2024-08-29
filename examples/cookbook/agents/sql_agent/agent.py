import asyncio
import sqlite3
from typing import ClassVar

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, ConfigDict

from mirascope.core import openai, prompt_template


class Librarian(BaseModel):
    con: ClassVar[sqlite3.Connection] = sqlite3.connect("database.db")
    messages: list[ChatCompletionMessageParam] = []

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


if __name__ == "__main__":
    librarian = Librarian()
    asyncio.run(librarian.run())
