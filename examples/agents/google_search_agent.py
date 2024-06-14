"""A google search agent that can be used to answer current questions using Mirascope"""
import os
from typing import Any

import requests
from bs4 import BeautifulSoup
from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

API_KEY = "YOUR_GOOGLE_SEARCH_API_KEY"
CSE_ID = "YOUR_CUSTOM_SEARCH_ENGINE_ID"
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
        print(data)
        items: list[dict[str, Any]] = data.get("items", [])
        if items:
            search_results = []
            for item in items:
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


class QuestionAnswerer(OpenAICall):
    prompt_template = """
    SYSTEM: 
    Answer the following question.
    You can use the search tool to answer the question.
    MESSAGES:
    {history}
    USER:
    {question}
    """
    question: str
    history: list[ChatCompletionMessageParam] = []
    call_params = OpenAICallParams(
        model="gpt-3.5-turbo",
        tools=[google_search],
        tool_choice="auto",
    )


forecast = QuestionAnswerer(question="What's the weather in Tokyo Japan?")
response = forecast.call()
forecast.history += [
    {"role": "user", "content": forecast.question},
    response.message.model_dump(),  # type: ignore
]

tool = response.tool
if tool:
    print("Tool arguments:", tool.args)
    output = tool.fn(**tool.args)
    print("Tool output:", output)
    forecast.history += [
        {
            "role": "tool",
            "content": output,
            "tool_call_id": tool.tool_call.id,
            "name": tool.__class__.__name__,
        },  # type: ignore
    ]
    forecast.question = ""
else:
    print(response.content)

response = forecast.call()
print("After Tools Response:", response.content)
