"""
An example of an librarian agent chatbot that remembers the interaction with the user.
This example streams the assistant response to the user.
"""

import os

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class Librarian(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-4o", stream=True)
    def _step(self, question: str):
        """
        SYSTEM: You are the world's greatest librarian.
        MESSAGES: {self.history}
        USER: {question}
        """

    def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            response = self._step(question)
            print("(Assistant): ", end="", flush=True)
            for chunk, _ in response:
                if chunk.user_message_param:
                    print(chunk.content, end="", flush=True)
            print()
            if response.user_message_param:
                self.history.append(response.user_message_param)
            self.history.append(response.message_param)


librarian = Librarian(history=[])
librarian.run()
