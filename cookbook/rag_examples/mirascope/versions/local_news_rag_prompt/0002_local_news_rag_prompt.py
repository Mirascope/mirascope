"""Prompt for local RAG."""
import os

import pandas as pd
from pydantic import ConfigDict
from utils import query_dataframe

from mirascope import OpenAIChat, Prompt, messages

prev_revision_id = "0001"
revision_id = "0002"


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
        statements = query_dataframe(
            df=self.df,
            query=self.topic,
            num_results=self.num_statements,
            chat=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
        )
        return "\n".join(
            [f"{i + 1}. {statement}" for (i, statement) in enumerate(statements)]
        )
