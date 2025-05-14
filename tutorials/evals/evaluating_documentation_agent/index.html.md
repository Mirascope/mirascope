# Evaluating Documentation Agent

In this recipe, we will be using taking our [Documentation Agent](../../agents/documentation_agent) example and running evaluations on the LLM call. We will be exploring various different evaluations we can run to ensure quality and expected behavior.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/chaining/">Chaining</a></li>
<li><a href="../../../learn/evals/">Evals</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Check out the Documentation Agent Tutorial</p>
<p>
We will be using our <code>DocumentationAgent</code> for our evaluations. For a detailed explanation regarding this code snippet, refer to the <a href="../../agents/documentation_agent/">Documentation Agent Tutorial</a>.
</p>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[openai]"
# for testing and llama index
!pip install  ipytest pytest llama-index
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Basic Evaluations

We will first test the functionality of our LLM Rerank function to ensure it performs as intended. We have prepared a list of mock documents, each with an assigned semantic score, simulating retrieval from our vector store. The LLM Rerank function will then reorder these documents based on their relevance to the query, rather than relying solely on their semantic scores.



```python
import ipytest
import pytest
from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field

ipytest.autoconfig()

documents = [
    {"id": 0, "text": "Bob eats burgers every day.", "semantic_score": 0.8},
    {"id": 1, "text": "Bob's favorite food is not pizza.", "semantic_score": 0.9},
    {"id": 2, "text": "I ate at In-N-Out with Bob yesterday", "semantic_score": 0.5},
    {"id": 3, "text": "Bob said his favorite food is burgers", "semantic_score": 0.9},
]


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


@pytest.mark.parametrize(
    "query,documents,top_n_ids",
    (("What is Bob's favorite food", documents, {3, 0}),),
)
def test_llm_query_rerank(query: str, documents: list[dict], top_n_ids: set[int]):
    """Tests that the LLM query rerank ranks more relevant documents higher."""
    response = llm_query_rerank(documents, query)
    results = sorted(response, key=lambda x: x.score or 0, reverse=True)
    assert all(result.score > 5 for result in results)
    assert top_n_ids.issuperset({result.id for result in results[: len(top_n_ids)]})


ipytest.run()
```


Our tests:

* Ensures that all returned documents have a relevancy score above 5 out of 10, indicating a minimum threshold of relevance.
* Checks that the top-ranked documents (as many as specified in `top_n_ids`) are within the set of expected documents, allowing for some flexibility in the exact ordering.

The test accommodates the non-deterministic nature of LLM-based reranking. While we can't expect identical results in every run, especially when multiple documents are similarly relevant, we can at least verify that the output falls within our boundaries.

## Evaluating Code Snippets and General Q&A

The example documents we are using for our `DocumentationAgent` are the Mirascope docs. Since Mirascope is a python library, users are likely to ask about both code implementation and conceptual understanding. Therefore, our evaluation process needs to address these two distinct scenarios.

### Evaluating Code Snippet

To ensure the accuracy and functionality of the LLM-generated code, we implement a two-step verification process:

* Syntax Validation: We create a general Python code tester to verify the syntactic correctness of the generated code.
* Import Verification: Since syntax validation alone is insufficient, we incorporate an additional check for proper imports. This step confirms all modules and dependencies are valid and no "magic" imports exist.



```python
import ast
import importlib.util


def check_syntax(code_string: str) -> bool:
    try:
        compile(code_string, "<string>", "exec")
        return True
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False


def is_importable(code_string: str) -> bool:
    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom):
            module_name = (
                node.module if isinstance(node, ast.ImportFrom) else node.names[0].name
            )
            if not check_module(module_name):
                return False

            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if not check_attribute(module_name, alias.name):
                        return False

    return True


def check_module(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, AttributeError, ValueError):
        return False


def check_attribute(module_name, attribute):
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        module = importlib.util.module_from_spec(spec)
        if spec.loader:
            spec.loader.exec_module(module)
        return hasattr(module, attribute)
    except (ImportError, AttributeError):
        return False


@pytest.mark.parametrize(
    "import_str,expected",
    [
        ("from mirascope.core import openai", True),
        ("import math", True),
        ("from datetime import datetime", True),
        ("import non_existent_module", False),
        ("from os import path, nonexistent_function", False),
        ("from sys import exit, nonexistent_variable", False),
        ("from openai import OpenAI", True),
        ("from mirascope.core import openai", True),
    ],
)
def test_is_importable(import_str: str, expected: bool):
    assert is_importable(import_str) == expected


@pytest.mark.parametrize(
    "syntax,expected",
    [("print('Hello, World!')", True), ("print('Hello, World!'", False)],
)
def test_check_syntax(syntax: str, expected: bool):
    assert check_syntax(syntax) == expected


ipytest.run()
```

Now that we have our `check_syntax` and `is_importable` tests working, we can test our LLM output:



```python
from typing import Literal, cast

from llama_index.core import (
    QueryBundle,
    load_index_from_storage,
)
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.storage import StorageContext

storage_context = StorageContext.from_defaults(persist_dir="storage")
loaded_index = load_index_from_storage(storage_context)


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
```


```python
@pytest.mark.parametrize(
    "query,expected",
    [
        ("How do I make a basic OpenAI call using Mirascope?", None),
        ("What is Mirascope?", "a toolkit for building AI-powered applications"),
    ],
)
def test_documentation_agent_code(query: str, expected: str):
    documentation_agent = DocumentationAgent()
    response = documentation_agent._call(query)
    if response.classification == "code":
        assert check_syntax(response.content) and is_importable(response.content)
    else:
        assert expected in response.content


ipytest.run()
```


### Evaluating General Q&A

For non-code responses generated by the LLM, our primary goal is to verify that the LLM is sourcing its responses directly from the Mirascope documentation rather than relying on its broader knowledge base. Here we require that the LLM's response contains a sentence verbatim.



```python
@pytest.mark.parametrize(
    "query,expected",
    [
        ("What is Mirascope?", "a toolkit for building AI-powered applications"),
    ],
)
def test_documentation_agent_general(query: str, expected: str):
    documentation_agent = DocumentationAgent()
    response = documentation_agent._call(query)
    if response.classification == "general":
        assert expected in response.content


ipytest.run()
```


When adapting this recipe to your specific use-case, consider the following:

* Update the Few-Shot examples to match your documents.
* Experiment with other providers for LLM Reranking or use multiple LLM Rerankers and average out the scores.
* Add history to the `DocumentationAgent` and have the LLM generate the query for `get_documents` for a more relevant semantic search.

