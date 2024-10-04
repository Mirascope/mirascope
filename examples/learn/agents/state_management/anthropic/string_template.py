from mirascope.core import Messages, anthropic, prompt_template
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[anthropic.AnthropicMessageParam] = []

    @anthropic.call("claude-3-5-sonnet-20240620")
    @prompt_template(
        """
        SYSTEM: You are a librarian
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str): ...

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
