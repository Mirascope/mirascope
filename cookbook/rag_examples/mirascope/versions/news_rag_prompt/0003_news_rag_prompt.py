import abc
import inspect
import os

import pandas as pd
from config import PINECONE_INDEX, TEXT_COLUMN
from pinecone import Pinecone
from pydantic import ConfigDict
from utils import query_dataframe, query_pinecone

from mirascope import OpenAIChat, Prompt, messages

prev_revision_id = "0002"
revision_id = "0003"


@messages
class NewsRagPrompt(Prompt, abc.ABC):
    """
    SYSTEM:
    You are an expert at:
    1) determining the relevancy of articles to a topic, and
    2) summarizing articles concisely and eloquently.

    When given a topic and a list of possibly relevant texts, you determine for each
    text if it is truly relevant to the topic, and only if so, do you summarize it. You
    format your responses as only a list, where each item is a summary of an article or
    an explanation as to why it is not relevant.

    USER:
    Here are {num_statements} article snippets about this topic: {topic}

    {context}

    Pick only the snippets which are truly relevant to the topic, and summarize them.
    """

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
    __doc__ = inspect.getdoc(NewsRagPrompt)

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
            [f"{i + 1}. {statement}" for (i, statement) in enumerate(statements)]
        )


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
            [f"{i + 1}. {statement}" for (i, statement) in enumerate(statements)]
        )
