from mirascope.core import Messages, bedrock
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[bedrock.BedrockMessageParam] = []

    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
    def _call(self, query: str) -> Messages.Type:
        return [
            Messages.System("You are a librarian"),
            *self.history,
            Messages.User(query),
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
                Messages.User(query),
                response.message_param,
            ]


Librarian().run()
