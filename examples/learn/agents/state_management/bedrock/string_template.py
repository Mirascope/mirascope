from mirascope.core import Messages, bedrock, prompt_template
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[bedrock.BedrockMessageParam] = []

    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
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
