"""Prompt for Pinecone RAG."""
import inspect
import os

from config import PINECONE_INDEX, TEXT_COLUMN
from pinecone import Pinecone
from pydantic import ConfigDict
from utils import query_pinecone

from mirascope import OpenAIChat
from rag_prompts.news_rag_prompt import NewsRagPrompt


class PineconeNewsRagPrompt(NewsRagPrompt):
    __doc__ = inspect.getdoc(NewsRagPrompt)

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
