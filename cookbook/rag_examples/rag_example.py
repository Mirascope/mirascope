"""A script using RAG to summarize relevant articles from a large database in 2 ways.

News articles from 2004 are embedded so they may be queried (in two ways) according to a
topic of choice. In the first way we manually calculate similarity between query and
embeddings. In the second, we set up Pinecone and efficiently use its search to find the
most relevant articles. In both cases, we use the Mirascope library to handle the logic
so as to streamline prompt creation.
"""
import os

import pandas as pd
from config import FILENAME, MAX_TOKENS, URL
from rag_prompts.news_rag_prompt import LocalNewsRagPrompt, PineconeNewsRagPrompt
from setup_pinecone import setup_pinecone
from utils import embed_df_with_openai, load_data

from mirascope import OpenAIChat

chat = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))


# Make reruns efficient by preprocessing data before saving to csv
if not os.path.exists(FILENAME):
    df = load_data(url=URL, max_tokens=MAX_TOKENS)
    df = embed_df_with_openai(df=df, chat=chat)
    df.to_pickle(FILENAME)

    # Comment this line out if you don't have your data saved locally but somehow have
    # it already on Pinecone since it takes time and server credits.
    setup_pinecone(df=df)
else:
    df = pd.read_pickle(FILENAME)


def summarize_news_local_embeddings(query: str, num_articles: int) -> str:
    """Summarizes 2004 news about retrieved context that is relevant to query.

    Locally calculates similarity between query and articles embeddings within pandas
    dataframe using dot product.

    Args:
        query: The query to compare against for similarity.
        num_articles: The number of articles to return.

    Returns:
        A summary of the most relevant articles to the query.
    """
    completion = chat.create(
        LocalNewsRagPrompt(num_statements=num_articles, topic=query, df=df)
    )
    return str(completion)


def summarize_news_pinecone_embeddings(query: str, num_articles: int) -> str:
    """Summarizes 2004 news about retrieved context that is relevant to query.

    Uses Pinecone to efficiently calculate similarity between query and article
    embeddings.

    Args:
        query: The query to compare against for similarity.
        num_articles: The number of articles to return.

    Returns:
        A summary of the most relevant articles to the query.
    """
    completion = chat.create(
        PineconeNewsRagPrompt(num_statements=num_articles, topic=query, df=df)
    )
    return str(completion)


topics = [
    "soccer teams/players going through trouble",
    "environmental factors affecting economy",
    "celebrity or politician scandals",
]
for topic in topics:
    # Run Locally
    # print(summarize_news_local_embeddings(topic, 3)

    # Run with Pinecone
    print(summarize_news_pinecone_embeddings(topic, 3))
    print("\n")
