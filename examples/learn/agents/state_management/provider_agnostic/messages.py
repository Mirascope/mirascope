from typing import Literal

from mirascope.core import (
    BaseMessageParam,
    Messages,
    anthropic,
    openai,
    prompt_template,
)
from mirascope.core.base import BaseCallResponse
from pydantic import BaseModel


class Librarian(BaseModel):
    provider: Literal["openai", "anthropic"]
    model: Literal["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
    history: list[BaseMessageParam] = []

    @prompt_template()
    def _prompt(self, query: str) -> Messages.Type:
        return [
            Messages.System("You are a librarian"),
            *self.history,
            Messages.User(query),
        ]

    def _call(self, query: str) -> BaseCallResponse:
        if self.provider == "openai":
            call = openai.call(self.model)(self._prompt)
        elif self.provider == "anthropic":
            call = anthropic.call(self.model)(self._prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        return call(query)

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


Librarian(provider="openai", model="gpt-4o-mini").run()
