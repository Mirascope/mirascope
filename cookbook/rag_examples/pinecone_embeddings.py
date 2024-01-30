"""A script using RAG and Pinecone to summarize relevant articles from a large database.

First we load in a dataset of news articles from 2004 and embed them. Then we use
Pinecone to efficiently find the articles with most relevance to a query, then use said
articles in a prompt to get the summary.
"""
import os

import pandas as pd
from config import FILENAME, URL
from prompts.news_rag_prompt import LocalNewsRagPrompt, PineconeNewsRagPrompt
from setup_pinecone import setup_pinecone
from utils import embed_df_with_openai, load_data

from mirascope import OpenAIChat

chat = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))


# Make reruns efficient by preprocessing data before saving to csv
if not os.path.exists(FILENAME):
    df = load_data(url=URL)
    df = embed_df_with_openai(df=df, chat=chat)
    df.to_pickle(FILENAME)
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
    # print(summarize_news_local_embeddings(topic, 3)
    print(summarize_news_pinecone_embeddings(topic, 3))
    print("\n")
