import json

from mirascope.core import BaseDynamicConfig, BaseMessageParam, gemini
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class Librarian(BaseModel):
    history: list[gemini.GeminiMessageParam] = []
    library: list[Book] = [
        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
    ]

    def _available_books(self) -> str:
        """Returns the list of books available in the library."""
        return json.dumps([book.model_dump() for book in self.library])

    @gemini.call("gemini-1.5-flash", stream=True)
    def _stream(self, query: str) -> BaseDynamicConfig:
        messages = [
            BaseMessageParam(role="system", content="You are a librarian"),
            *self.history,
            BaseMessageParam(role="user", content=query),
        ]
        return {"messages": messages, "tools": [self._available_books]}

    def _step(self, query: str) -> None:
        if query:
            self.history.append(BaseMessageParam(role="user", content=query))
        stream = self._stream(query)
        tools_and_outputs = []
        for chunk, tool in stream:
            if tool:
                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                tools_and_outputs.append((tool, tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        self.history.append(stream.message_param)
        if tools_and_outputs:
            self.history += stream.tool_message_params(tools_and_outputs)
            self._step("")

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            self._step(query)
            print()


Librarian().run()
