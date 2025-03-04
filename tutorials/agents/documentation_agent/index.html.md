# Documentation Agent

In this recipe, we will be building a `DocumentationAgent` that has access to some documentation. We will be using Mirascope documentation in this example, but this should work on all types of documents. This is implemented using `OpenAI`, see [Local Chat with Codebase](../../agents/local_chat_with_codebase) for the Llama3.1 implementation.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/chaining/">Chaining</a></li>
<li><a href="../../../learn/response_models/">Response Model</a></li>
<li><a href="../../../learn/json_mode/">JSON Mode</a></li>
<li><a href="../../../learn/agents/">Agents</a></li>
</ul>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[openai]"
# LLamaIndex for embedding and retrieving embeddings from a vectorstore
!pip install llama-index
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Store Embeddings

The first step is to grab our docs and embed them into a vectorstore. In this recipe, we will be storing our vectorstore locally, but using Pinecone or other cloud vectorstore providers will also work. We adjusted the `chunk_size` and `chunk_overlap` to get the best results for Mirascope docs, but these values may not necessarily be good for other types of documents.


```python
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding

documents = SimpleDirectoryReader("../../../docs/learn").load_data()
vector_store = SimpleVectorStore()
storage_context = StorageContext.from_defaults(vector_store=vector_store)

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=512, chunk_overlap=128),
        TitleExtractor(),
        OpenAIEmbedding(),
    ],
    vector_store=vector_store,
)

nodes = pipeline.run(documents=documents)
index = VectorStoreIndex(
    nodes,
    storage_context=storage_context,
)

index.storage_context.persist()
```


## Load Embeddings

After we saved our embeddings, we can use the below code to retrieve it and load in memory:




```python
from llama_index.core import (
    load_index_from_storage,
)

storage_context = StorageContext.from_defaults(persist_dir="storage")
loaded_index = load_index_from_storage(storage_context)
query_engine = loaded_index.as_query_engine()
```


## LLM Reranker

Vectorstore retrieval relies on semantic similarity search but lacks contextual understanding. By employing an LLM to rerank results based on relevance, we can achieve more accurate and robust answers.



```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


class Relevance(BaseModel):
    id: int = Field(..., description="The document ID")
    score: int = Field(..., description="The relevance score (1-10)")
    document: str = Field(..., description="The document text")
    reason: str = Field(..., description="A brief explanation for the assigned score")


@openai.call(
    "gpt-4o-mini",
    response_model=list[Relevance],
    json_mode=True,
)
@prompt_template(
    """
    SYSTEM:
    Document Relevance Assessment
    Given a list of documents and a question, determine the relevance of each document to answering the question.

    Input
        - A question
        - A list of documents, each with an ID and content summary

    Task
        - Analyze each document for its relevance to the question.
        - Assign a relevance score from 1-10 for each document.
        - Provide a reason for each score.

    Scoring Guidelines
        - Consider both direct and indirect relevance to the question.
        - Prioritize positive, affirmative information over negative statements.
        - Assess the informativeness of the content, not just keyword matches.
        - Consider the potential for a document to contribute to a complete answer.

    Important Notes
        - Exclude documents with no relevance less than 5 to the question.
        - Be cautious with negative statements - they may be relevant but are often less informative than positive ones.
        - Consider how multiple documents might work together to answer the question.
        - Use the document title and content summary to make your assessment.

    Documents:
    {documents}

    USER: 
    {query}
    """
)
def llm_query_rerank(documents: list[dict], query: str): ...
```


We get back a list of `Relevance`s which we will be using for our `get_documents` function.

## Getting our documents

With our LLM Reranker configured, we can now retrieve documents for our query. The process involves three steps:

1. Fetch the top 10 (`top_k`) semantic search results from our vectorstore.
2. Process these results through our LLM Reranker in batches of 5 (`choice_batch_size`).
3. Return the top 2 (`top_n`) most relevant documents.



