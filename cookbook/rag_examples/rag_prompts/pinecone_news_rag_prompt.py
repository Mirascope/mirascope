"""Prompt for Pinecone RAG."""
import os

import pandas as pd
from config import PINECONE_INDEX, TEXT_COLUMN
from pinecone import Pinecone
from pydantic import ConfigDict
from utils import query_pinecone

from mirascope import OpenAIChat, Prompt, messages


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
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self._index = pc.Index(PINECONE_INDEX)

    @property
    def context(self) -> str:
        """Finds most similar articles in pinecone using embeddings."""
        indices = query_pinecone(
            index=self._index,
            query=self.topic,
            chat=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
            num_results=self.num_statements,
        )
        statements = self.df.iloc[indices][TEXT_COLUMN].to_list()
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
        )
