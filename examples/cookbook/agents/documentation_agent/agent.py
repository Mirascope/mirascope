from typing import cast

from llama_index.core import (
    QueryBundle,
    load_index_from_storage,
)
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.storage import StorageContext
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template

storage_context = StorageContext.from_defaults(persist_dir="storage")
loaded_index = load_index_from_storage(storage_context)
query_engine = loaded_index.as_query_engine()


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

    A question
    A list of documents, each with an ID and content summary

    Task

    Analyze each document for its relevance to the question.
    Assign a relevance score from 1-10 for each document.
    Provide a reason for each score.

    Scoring Guidelines

    Consider both direct and indirect relevance to the question.
    Prioritize positive, affirmative information over negative statements.
    Assess the informativeness of the content, not just keyword matches.
    Consider the potential for a document to contribute to a complete answer.

    Important Notes

    Exclude documents with no relevance to the question.
    Be cautious with negative statements - they may be relevant but are often less informative than positive ones.
    Consider how multiple documents might work together to answer the question.

    Documents:
    {documents}

    USER: 
    query:
    {query}
    """
)
def llm_query_rerank(documents: list[dict], query: str): ...


def get_documents(query: str) -> list[str]:
    """The get_documents tool that retrieves Mirascope documentation based on the
    relevance of the query"""
    print("Query:", query)
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
                "semantic_score": node.score,
            }
            for id, node in enumerate(retrieved_nodes[idx : idx + choice_batch_size])
        ]
        results += llm_query_rerank(nodes_batch, query)
    results = sorted(results, key=lambda x: x.score or 0, reverse=True)[:top_n]

    return [result.document for result in results]


class MirascopeBot(BaseModel):
    @openai.call(
        "gpt-4o-mini",
    )
    @prompt_template(
        """
        SYSTEM:
        You are an AI Assistant that is an expert at answering questions about Mirascope.
        Here is the relevant documentation to answer the question.

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
    MirascopeBot().run()
