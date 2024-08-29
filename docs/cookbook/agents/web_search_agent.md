# Web Search Agent

In this recipe, we'll explore using Mirascope to enhance our Large Language Model (LLM) — specifically OpenAI's GPT-4o mini — by providing it with access to the web and its contents. We will be using DuckDuckGo's API as a tool for our Agentic workflow.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Agents](../../learn/agents.md)

!!! note "Background"

    In the past, users had to rely on search engines and manually browse through multiple web pages to find answers to their questions. Large Language Models (LLMs) have revolutionized this process. They can efficiently utilize search engine results pages (SERPs) and extract relevant content from websites. By leveraging this information, LLMs can quickly provide accurate answers to user queries, eliminating the need for active searching. Users can simply pose their questions and let the LLM work in the background, significantly streamlining the information retrieval process.

## Setting Up Your Environment

To set up our environment, first let's install all of the packages we will use:

```shell
pip install "mirascope[openai]", bs4, duckduckgo-search
```

Make sure to also set your `OPENAI_API_KEY` if you haven't already. We are using `duckduckgo-search` since it does not require an API key, but feel free to use Google Search API or other search engine APIs.

## Add DuckDuckGo Tool

The first step is to create a `WebAssistant` that first conducts a web search based on the user's query. Let’s go ahead and create our `WebAssistant` and add our web search tool:

```python
import requests
from duckduckgo_search import DDGS
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

class WebAssistant(BaseModel):
    messages: list[ChatCompletionMessageParam] = []
    search_history: list[str] = []

    def _web_search(self, queries: list[str]) -> str:
        """Performs web searches for given queries and returns URLs.

        Args:
            queries: List of search queries.

        Returns:
            str: Newline-separated URLs from search results or error messages.

        Raises:
            Exception: If web search fails entirely.
        """
        try:
            urls = []
            for query in queries:
                results = DDGS(proxies=None).text(query, max_results=2)

                for result in results:
                    link = result["href"]
                    try:
                        urls.append(link)
                    except Exception as e:
                        urls.append(
                            f"{type(e)}: Failed to parse content from URL {link}"
                        )
                self.search_history.append(query)
            return "\n\n".join(urls)

        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"
```

We are grabbing the first 2 results that best match each of our user queries and retrieving their URLs. We save our search results into `search_history` to provide as context for future searches.

We also want to setup our `extract_content` tool which will take in a url and grab the HTML content.

```python
import re

from bs4 import BeautifulSoup


def extract_content(url: str) -> str:
    """Extract the main content from a webpage.

    Args:
        url: The URL of the webpage to extract the content from.

    Returns: 
        The extracted content as a string.
    """
    try:
        response = requests.get(url, timeout=5)

        soup = BeautifulSoup(response.content, "html.parser")

        unwanted_tags = ["script", "style", "nav", "header", "footer", "aside"]
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile("content|main"))
        )

        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        lines = (line.strip() for line in text.splitlines())
        return "\n".join(line for line in lines if line)
    except Exception as e:
        return f"{type(e)}: Failed to extract content from URL {url}"
```

Notice that we did not define `extract_content` as a method of `WebAssistant`, since `extract_content` does not need to update state. 

Now that our tools are setup, we can proceed to implement the Q&A functionality of our `WebAssistant`.

## Add Q&A Functionality

Now that we have our tools we can now create our `prompt_template` and `_stream` function. We engineer the prompt to first use our `_web_search` tool, then `extract_content` from the tool before answering the user question based on the retrieved content:

```python
from mirascope.core import openai, prompt_template


class WebAssistant(BaseModel):
    messages: list[ChatCompletionMessageParam] = []
    search_history: list[str] = []

    def _web_search(self, queries: list[str]) -> str:
        ...

    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM:
        You are an expert web searcher. Your task is to answer the user's question using the provided tools.
        The current date is {current_date}.

        You have access to the following tools:
        - `_web_search`: Search the web when the user asks a question. Follow these steps for EVERY web search query:
            1. There is a previous search context: {self.search_history}
            2. There is the current user query: {question}
            3. Given the previous search context, generate multiple search queries that explores whether the new query might be related to or connected with the context of the current user query. 
                Even if the connection isn't immediately clear, consider how they might be related.
        - `extract_content`: Parse the content of a webpage.

        When calling the `_web_search` tool, the `body` is simply the body of the search
        result. You MUST then call the `extract_content` tool to get the actual content
        of the webpage. It is up to you to determine which search results to parse.

        Once you have gathered all of the information you need, generate a writeup that
        strikes the right balance between brevity and completeness based on the context of the user's query.

        MESSAGES: {self.messages}
        USER: {question}
        """
    )
    async def _stream(self, question: str) -> openai.OpenAIDynamicConfig:
        return {
            "tools": [self._web_search, extract_content],
            "computed_fields": {
                "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
        }

```

There are a few things to note:

1. We set our `@openai.call()` to `stream=True` to provide a more responsive user experience.
2. We give the LLM the current date so the user does not need to provide that.
3. We instruct our LLM on how to use the tools.
    * User queries can often times be ambiguous so giving as much context to the LLM when it generates the search query is crucial.
    * Multiple search queries are generated for user queries that might rely on previous context.

