"""Mirascope implementation of LangGraph quickstart.

Here is the reference link to LangGraph quickstart:
    https://langchain-ai.github.io/langgraph/tutorials/introduction
"""

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class WebSearch(openai.OpenAITool):
    """Search the web for the given text and parse the paragraphs of the results."""

    query: str = Field(..., description="The text to search for.")

    def call(self) -> str:
        """Search the web for the given text and parse the paragraphs of the results.

        Returns:
            Parsed paragraphs of each of the webpages, separated by newlines.
        """
        try:
            # Search the web for the given text
            results = DDGS(proxy=None).text(self.query, max_results=2)

            # Parse the paragraphs of each resulting webpage
            parsed_results = []
            for result in results:
                link = result["href"]
                try:
                    response = requests.get(link)
                    soup = BeautifulSoup(response.content, "html.parser")
                    parsed_results.append(
                        "\n".join([p.text for p in soup.find_all("p")])
                    )
                except Exception as e:
                    parsed_results.append(
                        f"{type(e)}: Failed to parse content from URL {link}"
                    )

            return "\n\n".join(parsed_results)

        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"


class RequestAssistance(openai.OpenAITool):
    """A tool that requests assistance from a human expert."""

    query: str = Field(
        ...,
        description="The request for assistance needed to properly respond to the user",
    )

    def call(self) -> str:
        """Prompts a human to enter a response."""
        print(f"I am in need of assistance. {self.query}")
        response = input("\t(Human): ")
        return f"Human response: {response}"


class Chatbot(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-4o-mini", stream=True, tools=[WebSearch, RequestAssistance])
    @prompt_template(
        """
        SYSTEM:
        You are an expert web searcher. 
        Your task is to answer the user's question using the provided tools.
        You have access to the following tools:
            - `WebSearch`: Search the web for information.
            - `RequestAssistance`: Request assistance from a human expert if you do not
                know how to answer the question.

        Once you have gathered all of the information you need, generate a writeup that
        strikes the right balance between brevity and completeness. The goal is to
        provide as much information to the writer as possible without overwhelming them.

        MESSAGES: {self.history}
        USER: {question}
        """
    )
    def _call(self, question: str | None = None): ...

    def _interrupt_before(self, tool: openai.OpenAITool) -> openai.OpenAITool | None:
        """Interrupt before the tool is called. Return the modified tool or None."""
        if not isinstance(tool, WebSearch):
            return tool
        response = input(f"Do you want to use the {tool._name()} tool? (y/n): ")
        if response.lower() in ["n", "no"]:
            response = input(
                f"Do you want to modify the {tool._name()} tool's query? (y/n): "
            )
            if response.lower() in ["n", "no"]:
                return None
            else:
                tool.query = input("(Assistant): Enter a new query: ")
                return tool
        else:
            return tool

    def _step(self, question: str | None = None):
        response = self._call(question)
        tools_and_outputs = []
        for chunk, tool in response:
            if tool:
                new_tool = self._interrupt_before(tool)
                if new_tool:
                    tools_and_outputs.append((new_tool, new_tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        if response.user_message_param:
            self.history.append(response.user_message_param)
        self.history.append(response.message_param)
        if tools_and_outputs:
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step()
        return response.content

    def run(self):
        while True:
            question = input("(User): ")
            if question in ["quit", "exit"]:
                print("(Assistant): Have a great day!")
                break
            print("(Assistant): ", end="", flush=True)
            self._step(question)
            print("")


Chatbot().run()
