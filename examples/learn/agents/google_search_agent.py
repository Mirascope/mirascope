from typing import Any

import requests
from bs4 import BeautifulSoup
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai, prompt_template

API_KEY = "YOUR_GOOGLE_SEARCH_KEY"
CSE_ID = "YOUR_GOOGLE_CSE_ID"
BASE_URL = "https://www.googleapis.com/customsearch/v1"


def google_search(query: str) -> str:
    """Google Search tool to find relevant information about a query.

    Args:
        query (str): The query to search for.

    Returns:
        str: The content of webpages, separated by a newline.
    """
    params = {"key": API_KEY, "cx": CSE_ID, "q": query}

    try:
        response = requests.get(BASE_URL, params=params)
        data: dict[str, Any] = response.json()
        items: list[dict[str, Any]] = data.get("items", [])
        search_results = []
        for item in items[:5] or []:
            link = item.get("link", "")
            paragraphs = BeautifulSoup(
                requests.get(link).content, "html.parser"
            ).find_all("p")
            search_results.append("\n".join([p.text for p in paragraphs]))
        return "\n".join(search_results)
    except Exception:
        return "Failed to retrieve search results"


class GoogleBot(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-3.5-turbo", tools=[google_search])
    @prompt_template(
        """
        SYSTEM: Answer the user's question using your `google_search` tool.
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str): ...

    def _step(self, query: str):
        response = self._call(query)
        self.history += [response.user_message_param, response.message_param]
        if tools := response.tools:
            for tool in tools:
                self.history += response.tool_message_params([(tool, tool.call())])
            return self._step("")
        else:
            return response.content

    def run(self):
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            response = self._step(query)
            print(f"(Assistant): {response}")


bot = GoogleBot()
bot.run()