### Example search queries

```bash
(User): I am a SWE looking for a LLM dev tool library
```

Search Queries:

* LLM development tool libraries
* best libraries for LLM development
* software engineering tools for LLM
* open source LLM libraries for developers
* programming libraries for large language models

By prompting the LLM to generate multiple queries, the LLM has access to a wide range of relevant information, including both open-source and commercial products, which it would have a significantly lower chance of doing with a single query.

```bash
(User): What is Mirascope library?
```

Search Queries:

* Mirascope library
* what is Mirascope
* Mirascope Python library
* Mirascope library documentation
* Mirascope library features
* Mirascope library use cases
* Mirascope library tutorial

The LLM can gather information regarding the Mirascope library but has no context beyond that.

Let's take a look at what happens when we call the user queries together.

```bash
(User): I am a SWE looking for a LLM dev tool library
(Assistant): ...
(User): What is Mirascope library?
```

Search Queries:

* Mirascope library
* Mirascope LLM development
* Mirascope open source
* Mirascope Python library
* LLM tools Mirascope

By giving the LLM search history, these search queries now connect the Mirascope library specifically to LLM development tools,
providing a more cohesive set of results.

We can now create our `_step` and `run` functions which will call our `_stream` and `_step` functions respectively.

```python
async def _step(self, question: str):
    response = await self._stream(question)
    tools_and_outputs = []
    async for chunk, tool in response:
        if tool:
            print(f"using {tool._name()} tool with args: {tool.args}")
            tools_and_outputs.append((tool, tool.call()))
        else:
            print(chunk.content, end="", flush=True)
    if response.user_message_param:
        self.messages.append(response.user_message_param)
    self.messages.append(response.message_param)
    if tools_and_outputs:
        self.messages += response.tool_message_params(tools_and_outputs)
        await self._step("")

async def run(self):
    while True:
        question = input("(User): ")
        if question == "exit":
            break
        print("(Assistant): ", end="", flush=True)
        await self._step(question)
        print()
```

The `run` function will keep running until the LLM feels that the users question can be answered.

```python
print(WebAssistant().run("What are the top 5 smartphones"))
# > 1. **iPhone 15 Pro Max**
#      - **Best Overall:**
#        - The iPhone 15 Pro Max offers a powerful A17 chipset, a versatile camera system with a 5x zoom telephoto lens, and a premium design with titanium sides. It's noted for its remarkable battery life and robust performance.
#
#   2. **Samsung Galaxy S24 Ultra**
#      - **Best Samsung Phone:**
#        - The Galaxy S24 Ultra features a Qualcomm Snapdragon 8 Gen 3 processor, a stunning OLED display, and a highly capable camera system with a new 50MP shooter for 5x zoom. It stands out for its AI capabilities and impressive battery life.
#
#   3. **Google Pixel 8 Pro**
#      - **Smartest Camera:**
#        - The Pixel 8 Pro is celebrated for its AI-driven photo-editing features, including Magic Editor and Magic Audio Eraser. It sports a Tensor G3 chip, a high-resolution display, and enhanced camera sensors, providing excellent low-light performance and a support period extending to seven years of updates.
#
#   4. **Google Pixel 8a**
#      - **Best Under $500:**
#        - The Pixel 8a delivers high performance with its Tensor G3 chipset, a bright OLED display, and strong camera capabilities for its price range. It also offers Google's AI features and promises seven years of updates, making it an excellent budget option.
#
#   5. **iPhone 15**
#      - **Best iPhone Value:**
#        - The iPhone 15 includes a 48MP main camera, supports USB-C, and features Apple's A16 Bionic chipset. It provides good value with solid performance, camera quality, and a user-friendly experience.
#
#   These smartphones have been chosen based on their overall performance, camera capabilities, battery life, and additional features like AI integration and long-term software support.
```

Note that by giving the LLM the current date, it'll automatically search for the most up-to-date information.

Check out [Evaluating Web Search Agent](../evals/evaluating_web_search_agent.md) for an in-depth guide on how we evaluate the quality of our agent.

!!! tip "Additional Real-World Applications"

    1. Advanced Research Assistant
        - Stay updated on latest developments in rapidly evolving fields

    2. Personalized Education
        - Create customized learning materials based on current curricula

    3. Business Intelligence
        - Assist in data-driven decision making with real-time insights

    4. Technical Support and Troubleshooting
        - Assist in debugging by referencing current documentation

    5. Travel Planning
        - Provide updates on travel restrictions, local events, and weather

    6. Journalism and Fact-Checking
        - Help identify and combat misinformation

    7. Environmental Monitoring
        - Track and analyze current climate data

When adapting this recipe, consider:

* Optimizing the search by utilizing `async` to increase parallelism.
* When targeting specific websites for scraping purposes, use `response_model` to extract the specific information you're looking for across websites with similar content.
* Implement a feedback loop so the LLM can rewrite the query for better search results.
* Reduce the number of tokens used by storing the extracted webpages as embeddings in a vectorstore and retrieving only what is necessary.
* Make a more specific web search agent for your use-case rather than a general purpose web search agent.
