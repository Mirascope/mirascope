# Search Agent with Sources

This recipe shows how to use LLMs — in this case, GPT 4o mini — to answer questions using the web. Since LLMs often time hallucinate answers, it is important to fact check and verify the accuracy of the answer.

## Setup

```bash
pip install beautifulsoup4
```

We will need an API key for search:

- [Nimble API Key](https://nimbleway.com/) or alternatively directly from Google [Custom Search](https://developers.google.com/custom-search/v1/introduction/) API.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Tools](../learn/tools.md)
    - [Chaining](../learn/chaining.md)
    - [Response Model](../learn/response_models.md)

!!! note "Background"

    Users of Large Language Models (LLMs) often struggle to distinguish between factual content and potential hallucinations, leading to time-consuming fact-checking. By implementing source citation requirements, LLMs need to rely on verified information, thereby enhancing the accuracy of its responses and reducing the need for manual verification.

## Creating Google Search tool

We use [Nimble](https://nimbleway.com/) since they provide an easy-to-use API for searching, but an alternative you can use is Google's Custom Search API. We first want to grab all the urls that are relevant to answer our question and then we take the contents of those urls, like so:

```python
--8<-- "examples/cookbook/search_with_sources.py:1:2"
--8<-- "examples/cookbook/search_with_sources.py:6:47"
```

Now that we have created our tool, it’s time to create our LLM call.

## Creating the first call

For this call, we force the LLM to always use its tool which we will later chain.

```python
--8<-- "examples/cookbook/search_with_sources.py:5:6"
--8<-- "examples/cookbook/search_with_sources.py:50:66"
```

We ask the LLM to rewrite the question to make it more suitable for search.

Now that we have the necessary data to answer the user query and their sources, it’s time to extract all that information into a structured format using `response_model`

## Extracting Search Results with Sources

As mentioned earlier, it is important to fact check all answers in case of hallucination, and the first step is to ask the LLM to cite its sources:

```python
--8<-- "examples/cookbook/search_with_sources.py:3:4"
--8<-- "examples/cookbook/search_with_sources.py:69:87"
```

and finally we create our `run` function to execute our chain:

```python
--8<-- "examples/cookbook/search_with_sources.py:90:115"
```

!!! tip "Additional Real-World Applications"

    - **Journalism Assistant**: Have the LLM do some research to quickly pull verifiable sources for blog posts and news articles.
    - **Education**: Find and cite articles to help write academic papers.
    - **Technical Documentation**: Generate code snippets and docs referencing official documentation.

When adapting this recipe, consider:
    - Adding [Tenacity](https://tenacity.readthedocs.io/en/latest/) `retry` for more a consistent extraction.
    - Use an LLM with web search tool to evaluate whether the answer produced is in the source.
    - Experiment with different model providers and version for quality and accuracy of results.
