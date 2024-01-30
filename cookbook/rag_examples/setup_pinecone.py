"""Script to upload a dataset to Pinecone"""
import os

import pandas as pd
from config import EMBEDDINGS_COLUMN, PINECONE_INDEX, PINECONE_NAMESPACE
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()


def setup_pinecone(df: pd.DataFrame) -> None:
    """Sets up a Pincone Index and upserts embeddings from dataframe.

    Each upserted embedding has ID set as index from original dataframe to help keep
    track of the affiliated text later on. Vectors are upserted in batches of 300
    (determined by trial and error) so as not to overload Pinecone.

    Args:
        df: The dataframe which contains embeddings to upsert.
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    existing_indexes = pc.list_indexes().names()
    if PINECONE_INDEX not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-west-2",
            ),
        )
    index = pc.Index(PINECONE_INDEX)

    batch_size = 300
    for start in range(0, len(df), batch_size):
        end = min(start + batch_size, len(df))
        batch = df[start:end]
        vectors = []
        for i, row in batch.iterrows():
            vectors.append({"id": str(i), "values": row[EMBEDDINGS_COLUMN]})
        index.upsert(vectors=vectors, namespace=PINECONE_NAMESPACE)
