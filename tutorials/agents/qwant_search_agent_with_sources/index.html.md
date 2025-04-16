# Qwant Search Agent with Sources

This notebook tutorial walks through the implementation of a web agent that uses Large Language Models (LLMs) to perform intelligent web searches and extract relevant information. We'll use the Groq API for our LLM calls and the Qwant search engine for web queries.

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
When generating information using LLMs, it's important to note that the generated outputs can often be hallucinated. This remains true even when supplying information from searching the web to the LLM as context for its generation. This makes it extremely important to maintain and include sources alongside the generated output so that the output can be better verified.
</p>
</div>

## Setup

First, let's install the necessary packages:


```python
!pip install "mirascope[groq]" requests beautifulsoup4 python-dotenv tenacity
```

Now, let's import the required libraries and load our environment variables:


```python
import os

os.environ["GROQ_API_KEY"] = "gsk_..."
# Set the appropriate API key for the provider you're using
```


```python
import re
import time
from typing import Any, Callable

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from mirascope.core import prompt_template
from mirascope.core.groq import groq_call
```


Now that we have created our tool, it’s time to create our LLM call.

## Qwant API Implementation

Let's implement the Qwant API class for performing web searches:


```python
class QwantApi:
    BASE_URL = "https://api.qwant.com/v3"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            }
        )

    def search(
        self,
        q: str,
        search_type: str = "web",
        locale: str = "en_US",
        offset: int = 0,
        safesearch: int = 1,
    ) -> dict[str, Any]:
        params = {"q": q, "locale": locale, "offset": offset, "safesearch": safesearch}
        url = f"{self.BASE_URL}/search/{search_type}"
        response = self.session.get(url, params=params)
        return response.json() if response.status_code == 200 else None
```

This class encapsulates the functionality to interact with the Qwant search API. It allows us to perform searches of different types (web, news, images, videos) and handles the API request details.

## Data Models

Next, let's define our data models using Pydantic:


```python
class SearchResponse(BaseModel):
    answer: str = Field(description="The answer to the question")
    sources: list[str] = Field(description="The sources used to generate the answer")


class SearchType(BaseModel):
    search_type: str = Field(
        description="The type of search to perform (web, news, images, videos)"
    )
    reasoning: str = Field(description="The reasoning behind the search type selection")


class OptimizedQuery(BaseModel):
    query: str = Field(description="The optimized search query")
    reasoning: str = Field(description="The reasoning behind the query optimization")
```

These Pydantic models define the structure for our data:
- `SearchResponse`: Represents the final answer and its sources
- `SearchType`: Represents the chosen search type and the reasoning behind it
- `OptimizedQuery`: Represents an optimized search query and the reasoning for the optimization



## Implement Throttling

Let's create a decorator for throttling our API calls:


```python
def throttle(calls_per_minute: int) -> Callable:
    min_interval = 60.0 / calls_per_minute
    last_called: list[float] = [0.0]

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret

        return wrapper

    return decorator


# Modify the groq_call decorator to include throttling and retrying
def throttled_groq_call(*args: Any, **kwargs: Any) -> Any:
    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5)
    )
    @throttle(calls_per_minute=6)  # Adjust this value based on your rate limit
    def wrapped_call(*call_args, **call_kwargs):
        return groq_call(*args, **kwargs)(*call_args, **call_kwargs)

    return wrapped_call
```

## Determine Search Type

Now, let's implement the function to determine the most appropriate search type:



```python
@throttled_groq_call(
    "llama-3.2-90b-text-preview", response_model=SearchType, json_mode=True
)
@prompt_template(
    """
SYSTEM:
You are an expert at determining the most appropriate type of search for a given query. Your task is to analyze the user's question and decide which Qwant search type to use: web, news, images, or videos.

Follow these strict guidelines:
1. For general information queries, use 'web'.
2. For recent events, breaking news, or time-sensitive information, use 'news'.
3. For queries explicitly asking for images or visual content, use 'images'.
4. For queries about video content or asking for video results, use 'videos'.
5. If unsure, default to 'web'.

Provide your decision in a structured format with the search type and a brief explanation of your reasoning.

USER:
Determine the most appropriate search type for the following question:
{question}

ASSISTANT:
Based on the question, I will determine the most appropriate search type and provide my reasoning.
"""
)
def determine_search_type(question: str) -> SearchType:
    """
    Determine the most appropriate search type for the given question.
    """
    ...
```

This function uses the Groq API to determine the most appropriate search type based on the user's question. It uses a prompt template to guide the LLM in making this decision.

## Web Search Function

Let's implement the function to perform the actual web search using Qwant:



