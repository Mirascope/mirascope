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

MODEL = "gpt-3.5-turbo"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
TEXT_COLUMN = "Text"
EMBEDDINGS_COLUMN = "embeddings"

chat = OpenAIChat(model=MODEL)

FILENAME = "news_article_dataset.csv"
URL = "https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv"


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


def embed_data(df: pd.DataFrame, batch_size: int) -> pd.DataFrame:
    """Embeds a dataframe of texts and stores it in a new column."""
    embeddings = []
    for start in range(0, len(df), batch_size):
        end = start + batch_size
        batch = df[TEXT_COLUMN][start:end].tolist()
        embeddings_response = chat.client.embeddings.create(
            model=EMBEDDINGS_MODEL, input=batch
        )
        embeddings += [datum.embedding for datum in embeddings_response.data]
    df[EMBEDDINGS_COLUMN] = embeddings

    return df


# Make reruns efficient by preprocessing data before saving to csv
if not os.path.exists(FILENAME):
    df = load_data(URL)
    # df = embed_data(df, 8)  # ada 02 supports ~8000 tokens, our max_tokens is 1000
    df.to_csv(FILENAME)
else:
    df = pd.read_csv(FILENAME)


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
        embeddings = row[EMBEDDINGS_COLUMN]
        # Embeddings need to be parsed if they've been read from a csv
        if isinstance(embeddings[0], str):
            embeddings = ast.literal_eval(embeddings)
        vectors.append({"id": str(i), "values": embeddings})
    index.upsert(vectors=vectors, namespace="articles")


class NewsPrompt(Prompt):
    """
    Here are {num_articles} relevant sections of news articles relevant to this topic:
    {topic}. Summarize them in a few sentences.

    {listed_articles}
    """

    num_articles: int
    topic: str
    articles: list[str]

    @property
    def listed_articles(self) -> str:
        return "\n".join(
            [f"{i+1}. {article}" for i, article in enumerate(self.articles)]
        )


def summarize_news(query: str, num_articles: int) -> str:
    """Summarizes 2004 news about retrieved context relevant to query."""
    query_embedding = (
        chat.client.embeddings.create(model=EMBEDDINGS_MODEL, input=[query])
        .data[0]
        .embedding
    )
    query_response = index.query(
        namespace="articles", vector=query_embedding, top_k=num_articles
    )
    relevant_article_indices = [
        int(article["id"]) for article in query_response["matches"]
    ]
    relevant_articles = df.loc[relevant_article_indices][TEXT_COLUMN].tolist()
    prompt = NewsPrompt(
        num_articles=num_articles, topic=query, articles=relevant_articles
    )

    return str(chat.create(prompt))


print(summarize_news("teams and players going through trouble in soccer", 3))
print("\n")
print(summarize_news("market fluctuations due to environmental factors", 4))
