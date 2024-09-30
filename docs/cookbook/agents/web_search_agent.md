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
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:7:12"
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:47:85"
```

We are grabbing the first 2 results that best match each of our user queries and retrieving their URLs. We save our search results into `search_history` to provide as context for future searches.

We also want to setup our `extract_content` tool which will take in a url and grab the HTML content.

```python
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:2:2"

--8<-- "examples/cookbook/agents/web_search_agent/agent.py:6:6"
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:13:46"
```

Notice that we did not define `extract_content` as a method of `WebAssistant`, since `extract_content` does not need to update state. 

Now that our tools are setup, we can proceed to implement the Q&A functionality of our `WebAssistant`.

## Add Q&A Functionality

Now that we have our tools we can now create our `prompt_template` and `_stream` function. We engineer the prompt to first use our `_web_search` tool, then `extract_content` from the tool before answering the user question based on the retrieved content:

```python
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:49:53"
    ...
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:86:119"
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
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:49:53"
    ...
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:120:145"   
```

The `run` function will keep running until the LLM feels that the users question can be answered.

```python
--8<-- "examples/cookbook/agents/web_search_agent/agent.py:148:175"
```

Note that by giving the LLM the current date, it'll automatically search for the most up-to-date information.

Check out [Evaluating Web Search Agent](../evals/evaluating_web_search_agent.ipynb) for an in-depth guide on how we evaluate the quality of our agent.

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