```python
def qwant_search(query: str, search_type: str, max_results: int = 5) -> dict[str, str]:
    """
    Use Qwant to get information about the query using the specified search type.
    """
    print(f"Searching Qwant for '{query}' using {search_type} search...")
    search_results = {}
    qwant = QwantApi()
    results = qwant.search(query, search_type=search_type)

    if (
        results
        and "data" in results
        and "result" in results["data"]
        and "items" in results["data"]["result"]
    ):
        items = results["data"]["result"]["items"]
        if isinstance(items, dict) and "mainline" in items:
            items = items["mainline"]

        count = 0
        for item in items:
            if "url" in item:
                url = item["url"]
                print(f"Fetching content from {url}...")
                content = get_content(url)
                search_results[url] = content
                count += 1
                if count >= max_results:
                    break
            elif isinstance(item, dict) and "items" in item:
                for subitem in item["items"]:
                    if "url" in subitem:
                        url = subitem["url"]
                        print(f"Fetching content from {url}...")
                        content = get_content(url)
                        search_results[url] = content
                        count += 1
                        if count >= max_results:
                            break
                if count >= max_results:
                    break

    return search_results


def get_content(url: str) -> str:
    """
    Fetch and parse content from a URL.
    """
    data = []
    try:
        response = requests.get(url)
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        paragraphs = soup.find_all("p")
        for paragraph in paragraphs:
            data.append(paragraph.text)
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
    return "\n".join(data)
```

These functions handle the web search process:
- `qwant_search`: Performs the search using the Qwant API and fetches content from the resulting URLs
- `get_content`: Fetches and parses the content from a given URL using BeautifulSoup

## Search and Extract Functions

Now, let's implement the functions to process the search results and extract the final answer:


```python
@groq_call("llama-3.2-90b-text-preview")
@prompt_template(
    """
SYSTEM:
You are an expert at finding information on the web.
Use the provided search results to answer the question.
Rewrite the question as needed to better find information on the web.
Search results:
{search_results}

USER:
{question}
"""
)
def search(question: str, search_results: dict[str, str]) -> str:
    """
    Use the search results to answer the user's question.
    """
    # The model will return an answer based on the search results and question
    ...


@throttled_groq_call(
    "llama-3.2-90b-text-preview", response_model=SearchResponse, json_mode=True
)  # Changed response_model from SearchType to SearchResponse
@prompt_template(
    """
SYSTEM:
Extract the answer to the question based on the search results.
Provide the sources used to answer the question in a structured format.
Search results:
{results}

USER:
{question}
"""
)
def extract(
    question: str, results: dict[str, str]
) -> SearchResponse:  # This function should return SearchResponse, not SearchType
    """
    Extract a concise answer from the search results and include sources.
    """
    ...


def clean_text(text: str) -> str:
    """
    Clean the text data for better formatting and readability.
    """
    # Removing extra spaces and special characters
    return re.sub(r"\s+", " ", text).strip()
```

These functions process the search results:
- `search`: Uses the Groq API to generate an answer based on the search results
- `extract`: Extracts a concise answer and the sources used from the search results
- `clean_text`: Cleans the text output for better readability

## Main Execution Function

Finally, let's implement the main execution function that orchestrates the entire process:


```python
def run(question: str) -> SearchResponse:
    """
    Orchestrate the search and extraction process to answer the user's question.
    """
    print(f"Processing question: '{question}'")

    # Step 1: Determine the appropriate search type
    search_type_result = determine_search_type(question)
    print(f"Selected search type: {search_type_result.search_type}")
    print(f"Reasoning: {search_type_result.reasoning}")

    # Step 2: Search the web using Qwant with the determined search type
    search_results = qwant_search(question, search_type_result.search_type)

    # Step 3: Use Groq Llama model to summarize search results
    response = search(question, search_results)
    print(f"Search response: {response}")

    # Step 4: Extract the final answer and structured sources
    result = extract(question, search_results)

    # Step 5: Clean the output for readability
    result.answer = clean_text(result.answer)
    print(f"Final result: {result}")

    return result
```

This `run` function orchestrates the entire process:
1. Determines the appropriate search type
2. Performs the web search
3. Summarizes the search results
4. Extracts the final answer and sources
5. Cleans the output for readability

## Usage Example

Let's add an example usage of our web agent:


```python
if __name__ == "__main__":
    print("Example usage:")
    response = run("what is the latest on donald trump and elon musk?")
    print(response)
```

This example demonstrates how to use the `run` function to process a question and get a response.

## Conclusion

This notebook tutorial has walked through the implementation of a web agent that uses LLMs to perform intelligent web searches and extract relevant information. The agent determines the most appropriate search type, performs the search, processes the results, and provides a structured response with sources.

Key components of this implementation include:
1. Qwant API integration for web searches
2. Groq API integration for LLM-powered decision making and information extraction
3. Pydantic models for structured data handling
4. Implemented retry logic with exponential backoff using the tenacity library.
5. BeautifulSoup for web scraping
6. Prompt engineering for guiding LLM behavior

This web agent can be extended and customized for various applications, such as research assistants, fact-checking tools, or automated information gathering systems.
