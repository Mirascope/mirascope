import abc
import os

import pandas as pd
from config import PINECONE_INDEX, TEXT_COLUMN
from dotenv import load_dotenv
from pinecone import Pinecone
from pydantic import ConfigDict
from utils import query_dataframe, query_pinecone

from mirascope import OpenAIChat, Prompt

load_dotenv()


class NewsRagPrompt(Prompt, abc.ABC):
    """"""

    num_statements: int
    topic: str
    df: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    @abc.abstractmethod
    def context(self) -> str:
        """Finds most similar articles to topic using embeddings."""
        ...


class LocalNewsRagPrompt(NewsRagPrompt):
    """
    USER: Here are {num_statements} article snippets about this topic: {topic}

    {context}

    Pick only the snippets which are truly relevant to the topic, and summarize them.
    """

    @property
    def context(self) -> str:
        """Finds most similar articles in dataframe using embeddings."""

        statements = query_dataframe(
            df=self.df,
            query=self.topic,
            num_results=self.num_statements,
            chat=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
        )
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
        )


class PineconeNewsRagPrompt(NewsRagPrompt):
    """
    USER: Here are {num_statements} article snippets about this topic: {topic}

    {context}

    Pick only the snippets which are truly relevant to the topic, and summarize them.
    """

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
