"""Utility functions for the RAG examples."""
from typing import Union

import pandas as pd
import tiktoken
from openai import OpenAI
from rag_config import (
    EMBEDDINGS_COLUMN,
    EMBEDDINGS_MODEL,
    MODEL,
    TEXT_COLUMN,
)


def embed_with_openai(text: Union[str, list[str]], client: OpenAI) -> list[list[float]]:
    """Embeds a string using OpenAI's embedding model.

    Args:
        text: A `str` or list of `str` to embed.
        client: The `OpenAI` instance used for embedding.

    Returns:
        The embeddings of the text.
    """
    if isinstance(text, str):
        text = [text]
    embeddings_response = client.embeddings.create(model=EMBEDDINGS_MODEL, input=text)
    return [datum.embedding for datum in embeddings_response.data]


def embed_df_with_openai(
    df: pd.DataFrame,
    client: OpenAI,
) -> pd.DataFrame:
    """Embeds a Pandas Series of texts in batches using minimal OpenAI calls.

    Note that this functions assumes all texts are less than 8192 tokens long.

    Args:
        texts: The texts to embed.
        client: The `OpenAI` instance used for embedding.

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
            embeddings += embed_with_openai(batch, client)
            batch = [text]
            batch_token_count = len(encoder.encode(text))
        else:
            batch.append(text)
            batch_token_count += len(encoder.encode(text))

    if batch:
        embeddings += embed_with_openai(batch, client)

    df[EMBEDDINGS_COLUMN] = embeddings
    return df


def load_data(url: str, max_tokens: int) -> pd.DataFrame:
    """Loads data from a url after splitting larger texts into smaller chunks.

    Args:
        url: the url to load the data from.
        max_tokens: the maximum number of tokens per chunk.

    Returns:
        The dataframe with the data from the url.
    """
    df = pd.read_csv(url)
    split_articles = []
    encoder = tiktoken.encoding_for_model(MODEL)
    for i, row in df.iterrows():
        text = row[TEXT_COLUMN]
        tokens = encoder.encode(text)
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
