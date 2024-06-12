"""
This example demonstrates how to use Mirascope to store and retrieve relevant 
chat history.
"""
import os
from typing import Literal, cast
from uuid import uuid4

from anthropic.types import MessageParam

from mirascope.anthropic.calls import AnthropicCall
from mirascope.chroma import ChromaSettings, ChromaVectorStore
from mirascope.openai import OpenAIEmbedder
from mirascope.rag import Document, TextChunker

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
os.environ["ANTHROPIC_API_KEY"] = "YOUR_ANTHROPIC_API_KEY"


class LibrarianStore(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "librarian-0001"
    client_settings = ChromaSettings()


store = LibrarianStore()


class Librarian(AnthropicCall):
    prompt_template = """
	SYSTEM: You are the world's greatest librarian.
	MESSAGES: {history}
	USER: {question}
	"""

    question: str

    @property
    def history(self) -> list[MessageParam]:
        retrieval = store.retrieve(self.question, include=["metadatas", "documents"])
        if (
            retrieval.documents is not None
            and len(retrieval.documents) > 0
            and retrieval.metadatas is not None
            and len(retrieval.metadatas) > 0
        ):
            documents = retrieval.documents[0]
            metadatas = retrieval.metadatas[0]
            return [
                {
                    "role": cast(Literal["user", "assistant"], metadata["role"])
                    if metadata
                    else "assistant",
                    "content": documents[i] if documents[i] else "",
                }
                for i, metadata in enumerate(metadatas)
            ]
        return []


librarian = Librarian(question="")
while True:
    librarian.question = input("(User): ")
    if librarian.question == "exit":
        break
    response = librarian.call()

    store.add(
        [
            Document(
                id=str(uuid4()),
                text=librarian.question,
                metadata={"role": "user"},
            ),
            Document(
                id=str(uuid4()),
                text=response.content,
                metadata={"role": "assistant"},
            ),
        ]
    )
    print(f"(Assistant): {response.content}")
