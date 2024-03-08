"""A script using RAG to summarize relevant articles from a large database in 2 ways.

News articles from 2004 are embedded so they may be queried (in two ways) according to a
topic of choice. In the first way we manually calculate similarity between query and
embeddings. In the second, we set up Pinecone and efficiently use its search to find the
most relevant articles. In both cases, we use the Mirascope library to handle the logic
so as to streamline prompt creation.
"""
import os
from argparse import ArgumentParser

import pandas as pd
from rag_config import FILENAME, MAX_TOKENS, URL, Settings
from rag_prompts.local_news_rag_prompt import LocalNewsRag
from rag_prompts.pinecone_news_rag_prompt import PineconeNewsRag
from rag_utils import embed_df_with_openai, load_data
from setup_pinecone import setup_pinecone

settings = Settings()


def main(use_pinecone=False):
    if not os.path.exists(FILENAME):
        df = load_data(url=URL, max_tokens=MAX_TOKENS)
        df = embed_df_with_openai(df=df)
        df.to_pickle(FILENAME)
    else:
        df = pd.read_pickle(FILENAME)

    if use_pinecone:
        setup_pinecone(df=df)

    topics = [
        "soccer teams/players going through trouble",
        "environmental factors affecting economy",
        "celebrity or politician scandals",
    ]
    for topic in topics:
        if use_pinecone:
            pinecone = PineconeNewsRag(num_statements=3, topic=topic, df=df)
            print(pinecone.create())
        else:
            local = LocalNewsRag(num_statements=3, topic=topic, df=df)
            print(local.create())
        print("\n")


if __name__ == "__main__":
    parser = ArgumentParser(description="Process some flags.")
    parser.add_argument(
        "-pc", "--pinecone", action="store_true", help="Activate Pinecone mode"
    )
    args = parser.parse_args()
    main(use_pinecone=args.pinecone)
