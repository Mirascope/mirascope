import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template

NIMBLE_TOKEN = "YOUR_NIMBLE_API_KEY"


def nimble_google_search(query: str):
    """
    Use Nimble to get information about the query using Google Search.
    """
    url = "https://api.webit.live/api/v1/realtime/serp"
    headers = {
        "Authorization": f"Basic {NIMBLE_TOKEN}",
        "Content-Type": "application/json",
    }
    search_data = {
        "parse": True,
        "query": query,
        "search_engine": "google_search",
        "format": "json",
        "render": True,
        "country": "US",
        "locale": "en",
    }
    response = requests.get(url, json=search_data, headers=headers)
    data = response.json()
    results = data["parsing"]["entities"]["OrganicResult"]
    urls = [result.get("url", "") for result in results]
    search_results = {}
    for url in urls:
        content = get_content(url)
        search_results[url] = content
    return search_results


def get_content(url: str):
    data = []
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    for paragraph in paragraphs:
        data.append(paragraph.text)
    return "\n".join(data)


@openai.call(
    model="gpt-4o-mini",
    tools=[nimble_google_search],
    call_params={"tool_choice": "required"},
)
@prompt_template(
    """
    SYSTEM:
    You are a an expert at finding information on the web.
    Use the `nimble_google_search` function to find information on the web.
    Rewrite the question as needed to better find information on the web.

    USER:
    {question}
    """
)
def search(question: str): ...


class SearchResponse(BaseModel):
    sources: list[str] = Field(description="The sources of the results")
    answer: str = Field(description="The answer to the question")


@openai.call(model="gpt-4o-mini", response_model=list[SearchResponse])
@prompt_template(
    """
    SYSTEM:
    Extract the question, results, and sources to answer the question based on the results.

    Results:
    {results}

    USER:
    {question}
    """
)
def extract(question: str, results: str): ...


def run(question: str):
    response = search(question)
    if tool := response.tool:
        output = tool.call()
        result = extract(question, output)
        return result


print(run("What is the average price of a house in the United States?"))
