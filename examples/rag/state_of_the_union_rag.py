import os

from dotenv import load_dotenv

from mirascope.base import BaseChunker
from mirascope.base.types import BaseChunkerParams
from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.openai import OpenAICall, OpenAIEmbedder

load_dotenv()


current_dir = os.path.dirname(os.path.abspath(__file__))


class Chunker(BaseChunker):
    chunker_params = BaseChunkerParams(chunk_size=1000, chunk_overlap=200)


class SOTU(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = Chunker()
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
