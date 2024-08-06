"""A google search agent that can be used to answer current questions using Mirascope"""

import os
from typing import Any

import requests
from bs4 import BeautifulSoup  # type: ignore
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"

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
        if items:
            search_results = []
            for item in items[:5]:
                link = item.get("link", "")
                search_results.append(parse_content(link))
            return "\n".join(search_results)
        else:
            return ""
    except Exception:
        return ""


def parse_content(link: str) -> str:
    """Parse the content of a webpage.

    Args:
        link (str): The URL of the webpage.

    Returns:
        str: The content of the webpage, separated by a newline.
    """
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        data = []
        for paragraph in paragraphs:
            data.append(paragraph.text)
        return "\n".join(data)
    except Exception:
        return ""


class GoogleBot(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-3.5-turbo", tools=[google_search])
    def _step(self, question: str):
        """
        SYSTEM:
        Answer the following question.
        You can use the search tool to answer the question.

        MESSAGES:
        {self.history}

        USER:
        {question}
        """

    def run(self, question: str, depth=2):
        i = 0
        while i < depth:
            response = self._step(question)
            self.history += [response.user_message_param, response.message_param]
            if tool := response.tool:
                output = tool.call()
                self.history += response.tool_message_params([(tool, output)])
            else:
                return response.content
            i += 1


forecast = GoogleBot().run("What's the weather in Tokyo Japan?")
print(forecast)
