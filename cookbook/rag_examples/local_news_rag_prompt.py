"""Prompt for local RAG."""
import os

import numpy as np
import pandas as pd
from config import EMBEDDINGS_COLUMN, TEXT_COLUMN
from openai import OpenAI
from pydantic import ConfigDict
from utils import embed_with_openai

from mirascope import Prompt, messages


@messages
class LocalNewsRagPrompt(Prompt):
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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def context(self) -> str:
        """Finds most similar articles in dataframe using embeddings."""

        query_embedding = embed_with_openai(
            self.topic, OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        )[0]
        self.df["similarities"] = self.df[EMBEDDINGS_COLUMN].apply(
            lambda x: np.dot(x, query_embedding)
        )
        most_similar = self.df.sort_values("similarities", ascending=False).iloc[
            : self.num_statements
        ][TEXT_COLUMN]
        statements = most_similar.to_list()
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
        )
