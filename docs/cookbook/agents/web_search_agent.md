# Web Scraper

In this recipe we’ll explore using Mirascope to get structured information from scraping the web — in this case using OpenAI GPT 4o. We will be using DuckDuckGo's API as a tool for our Agentic workflow.

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

The first step is to create a `WebAssistant` that first conducts a web search based on the user's query. Let’s go ahead and add our web search tool:

```python
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

def web_search(text: str) -> str:
    """Search the web for the given text and parse the paragraphs of the results.

    Args:
        text: The text to search for.

    Returns:
        Parsed paragraphs of each of the webpages, separated by newlines.
    """
    try:
        # Search the web for the given text
        results = DDGS(proxy=None).text(text, max_results=5)
        
        # Parse the paragraphs of each resulting webpage
        parsed_results = []
        for result in results:
            link = result["href"]
            try:
                response = requests.get(link)
                soup = BeautifulSoup(response.content, "html.parser")
                parsed_results.append("\n".join([p.text for p in soup.find_all("p")]))
            except Exception as e:
                parsed_results.append(f"{type(e)}: Failed to parse content from URL {link}")
        
        return "\n\n".join(parsed_results)
    
    except Exception as e:
        return f"{type(e)}: Failed to search the web for text"
```

We are grabbing the first 5 results that best match our user query and retrieving their URLs, for parsing and use BeautifulSoup to assist in extracting all paragraph tags in the HTML.

Depending on your use-case, you may want to let the LLM decide which urls to use by separating search and parsing into two separate tools.

Now that our tool is setup, we can proceed to implement the Q&A functionality of our `WebAssistant`.

## Add Q&A Functionality

Now that we have our tools we can now create our prompt_template and `_step` function. We engineer the prompt to first use our `web_search` tool and then answer the user question based on the retrieved content:

```python
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class WebAssistant(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-4o", stream=True, tools=[web_search])
    @prompt_template(
        """
        SYSTEM:
        You are an expert web searcher. Your task is to answer the user's question using the provided tools.
        Use the tool `web_search` once to gather the required information.
        After using the tool, provide a comprehensive answer to the user's question based on the information you retrieved.

        MESSAGES:
        {self.history}

        USER:
        {question}
        """
    )
    def _step(self, question: str): ...

```

We set our `@openai.call()` to `stream=True` to provide a more responsive user experience. We can now create our `run` function which will call our `_step` function, which will loop until it answers the users question.

```python
def run(self, prompt: str) -> str:
    stream = self._step(prompt)
    result, tools_and_outputs = "", []
    for chunk, tool in stream:
        if tool:
            tools_and_outputs.append((tool, tool.call()))
        else:
            result += chunk.content
            print(chunk.content, end="", flush=True)
    if stream.user_message_param:
        self.history.append(stream.user_message_param)
    self.history.append(stream.message_param)
    if tools_and_outputs:
        self.history += stream.tool_message_params(tools_and_outputs)
        return self.run("")
    return result
```

The `run` function will keep running until the LLM feels that the users question can be answered.

```python
print(WebAssistant().run("What are the top 5 smartphones of 2024?"))
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

- Optimizing the search by utilizing `async` to increase parallelism.
- Separate `web_search` into `serp_tool` and `parse_web` tools, so the LLM can pick and choose which url to parse.
- When targeting specific websites for scrapping purposes, use `response_model` to extract the specific information you're looking for across websites with similar content.
- Implement a feedback loop so the LLM can rewrite the query for better search results.
