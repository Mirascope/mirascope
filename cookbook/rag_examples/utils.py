"""Utility functions for the RAG examples."""
from typing import Union

import numpy as np
import pandas as pd
import tiktoken
from config import (
    EMBEDDINGS_COLUMN,
    EMBEDDINGS_MODEL,
    MODEL,
    PINECONE_NAMESPACE,
    TEXT_COLUMN,
)
from pinecone import Pinecone

from mirascope import OpenAIChat


def embed_with_openai(
    text: Union[str, list[str]], chat: OpenAIChat
) -> list[list[float]]:
    """Embeds a string using OpenAI's text-embedding-ada-002 model."""
    if isinstance(text, str):
        text = [text]
    embeddings_response = chat.client.embeddings.create(
        model=EMBEDDINGS_MODEL, input=text
    )
    return [datum.embedding for datum in embeddings_response.data]


def embed_df_with_openai(
    df: pd.DataFrame,
    chat: OpenAIChat,
) -> pd.DataFrame:
    """Embeds a Pandas Series of texts in bathces using minimal OpenAI calls.

    Note that this functions assumes all texts are less than 8192 tokens long.

    Args:
        texts: The texts to embed.
        chat: The `OpenAIChat` instance used for embedding.

    Returns:
        The dataframe with the embeddings column added.
    """
    encoder = tiktoken.encoding_for_model(MODEL)
    max_tokens = 8191

    embeddings: list[list[float]] = []
    batch: list[str] = []
    batch_token_count = 0
    for i, text in enumerate(df[TEXT_COLUMN]):
        if batch_token_count + len(encoder.encode(text)) > max_tokens:
            embeddings += embed_with_openai(batch, chat)
            batch = [text]
            batch_token_count = len(encoder.encode(text))
        else:
            batch.append(text)
            batch_token_count += len(encoder.encode(text))

    if batch:
        embeddings += embed_with_openai(batch, chat)

    df[EMBEDDINGS_COLUMN] = embeddings
    return df


def query_dataframe(
    df: pd.DataFrame,
    query: str,
    num_results: int,
    chat: OpenAIChat,
) -> list[str]:
    """Searches a dataframe with embeddings for the most similar texts to a query.

    Args:
        df: The dataframe to query.
        query: The query to compare against for similarity.
        results: The number of results to return.
        chat: The `OpenAIChat` instance used for embedding.

    Returns:
        The most similar texts to the query.
    """
    query_embedding = embed_with_openai(query, chat)[0]
    df["similarities"] = df[EMBEDDINGS_COLUMN].apply(
        lambda x: np.dot(x, query_embedding)
    )
    most_similar = df.sort_values("similarities", ascending=False).iloc[:num_results][
        TEXT_COLUMN
    ]

    return most_similar.to_list()


def query_pinecone(
    index: Pinecone.Index,
    query: str,
    chat: OpenAIChat,
    num_results: int,
) -> list[int]:
    """Searches a Pinecone index for the most similar texts to a query.

    Args:
        index: The Pinecone index to query.
        query: The query to compare against for similarity.
        results: The number of results to return.
        chat: The `OpenAIChat` instance used for embedding.

    Returns:
        The most similar texts to the query.
    """
    query_embedding = embed_with_openai(query, chat)[0]
    query_response = index.query(
        namespace=PINECONE_NAMESPACE, vector=query_embedding, top_k=num_results
    )
    return [int(article["id"]) for article in query_response["matches"]]


def load_data(url: str) -> pd.DataFrame:
    """Loads data from a url, and splits larger texts into smaller chunks."""
    df = pd.read_csv(url)
    split_articles = []
    encoder = tiktoken.encoding_for_model(MODEL)
    for i, row in df.iterrows():
        text = row[TEXT_COLUMN]
        tokens = encoder.encode(text)
        max_tokens = 1000
        if len(tokens) > max_tokens:
            split_articles += split_text(text, tokens, max_tokens)
            df.drop(i, inplace=True)

    # Long texts which were dropped from the dataframe are now readded.
    df = pd.concat(
        [df, pd.DataFrame(split_articles, columns=[TEXT_COLUMN])], ignore_index=True
    )

    return df


def split_text(text: str, tokens: list[int], max_tokens: int) -> list[str]:
    """Roughly splits a text into chunks according to max_tokens.

    Text is split into equal word counts, with number of splits determined by how many
    times `max_tokens` goes into the total number of tokens (including partially). Note
    that tokens and characters do not have an exact correspondence, so in certain edge
    cases a chunk may be slightly larger than max_tokens.

    Args:
        text: The text to split.
        tokens: How many tokens `text` is.
        max_tokens: The (rough) number of maximum tokens per chunk.

    Returns:
        A list of the split texts.
    """
    words = text.split()
    num_splits = len(tokens) // max_tokens + 1
    split_texts = []
    for i in range(num_splits):
        start = i * len(words) // num_splits
        end = (i + 1) * len(words) // num_splits
        split_texts.append(" ".join(words[start:end]))

    return split_texts
