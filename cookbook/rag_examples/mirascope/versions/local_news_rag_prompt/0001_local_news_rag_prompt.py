"""Prompt for local RAG."""
import inspect
import os

from utils import query_dataframe

from mirascope import OpenAIChat

from .news_rag_prompt import NewsRagPrompt

prev_revision_id = "None"
revision_id = "0001"


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
