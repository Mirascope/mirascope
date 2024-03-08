"""Script to upload a dataset to Pinecone.

Note that for the sake of user experience, we assume that if the Pinecone Index exists,
it already contains all the embeddings from the dataframe. To work around this, we would
need to check the numbers of vectors in the Index, which entails the user having to copy
and paste the Pinecone host URL after the Index is created, which is a headache. In the
case of failed upsertions, manually delete the Pinecone Index and try again.
"""
import os

import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from pinecone.core.client.exceptions import PineconeApiException
from rag_config import EMBEDDINGS_COLUMN, PINECONE_INDEX

load_dotenv()


def setup_pinecone(df: pd.DataFrame, max_retries: int = 3) -> None:
    """Sets up a Pincone Index and upserts embeddings from dataframe if needed.

    Creates a Pinecone Index and upserts vectors from Dataframe if Index doesn't
    currently exist. Each upserted embedding has ID set as index from original dataframe
    to help keep track of the affiliated text later on. Vectors are upserted in batches
    of 300 (determined by trial and error) so as not to overload Pinecone.

    Args:
        df: The dataframe which contains embeddings to upsert.
        max_retries: The maximum number of times to retry upserting vectors to Pinecone.
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
            vectors = [
                {"id": str(i), "values": row[EMBEDDINGS_COLUMN]}
                for i, row in batch.iterrows()
            ]
            attempt = 0
            while attempt < max_retries:
                try:
                    index.upsert(vectors)
                    break
                except PineconeApiException as e:
                    attempt += 1
                    if attempt >= max_retries:
                        print(
                            f"Upsert failed after {max_retries} attempts, starting "
                            f"at index {start}"
                        )
                        raise e
