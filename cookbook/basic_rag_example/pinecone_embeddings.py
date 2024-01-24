"""A script using RAG and Pinecone to summarize relevant articles from a large database.

First we load in a dataset of news articles from 2004 and embed them. Then we use
Pinecone to efficiently find the articles with most relevance to a query, then use said
articles in a prompt to get the summary.
"""
import ast
import os

import pandas as pd
import tiktoken
from pinecone import Pinecone, ServerlessSpec

from mirascope import OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
chat = OpenAIChat()
embeddings_model = "text-embedding-ada-002"


def load_data(url) -> pd.DataFrame:
    """Loads data from a url, and splits larger texts into smaller chunks."""
    df = pd.read_csv(url)
    split_articles = []
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def split_text(text, tokens, max_tokens):
        """Roughly splits a text into chunks of max_tokens size.

        Note that tokens and characters do not have an exact correspondence, so in
        certain edge cases a chunk may be slightly larger than max_tokens.
        """
        words = text.split()
        num_splits = len(tokens) // max_tokens + 1
        words_per_split = len(words) // num_splits
        split_texts = [
            " ".join(words[i : i + words_per_split])
            for i in range(0, len(words), words_per_split + 1)
        ]
        return split_texts

    for i, row in df.iterrows():
        text = row["Text"]
        tokens = encoder.encode(text)
        if len(tokens) > 1000:
            split_articles += split_text(text, tokens, 1000)
            df.drop(i, inplace=True)

    # Long texts which were dropped from the dataframe are now readded.
    df = pd.concat(
        [df, pd.DataFrame(split_articles, columns=["Text"])], ignore_index=True
    )

    return df


def embed_data(df, batch_size):
    """Embeds a dataframe of texts and stores it in a new column."""
    embeddings = []
    # ada 02 supports ~8000 tokens and 8 articles fit in the max batch size
    for start in range(0, len(df), batch_size):
        end = start + batch_size
        batch = df["Text"][start:end].tolist()
        embeddings_response = chat.client.embeddings.create(
            model=embeddings_model, input=batch
        )
        embeddings += [datum.embedding for datum in embeddings_response.data]
    df["embeddings"] = embeddings

    return df


filename = "news_article_dataset.csv"
# Make reruns efficient by preprocessing data before saving to csv
if not os.path.exists("cookbook/basic_rag_example/news_article_dataset.csv"):
    url = "https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv"
    df = load_data(url)
    df = embed_data(df, 8)  # ada 02 supports ~8000 tokens, our max_tokens is 1000
    df.to_csv(f"{os.getcwd()}/cookbook/basic_rag_example/{filename}")
else:
    df = pd.read_csv(f"{os.getcwd()}/cookbook/basic_rag_example/{filename}")


pc = Pinecone(api_key="YOUR_API_KEY")
existing_indexes = pc.list_indexes().names()
index_name = "news-articles"
if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-west-2",
        ),
    )
index = pc.Index(index_name)


batch_size = 300  # Pinecone can't handle too large of an upsert request
for start in range(0, len(df), batch_size):
    end = min(start + batch_size, len(df))
    batch = df[start:end]
    vectors = []
    for i, row in batch.iterrows():
        embeddings = row["embeddings"]
        # Embeddings need to be parsed if they've been read from a csv
        if isinstance(embeddings[0], str):
            embeddings = ast.literal_eval(embeddings)
        vectors.append({"id": str(i), "values": embeddings})
    index.upsert(vectors=vectors, namespace="articles")


class NewsPrompt(Prompt):
    """
    Here are 4 relevant sections of news articles relevant to this topic: {topic}.
    Summarize them in a few sentences.

    {listed_articles}
    """

    topic: str
    articles: list[str]

    @property
    def listed_articles(self) -> str:
        return "\n".join(
            [f"{i+1}. {article}" for i, article in enumerate(self.articles)]
        )


def summarize_news(query):
    """Summarizes 2004 news about retrieved context relevant to query."""
    query_embedding = (
        chat.client.embeddings.create(model=embeddings_model, input=[query])
        .data[0]
        .embedding
    )
    query_response = index.query(namespace="articles", vector=query_embedding, top_k=4)
    relevant_article_indices = [
        int(article["id"]) for article in query_response["matches"]
    ]
    relevant_articles = df.loc[relevant_article_indices]["Text"].tolist()
    prompt = NewsPrompt(topic=query, articles=relevant_articles)
    completion = chat.create(prompt)
    print(str(prompt))
    print(completion)


summarize_news("teams and players going through trouble in soccer")
summarize_news("market fluctuations due to environmental factors")
