# Local Chat with Codebase

In this recipe, we will be using all Open Source Software to build a local ChatBot that has access to some documentation. We will be using Mirascope documentation in this example, but this should work on all types of documents. Also note that we will be using a smaller Llama 3.1 8B so the results will not be as impressive as larger models. Later, we will take a look at how OpenAI's GPT compares with Llama.

## Setup

```bash
pip install llama-index, llama-index-llms-ollama, llama-index-embeddings-huggingface
```

[Ollama](https://github.com/ollama/ollama)

For this setup, we use Ollama but vLLM will also work.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Agents](../../learn/agents.md)

## Configuration

```python
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:3:8"
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:19:21"
```

We will be using LlamaIndex for RAG, and setting up the proper models we will be using for Re-ranking and the Embedding model.

## Store Embeddings

The first step is to grab our docs and embed them into a vectorstore. In this recipe, we will be storing our vectorstore locally, but using Pinecone or other cloud vectorstore providers will also work.

```python
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:9:14"
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:24:28"
```

## Load Embeddings

After we saved our embeddings, we can use the below code to retrieve it and load in memory:

```python
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:31:33"
```

## Code

We need to update LlamaIndex `default_parse_choice_select_answer_fn` for Llama 3.1. You may need to update the `custom_parse_choice_select_answer_fn` depending on which model you are using. Adding re-ranking is extremely important to get better quality retrievals so the LLM can make better context-aware answers.

We will be creating an Agent that will read Mirascope documentation called MiraBot which will answer questions regarding Mirascope docs.

~~~python
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:1:2"
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:18:19"
--8<-- "examples/cookbook/agents/local_chat_with_codebase.py:35:148"
~~~

!!! note "Check out OpenAI Implementation"
    While we demonstrated an open source version of chatting with our codebase, there are several improvements we can make to get better results. Refer to [Documentation Agent Cookbook](./documentation_agent.md) for a detailed walkthrough on the improvements made.



!!! tip "Additional Real-World Applications"

    - **Improved Chat Application**: Maintain the most current documentation by storing it in a vector database or using a tool to retrieve up-to-date information in your chat application
    - **Code Autocomplete**: Integrate the vector database with the LLM to generate accurate, context-aware code suggestions."
    - **Interactive Internal Knowledge Base**: Index company handbooks and internal documentation to enable instant, AI-powered Q&A access.

When adapting this recipe, consider:

- Experiment with different model providers and version for quality.
- Use a different Reranking prompt as that impacts the quality of retrieval
- Implement a feedback loop so the LLM hallucinates less frequently.
