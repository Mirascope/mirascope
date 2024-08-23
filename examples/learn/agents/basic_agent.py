from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class Librarian(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM: You are a helpful librarian assistant.
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str) -> openai.OpenAIDynamicConfig: ...

    def run(self):
        while True:
            query = input("User: ")
            if query.lower() == "exit":
                break

            response = self._call(query)
            print(f"Librarian: {response.content}")

            if response.user_message_param:
                self.history.append(response.user_message_param)
            self.history.append(response.message_param)


librarian = Librarian()
librarian.run()
