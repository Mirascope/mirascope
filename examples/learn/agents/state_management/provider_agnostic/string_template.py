from mirascope import BaseMessageParam, llm, prompt_template
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[BaseMessageParam] = []

    @llm.call(provider="openai", model="gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM: You are a librarian
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str): ...

    def run(
        self,
        provider: llm.Provider,
        model: str,
    ) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            response = llm.override(self._call, provider=provider, model=model)(query)
            print(response.content)
            self.history += [
                response.user_message_param,
                response.message_param,
            ]


Librarian().run("anthropic", "claude-3-5-sonnet-latest")
