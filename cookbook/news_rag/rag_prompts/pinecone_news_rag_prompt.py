"""Prompt for Pinecone RAG."""
import pandas as pd
from openai import OpenAI
from pinecone import Pinecone
from pydantic import ConfigDict
from rag_config import PINECONE_INDEX, PINECONE_NAMESPACE, TEXT_COLUMN, Settings
from rag_utils import embed_with_openai

from mirascope import Prompt, messages

settings = Settings()


@messages
class PineconeNewsRagPrompt(Prompt):
    """
    SYSTEM:
    You are an expert at:
    1) determining the relevancy of articles to a topic, and
    2) summarizing articles concisely and eloquently.

    When given a topic and a list of possibly relevant texts, you format your responses
    as a single list, where you summarize the articles relevant to the topic or explain
    why the article is not relevant to the topic.

    USER:
    Here are {num_statements} article snippets about this topic: {topic}

    {context}

    Pick only the snippets which are truly relevant to the topic, and summarize them.
    """

    num_statements: int
    topic: str
    df: pd.DataFrame

    _index: Pinecone.Index

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index = pc.Index(PINECONE_INDEX)

    @property
    def context(self) -> str:
        """Finds most similar articles in pinecone using embeddings."""
        query_embedding = embed_with_openai(
            self.topic, OpenAI(api_key=settings.openai_api_key)
        )[0]
        query_response = self._index.query(
            namespace=PINECONE_NAMESPACE,
            vector=query_embedding,
            top_k=self.num_statements,
        )
        indices = [int(article["id"]) for article in query_response["matches"]]
        statements = self.df.iloc[indices][TEXT_COLUMN].to_list()
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
        )
