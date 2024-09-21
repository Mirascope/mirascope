# Documentation Agent

In this recipe, we will be building a `DocumentationAgent` that has access to some documentation. We will be using Mirascope documentation in this example, but this should work on all types of documents. This is implemented using `OpenAI`, see [Local Chat with Codebase](./local_chat_with_codebase.md) for the Llama3.1 implementation.

## Setup

We use LlamaIndex for embedding and retrieving our embeddings from a vectorstore.

```bash
pip install llama-index
```

??? tip "Mirascope Concepts Used"
    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Chaining](../../learn/chaining.md)
    - [Response Model](../../learn/response_models.md)
    - [JSON Mode](../../learn/json_mode.md)
    - [Agents](../../learn/agents.md)

## Store Embeddings

The first step is to grab our docs and embed them into a vectorstore. In this recipe, we will be storing our vectorstore locally, but using Pinecone or other cloud vectorstore providers will also work. We adjusted the `chunk_size` and `chunk_overlap` to get the best results for Mirascope docs, but these values may not necessarily be good for other types of documents.

```python
--8<-- "examples/cookbook/agents/documentation_agent/setup.py"
```

## Load Embeddings

After we saved our embeddings, we can use the below code to retrieve it and load in memory:

```python
--8<-- "examples/cookbook/agents/documentation_agent/agent.py:3:9"
--8<-- "examples/cookbook/agents/documentation_agent/agent.py:13:16"
```

## LLM Reranker

Vectorstore retrieval relies on semantic similarity search but lacks contextual understanding. By employing an LLM to rerank results based on relevance, we can achieve more accurate and robust answers.

```python
--8<-- "examples/cookbook/agents/documentation_agent/agent.py:10:13"
--8<-- "examples/cookbook/agents/documentation_agent/agent.py:17:65"
```

We get back a list of `Relevance`s which we will be using for our `get_documents` function.

## Getting our documents

With our LLM Reranker configured, we can now retrieve documents for our query. The process involves three steps:

1. Fetch the top 10 (`top_k`) semantic search results from our vectorstore.
2. Process these results through our LLM Reranker in batches of 5 (`choice_batch_size`).
3. Return the top 2 (`top_n`) most relevant documents.

```python
--8<-- "examples/cookbook/agents/documentation_agent/agent.py:68:93"
```

Now that we can retrieve relevant documents for our user query, we can create our Agent.

## Creating `DocumentationAgent`

Our `get_documents` method retrieves relevant documents, which we pass to the `context` for our call. The LLM then categorizes the question as either `code` or `general`. Based on this classification:

- For code questions, the LLM generates an executable code snippet.
- For general questions, the LLM summarizes the content of the retrieved documents.

```python
--8<-- "examples/cookbook/agents/documentation_agent/agent.py:96:178"
```

!!! tip "Additional Real-World Applications"
    - **Improved Chat Application**: Maintain the most current documentation by storing it in a vector database or using a tool to retrieve up-to-date information in your chat application
    - **GitHub Issues Bot**: Add a GitHub bot that scans through issues and answers questions for users.
    - **Interactive Internal Knowledge Base**: Index company handbooks and internal documentation to enable instant, AI-powered Q&A access.

When adapting this recipe, consider:

- Experiment with different model providers and version for quality.
- Add evaluations to the agent, and feed the errors back to the LLM for refinement.
- Add history to the Agent so that the LLM can generate context-aware queries to retrieve more semantically similar embeddings.
