import pytest

from examples.cookbook.agents.documentation_agent.agent import llm_query_rerank
from examples.cookbook.agents.documentation_agent.documents import (
    retrieved_dummy_docs,
    retrieved_mirascope_docs,
    retrieved_mirascope_ollama_docs,
    retrieved_mirascope_openai_docs,
)

batch_query_rerank_golden_dataset = [
    ("What is Bob's favorite food", retrieved_dummy_docs, {3, 0}),
    (
        "How do I make a basic OpenAI call using Mirascope?",
        retrieved_mirascope_openai_docs,
        {4, 1},
    ),
    (
        "Can you write me code for making a Mirascope call?",
        retrieved_mirascope_docs,
        {0, 1},
    ),
    (
        "How do I use an Ollama Custom Client instead of OpenAI client?",
        retrieved_mirascope_ollama_docs,
        {0, 9},
    ),
]


@pytest.mark.parametrize(
    "query,documents,top_n_ids",
    batch_query_rerank_golden_dataset,
)
def test_llm_query_rerank(query: str, documents: list[dict], top_n_ids: set[int]):
    """Tests that the LLM query rerank ranks more relevant documents higher."""
    response = llm_query_rerank(documents, query)
    results = sorted(response, key=lambda x: x.score or 0, reverse=True)
    assert all(result.score > 5 for result in results)
    assert {result.id for result in results[: len(top_n_ids)]} == top_n_ids
