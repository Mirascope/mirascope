from mirascope.core import BaseMessageParam, google
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[google.GoogleMessageParam] = []

    @google.call("gemini-1.5-flash")
    def _call(self, query: str) -> list[google.GoogleMessageParam]:
        return [
            BaseMessageParam(role="system", content="You are a librarian"),
            *self.history,
            BaseMessageParam(role="user", content=query),
        ]

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            response = self._call(query)
            print(response.content)
            self.history += [
                BaseMessageParam(role="user", content=query),
                response.message_param,
            ]


Librarian().run()