```python
from typing import cast

from llama_index.core import QueryBundle
from llama_index.core.indices.vector_store import VectorIndexRetriever


def get_documents(query: str) -> list[str]:
    """The get_documents tool that retrieves Mirascope documentation based on the
    relevance of the query"""
    query_bundle = QueryBundle(query)
    retriever = VectorIndexRetriever(
        index=cast(VectorStoreIndex, loaded_index),
        similarity_top_k=10,
    )
    retrieved_nodes = retriever.retrieve(query_bundle)
    choice_batch_size = 5
    top_n = 2
    results: list[Relevance] = []
    for idx in range(0, len(retrieved_nodes), choice_batch_size):
        nodes_batch = [
            {
                "id": idx + id,
                "text": node.node.get_text(),  # pyright: ignore[reportAttributeAccessIssue]
                "document_title": node.metadata["document_title"],
                "semantic_score": node.score,
            }
            for id, node in enumerate(retrieved_nodes[idx : idx + choice_batch_size])
        ]
        results += llm_query_rerank(nodes_batch, query)
    results = sorted(results, key=lambda x: x.score or 0, reverse=True)[:top_n]

    return [result.document for result in results]
```


Now that we can retrieve relevant documents for our user query, we can create our Agent.

## Creating `DocumentationAgent`

Our `get_documents` method retrieves relevant documents, which we pass to the `context` for our call. The LLM then categorizes the question as either `code` or `general`. Based on this classification:

- For code questions, the LLM generates an executable code snippet.
- For general questions, the LLM summarizes the content of the retrieved documents.



```python
from typing import Literal


class Response(BaseModel):
    classification: Literal["code", "general"] = Field(
        ..., description="The classification of the question"
    )
    content: str = Field(..., description="The response content")


class DocumentationAgent(BaseModel):
    @openai.call("gpt-4o-mini", response_model=Response, json_mode=True)
    @prompt_template(
        """
        SYSTEM:
        You are an AI Assistant that is an expert at answering questions about Mirascope.
        Here is the relevant documentation to answer the question.

        First classify the question into one of two types:
            - General Information: Questions about the system or its components.
            - Code Examples: Questions that require code snippets or examples.

        For General Information, provide a summary of the relevant documents if the question is too broad ask for more details. 
        If the context does not answer the question, say that the information is not available or you could not find it.

        For Code Examples, output ONLY code without any markdown, with comments if necessary.
        If the context does not answer the question, say that the information is not available.

        Examples:
            Question: "What is Mirascope?"
            Answer:
            A toolkit for building AI-powered applications with Large Language Models (LLMs).
            Explanation: This is a General Information question, so a summary is provided.

            Question: "How do I make a basic OpenAI call using Mirascope?"
            Answer:
            from mirascope.core import openai, prompt_template


            @openai.call("gpt-4o-mini")
            def recommend_book(genre: str) -> str:
                return f'Recommend a {genre} book'

            response = recommend_book("fantasy")
            print(response.content)
            Explanation: This is a Code Examples question, so only a code snippet is provided.

        Context:
        {context:list}

        USER:
        {question}
        """
    )
    def _call(self, question: str) -> openai.OpenAIDynamicConfig:
        documents = get_documents(question)
        return {"computed_fields": {"context": documents}}

    def _step(self, question: str):
        answer = self._call(question)
        print("(Assistant):", answer.content)

    def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            self._step(question)


if __name__ == "__main__":
    DocumentationAgent().run()
    # Output:
    """
    (User): How do I make an LLM call using Mirascope?
    (Assistant): from mirascope.core import openai
    
    @openai.call('gpt-4o-mini')
    def recommend_book(genre: str) -> str:
        return f'Recommend a {genre} book'
    
    response = recommend_book('fantasy')
    print(response.content)
    """
```


<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Improved Chat Application</b>: Maintain the most current documentation by storing it in a vector database or using a tool to retrieve up-to-date information in your chat application</li>
<li><b>GitHub Issues Bot</b>: Add a GitHub bot that scans through issues and answers questions for users.</li>
<li><b>Interactive Internal Knowledge Base</b>: Index company handbooks and internal documentation to enable instant, AI-powered Q&A access.</li>
</ul>
</div>


When adapting this recipe, consider:

- Experiment with different model providers and version for quality.
- Add evaluations to the agent, and feed the errors back to the LLM for refinement.
- Add history to the Agent so that the LLM can generate context-aware queries to retrieve more semantically similar embeddings.

