import os
import uuid
from typing import Callable

from dotenv import load_dotenv

from mirascope.base.chunkers import Document
from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.openai import OpenAICall, OpenAIEmbedder

load_dotenv()


current_dir = os.path.dirname(os.path.abspath(__file__))


def chunk_fn(
    text: str = "", chunk_size: int = 1000, chunk_overlap: int = 200
) -> list[Document]:
    """This is a docstring"""
    chunks: list[Document] = []
    start: int = 0
    while start < len(text):
        end: int = min(start + chunk_size, len(text))
        chunks.append(Document(text=text[start:end], id=str(uuid.uuid4())))
        start += chunk_size - chunk_overlap
    return chunks


class SOTU(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker: Callable = chunk_fn
    # chunker: BaseChunker = BaseChunker()
    index_name = "sotu"


class SotuCall(OpenAICall):
    prompt_template = """
    SYSTEM: Answer the question based on the context.
    {context}
    USER: {question}
    """

    question: str

    @property
    def context(self):
        with open(f"{current_dir}/state_of_the_union.txt") as file:
            # LOAD DATA
            data = file.read()

            store = SOTU()
            store.add_documents(data)
            documents = store.get_documents(self.question)
            documents = "\n".join([doc for sublist in documents for doc in sublist])
            return documents


query = "What did the president say about jobs"
sotu = SotuCall(question=query).call()
print(sotu.content)
