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

if not os.path.exists("cookbook/basic_rag_example/news_article_dataset.csv"):
    url = "https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv"
    df = pd.read_csv(url)
    split_articles = []
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

    for i, row in df.iterrows():
        text = row["Text"]
        tokens = encoder.encode(text)
        if len(tokens) > 1000:
            words = text.split()
            num_splits = len(tokens) // 1000 + 1
            words_per_split = len(words) // num_splits
            split_texts = [
                " ".join(words[j : j + words_per_split])
                for j in range(0, len(words), words_per_split + 1)
            ]
            split_articles += split_texts
            df.drop(i, inplace=True)

    df = pd.concat(
        [df, pd.DataFrame(split_articles, columns=["Text"])], ignore_index=True
    )
    embeddings = []
    # ada 02 supports ~8000 tokens and 8 articles fit in the max batch size
    for start_idx in range(0, len(df), 8):
        end_idx = start_idx + 8
        batch = df["Text"][start_idx:end_idx].tolist()
        embeddings_response = chat.client.embeddings.create(
            model=embeddings_model, input=batch
        )
        embeddings += [datum.embedding for datum in embeddings_response.data]

    df["embeddings"] = embeddings
    df.to_csv(os.getcwd() + "/cookbook/basic_rag_example/news_article_dataset.csv")
else:
    df = pd.read_csv(
        os.getcwd() + "/cookbook/basic_rag_example/news_article_dataset.csv"
    )

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


batch_size = len(df) // 2
for batch_num, data in enumerate([df.iloc[:batch_size], df.iloc[batch_size:]]):
    vectors = [
        {"id": str(idx), "values": ast.literal_eval(row["embeddings"])}
        for idx, row in data.iterrows()
    ]
    index.upsert(vectors=vectors, namespace=f"batch{batch_num+1}")


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
    articles = []
    for batch in ["batch1", "batch2"]:
        query_response = index.query(namespace=batch, vector=query_embedding, top_k=2)
        relevant_article_indices = [
            int(article["id"]) for article in query_response["matches"]
        ]
        articles += relevant_article_indices
    relevant_articles = df.loc[articles]["Text"].tolist()
    prompt = NewsPrompt(topic=query, articles=relevant_articles)
    res = chat.create(prompt)
    print(str(prompt))
    print(res)


summarize_news("teams and players going through trouble in soccer")
summarize_news("market fluctuations due to environmental factors")
