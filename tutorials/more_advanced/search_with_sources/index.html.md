# Search with Sources

This recipe shows how to use LLMs — in this case, GPT 4o mini — to answer questions using the web. Since LLMs often time hallucinate answers, it is important to fact check and verify the accuracy of the answer.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/tools/">Tools</a></li>
<li><a href="../../../learn/chaining/">Chaining</a></li>
<li><a href="../../../learn/response_models/">Response Model</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
Users of Large Language Models (LLMs) often struggle to distinguish between factual content and potential hallucinations, leading to time-consuming fact-checking. By implementing source citation requirements, LLMs need to rely on verified information, thereby enhancing the accuracy of its responses and reducing the need for manual verification.
</p>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[openai]" beautifulsoup4
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```


We will need an API key for search:

- [Nimble API Key](https://nimbleway.com/) or alternatively directly from Google [Custom Search](https://developers.google.com/custom-search/v1/introduction/) API.

## Creating Google Search tool

We use [Nimble](https://nimbleway.com/) since they provide an easy-to-use API for searching, but an alternative you can use is Google's Custom Search API. We first want to grab all the urls that are relevant to answer our question and then we take the contents of those urls, like so:


```python
import requests
from bs4 import BeautifulSoup

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
```


Now that we have created our tool, it’s time to create our LLM call.

## Creating the first call

For this call, we force the LLM to always use its tool which we will later chain.



```python
from mirascope.core import openai, prompt_template


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
```


We ask the LLM to rewrite the question to make it more suitable for search.

Now that we have the necessary data to answer the user query and their sources, it’s time to extract all that information into a structured format using `response_model`

## Extracting Search Results with Sources

As mentioned earlier, it is important to fact check all answers in case of hallucination, and the first step is to ask the LLM to cite its sources:



```python
from pydantic import BaseModel, Field


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
```


and finally we create our `run` function to execute our chain:



```python
def run(question: str):
    response = search(question)
    if tool := response.tool:
        output = tool.call()
        result = extract(question, output)
        return result


print(run("What is the average price of a house in the United States?"))
```

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Journalism Assistant</b>: Have the LLM do some research to quickly pull verifiable sources for blog posts and news articles.</li>
<li><b>Education</b>: Find and cite articles to help write academic papers.</li>
<li><b>Technical Documentation</b>: Generate code snippets and docs referencing official documentation.</li>
</ul>
</div>

When adapting this recipe, consider:
    - Adding [Tenacity](https://tenacity.readthedocs.io/en/latest/) `retry` for more a consistent extraction.
    - Use an LLM with web search tool to evaluate whether the answer produced is in the source.
    - Experiment with different model providers and version for quality and accuracy of results.

