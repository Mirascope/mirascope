# Web Search Agent

In this recipe, we'll explore using Mirascope to enhance our Large Language Model (LLM) — specifically OpenAI's GPT-4o mini — by providing it with access to the web and its contents. We will be using DuckDuckGo's API as a tool for our Agentic workflow.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/agents/">Agents</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
In the past, users had to rely on search engines and manually browse through multiple web pages to find answers to their questions. Large Language Models (LLMs) have revolutionized this process. They can efficiently utilize search engine results pages (SERPs) and extract relevant content from websites. By leveraging this information, LLMs can quickly provide accurate answers to user queries, eliminating the need for active searching. Users can simply pose their questions and let the LLM work in the background, significantly streamlining the information retrieval process.
</p>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[openai]" beautifulsoup4  duckduckgo-search requests
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Add Web Search and Content Extraction

We'll use two pre-made tools from `mirascope.tools`:

1. `DuckDuckGoSearch`: For performing web searches through DuckDuckGo
2. `ParseURLContent`: For extracting content from webpages

The `DuckDuckGoSearch` tool provides search results with URLs while `ParseURLContent` handles the content extraction. We save our search results into `search_history` to provide context for future searches.

For a full list of available pre-made tools and their capabilities, check out the <a href="../../../learn/tools/#pre-made-tools\">Pre-made Tools documentation</a>.

## Add Q&A Functionality

Now that we have imported our tools, we can create our `prompt_template` and `_stream` function. We engineer the prompt to first use the `DuckDuckGoSearch` tool to find relevant pages, then `ParseURLContent` to extract content before answering the user question based on the retrieved information:


```python
from datetime import datetime

from pydantic import BaseModel

from mirascope.core import openai, prompt_template, BaseMessageParam
from mirascope.tools import DuckDuckGoSearch, ParseURLContent


class WebAssistantBaseWithStream(BaseModel):
    messages: list[BaseMessageParam | openai.OpenAIMessageParam] = []
    search_history: list[str] = []
    max_results_per_query: int = 2

    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template(  # noqa: F821
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
            "tools": [DuckDuckGoSearch, ParseURLContent],
            "computed_fields": {
                "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
        }

    async def _step(self, question: str):
        print(self.messages)
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
            print(f"(User): {question}", flush=True)
            print("(Assistant): ", end="", flush=True)
            await self._step(question)
            print()
```

There are a few things to note:

1. We set our `@openai.call()` to `stream=True` to provide a more responsive user experience.
2. We give the LLM the current date so the user does not need to provide that.
3. We instruct our LLM on how to use the pre-made tools we've imported.
    * User queries can often times be ambiguous so giving as much context to the LLM when it generates the search query is crucial.
    * Multiple search queries are generated for user queries that might rely on previous context.

By utilizing Mirascope's pre-made tools, we avoid having to implement web search and content extraction functionality ourselves. This allows us to focus on engineering the prompt and agent behavior rather than low-level implementation details.

### Example search queries

Let's look at how the search queries work together as context builds up...




```python
await WebAssistantBaseWithStream().run()
```


Search Queries:

* LLM development tool libraries
* best libraries for LLM development
* software engineering tools for LLM
* open source LLM libraries for developers
* programming libraries for large language models

By prompting the LLM to generate multiple queries, the LLM has access to a wide range of relevant information, including both open-source and commercial products, which it would have a significantly lower chance of doing with a single query.




```python
await WebAssistantBaseWithStream().run()
```


Search Queries:

* Mirascope library
* Mirascope library GitHub
* Mirascope Python
* What is Mirascope library used for
* Mirascope library overview
* Mirascope library features
* Mirascope library documentation

The LLM can gather information regarding the Mirascope library but has no context beyond that.

Let's take a look at what happens when we call the user queries together.


By giving the LLM search history, these search queries now connect the Mirascope library specifically to LLM development tools,
providing a more cohesive set of results.

We can now create our `_step` and `run` functions which will call our `_stream` and `_step` functions respectively.



```python
class WebAssistant(WebAssistantBaseWithStream):
    async def _step(self, question: str):
        print(self.messages)
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
```

The `run` function will keep running until the LLM feels that the users question can be answered.



```python
web_assistant = WebAssistant()
await web_assistant.run()
```

Note that by giving the LLM the current date, it'll automatically search for the most up-to-date information.

Check out [Evaluating Web Search Agent](../../evals/evaluating_web_search_agent) for an in-depth guide on how we evaluate the quality of our agent.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ol>
<li><p><b>Advanced Research Assistant</b></p>
<ul>
<li>Stay updated on latest developments in rapidly evolving fields</li>
</ul>
</li>
<li><p><b>Personalized Education</b></p>
<ul>
<li>Create customized learning materials based on current curricula</li>
</ul>
</li>
<li><p><b>Business Intelligence</b></p>
<ul>
<li>Assist in data-driven decision making with real-time insights</li>
</ul>
</li>
<li><p><b>Technical Support and Troubleshooting</b></p>
<ul>
<li>Assist in debugging by referencing current documentation</li>
</ul>
</li>
<li><p><b>Travel Planning</b></p>
<ul>
<li>Provide updates on travel restrictions, local events, and weather</li>
</ul>
</li>
<li><p><b>Journalism and Fact-Checking</b></p>
<ul>
<li>Help identify and combat misinformation</li>
</ul>
</li>
<li><p><b>Environmental Monitoring</b></p>
<ul>
<li>Track and analyze current climate data</li>
</ul>
</li>
</ol>
</div>

When adapting this recipe, consider:

* Optimizing the search by utilizing `async` to increase parallelism.
* When targeting specific websites for scraping purposes, use `response_model` to extract the specific information you're looking for across websites with similar content.
* Implement a feedback loop so the LLM can rewrite the query for better search results.
* Reduce the number of tokens used by storing the extracted webpages as embeddings in a vectorstore and retrieving only what is necessary.
* Make a more specific web search agent for your use-case rather than a general purpose web search agent.

