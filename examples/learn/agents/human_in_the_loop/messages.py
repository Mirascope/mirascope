from mirascope import BaseDynamicConfig, Messages, llm, BaseMessageParam
from pydantic import BaseModel


class Librarian(BaseModel):
    history: list[BaseMessageParam] = []

    def _ask_for_help(self, question: str) -> str:
        """Asks for help from an expert."""
        print("[Assistant Needs Help]")
        print(f"[QUESTION]: {question}")
        answer = input("[ANSWER]: ")
        print("[End Help]")
        return answer

    @llm.call(provider="openai", model="gpt-4o-mini")
    def _call(self, query: str) -> BaseDynamicConfig:
        messages = [
            Messages.System("You are a librarian"),
            *self.history,
            Messages.User(query),
        ]
        return {"messages": messages, "tools": [self._ask_for_help]}

    def _step(self, query: str) -> str:
        if query:
            self.history.append(Messages.User(query))
        response = self._call(query)
        self.history.append(response.message_param)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                tools_and_outputs.append((tool, tool.call()))
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step("")
        else:
            return response.content

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            step_output = self._step(query)
            print(step_output)


Librarian().run()
