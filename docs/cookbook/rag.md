# Retrieval Augmented Generation (RAG)

When we need to provide additional information to the model that it hasn't yet been trained on, we can retrieve the relevant information from an external source and provide it as context to our model. For our example, we will use a dataset of [BBC news articles from 2004](https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv). We will:

- query the dataset with a topic of our choosing
- retrieve a number of relevant articles
- ask our chat model to summarize the relevant ones
- show how to query the dataset both locally and using a vector database ([Pinecone](https://docs.pinecone.io/))
- show how Mirascope can simplify RAG.

!!! note

    The following code snippets have been moved around for the sake of clarity in the walkthrough, and may not work if you copy and paste them. For a fully functional script, take a look at the [code](https://github.com/Mirascope/mirascope/blob/main/cookbook/news_rag/) in our repo.

## Before we get started

If you haven't already, it will be worth taking a look some of our relevant concept pages for a more detailed explanation of the functionality we'll be using in this walkthrough. Specifically, you'll want to know about how Pydantic allows us to integrate python functionality into our [prompts](https://docs.mirascope.io/latest/features/prompt/).


In addition, here are the variables we will be using in this cookbook recipe:

```python
# .env

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
```

```python
# rag_config.py

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

MODEL = "gpt-3.5-turbo"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
MAX_TOKENS = 1000
TEXT_COLUMN = "Text"
EMBEDDINGS_COLUMN = "embeddings"
FILENAME = "news_article_dataset.pkl"
URL = "https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv"
PINECONE_INDEX = "news-articles"
PINECONE_NAMESPACE = "articles"

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")
```



## Load and preprocess the data

Before we load raw data into a pandas `Dataframe`, we have to handle large texts which may exceed token limits. In our case, we are using `gpt-3.5-turbo`, which has a token limit of 4096. A crude solution is to split any article of token count greater than `MAX_TOKENS=1000` into equal chunks, with each resulting chunk consisting of fewer than `MAX_TOKENS`. This way we can fit up to 3 article snippets as well as any text in our hand-written section of the prompt. Note that we have also made sure that `MAX_TOKENS` is less than the token limit for our embedding model `text-embedding-ada-02` that has a token limit of 8191.

The function `split_text()` below contains the implementation.

For counting the number of tokens in an article, we will use [tiktoken](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb) since we will be using OpenAI for both the chat and embedding models. [tiktoken](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb) is a useful library provided by OpenAI for encoding strings and decoding tokens for their models.

```python
# rag_utils.py

import pandas as pd
import tiktoken
from rag_config import MODEL, TEXT_COLUMN,

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

```

```python
# rag_example.py

df = load_data(url=URL, max_tokens=MAX_TOKENS)
```

For further clarity, here is an example of the output of `split_texts()`:

```python
# sample_output of split_texts()

text = "..."
tokens = encoder.encode(text)
print(len(tokens))

# Output: 3200

split_texts = split_text(text=text, tokens=tokens, max_tokens=1000)
print([len(encoder.encode(split_text)) for split_text in split_texts])

# Output: [800 800, 800, 800]
# Explanation: 4 is the minimum number of times to split 3200 until each
# piece is less than max_tokens=1000, so we get 3200/4 = 800.
```

Great! Now our `Dataframe` is loaded in with article snippets where each snippet is less than a thousand tokens.

## Embeddings

To be able to take a topic of our choosing and determine each article’s relevancy, we need to embed them. We define some helper functions to use [OpenAI's embeddings](https://platform.openai.com/docs/guides/embeddings):

```python
# rag_utils.py

from typing import Union

import pandas as pd
import tiktoken
from rag_config import EMBEDDINGS_COLUMN, EMBEDDINGS_MODEL, MODEL, Settings
from openai import OpenAI

def embed_with_openai(text: Union[str, list[str]]) -> list[list[float]]:
    """Embeds a string using OpenAI's embedding model.

    Args:
        text: A `str` or list of `str` to embed.
        client: The `OpenAI` instance used for embedding.

    Returns:
        The embeddings of the text.
    """
    if isinstance(text, str):
        text = [text]
    client = OpenAI(api_key=settings.openai_api_key)
    embeddings_response = client.embeddings.create(model=EMBEDDINGS_MODEL, input=text)
    return [datum.embedding for datum in embeddings_response.data]


def embed_df_with_openai(df: pd.DataFrame) -> pd.DataFrame:
    """Embeds a Pandas Series of texts in batches using minimal OpenAI calls.

    Note that this function assumes all texts are less than 8192 tokens long.

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
    
    # We can embed multiple texts in a single OpenAI call, so we implement a
    # simple greedy algorithm according to ada-02's token limit of 8191.
    for i, text in enumerate(df[TEXT_COLUMN]):
        if batch_token_count + len(encoder.encode(text)) > max_tokens:
            embeddings += embed_with_openai(batch)
            batch = [text]
            batch_token_count = len(encoder.encode(text))
        else:
            batch.append(text)
            batch_token_count += len(encoder.encode(text))

    if batch:
        embeddings += embed_with_openai(batch)

    df[EMBEDDINGS_COLUMN] = embeddings
    return df

```

We call these functions on our pandas `Dataframe` of article snippets, giving us the embedding of each article snippet in the new column `EMBEDDINGS_COLUMN="embeddings"`.

```python
# rag_example.py

df = embed_df_with_openai(df=df)

# df[TEXT_COLUMN] contains article snippets
# df[EMBEDDINGS_COLUMN] contains embedding for each snippet
```

## Retrieval ... but built into our prompts

We mentioned earlier that we will show how to perform retrieval in two ways: locally and via a vector database (Pinecone). In your own projects, you may want to perform retrieval in an entirely different way.

With any of Mirascope's prompts, we can use Python built-ins with Pydantic to implement complex, prompt-specific logic directly within the prompt itself — we can focus on prompt engineering, not the little things. This ensures that prompt-specific logic is well encapsulated, forcing a clean separation from the rest of the codebase. Furthermore, any updates to the prompt logic or template can be maintained and versioned with our CLI - check that out [here](https://docs.mirascope.io/latest/features/engineering_better_prompts/mirascope_cli/).

In this example, we are going to create two different prompt classes using `OpenAIPrompt`:

- `LocalNewsRag`: this prompt class will use a local `pd.DataFrame` to find the relevant article chunks.
- `PineconeNewsRag`: this prompt class will query a Pinecone vector database to find the relevant article chunks.

The querying logic for relevant article retrieval will live within each prompt's `context` property, regardless of whether it is the local or vector database implementation. In the local iteration, we manually calculate (using the dot product) the distances between each article snippet's embedding and the embedding of our chosen topic - the articles whose embeddings are closest are then chosen. For the vector database, we make a Pinecone API call to perform the same task via their streamlined architecture.

!!! note

    The querying logic for Pinecone lives within the PineconeNewsRagPrompt, but you must still do a [one-time pinecone setup](https://github.com/Mirascope/mirascope/blob/main/cookbook/rag_examples/setup_pinecone.py).

### LocalNewsRagPrompt

```python
# rag_prompts/local_news_rag_prompt.py

import numpy as np
import pandas as pd
from pydantic import ConfigDict
from rag_config import EMBEDDINGS_COLUMN, TEXT_COLUMN, Settings
from rag_utils import embed_with_openai

from mirascope.openai import OpenAIPrompt

settings = Settings()


class LocalNewsRag(OpenAIPrompt):
    """
    SYSTEM:
    You are an expert at:
    1) determining the relevancy of articles to a topic, and
    2) summarizing articles concisely and eloquently.

    When given a topic and a list of possibly relevant texts, you format your responses
    as a single list, where you summarize the articles relevant to the topic or explain
    why the article is not relevant to the topic.

    USER:
    Here are {num_statements} article snippets about this topic: {topic}

    {context}

    Pick only the snippets which are truly relevant to the topic, and summarize them.
    """

    num_statements: int
    topic: str
    df: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def context(self) -> str:
        """Finds most similar articles in dataframe using embeddings."""

        query_embedding = embed_with_openai(self.topic)[0]
        self.df["similarities"] = self.df[EMBEDDINGS_COLUMN].apply(
            lambda x: np.dot(x, query_embedding)
        )
        most_similar = self.df.sort_values("similarities", ascending=False).iloc[
            : self.num_statements
        ][TEXT_COLUMN]
        statements = most_similar.to_list()
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
        )
```

### PineconeNewsRagPrompt

```python
# rag_prompts/pinecone_news_rag_prompt.py

import pandas as pd
from pinecone import Pinecone
from pydantic import ConfigDict
from rag_config import PINECONE_INDEX, PINECONE_NAMESPACE, TEXT_COLUMN, Settings
from rag_utils import embed_with_openai

from mirascope.openai import OpenAIPrompt

settings = Settings()


class PineconeNewsRag(OpenAIPrompt):
    """
    SYSTEM:
    You are an expert at:
    1) determining the relevancy of articles to a topic, and
    2) summarizing articles concisely and eloquently.

    When given a topic and a list of possibly relevant texts, you format your responses
    as a single list, where you summarize the articles relevant to the topic or explain
    why the article is not relevant to the topic.

    USER:
    Here are {num_statements} article snippets about this topic: {topic}

    {context}

    Pick only the snippets which are truly relevant to the topic, and summarize them.
    """

    num_statements: int
    topic: str
    df: pd.DataFrame

    _index: Pinecone.Index

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index = pc.Index(PINECONE_INDEX)

    @property
    def context(self) -> str:
        """Finds most similar articles in pinecone using embeddings."""
        query_embedding = embed_with_openai(self.topic)[0]
        query_response = self._index.query(
            namespace=PINECONE_NAMESPACE,
            vector=query_embedding,
            top_k=self.num_statements,
        )
        indices = [int(article["id"]) for article in query_response["matches"]]
        statements = self.df.iloc[indices][TEXT_COLUMN].to_list()
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
        )
```

## Retrieval Script For Topics

We've built the retrieval functionality into the prompts themselves - now, we can build a script to use these prompts without having to worry about formatting the context or retrieving relevant articles:

```python
# rag_example.py

import os
from argparse import ArgumentParser

import pandas as pd
from rag_config import FILENAME, MAX_TOKENS, URL, Settings
from local_news_rag_prompt import LocalNewsRagPrompt
from pinecone_news_rag_prompt import PineconeNewsRagPrompt
from setup_pinecone import setup_pinecone
from rag_utils import embed_df_with_openai, load_data

from mirascope import OpenAIChat

settings = Settings()

def main(use_pinecone=False):
    chat = OpenAIChat(api_key=settings.openai_api_key)
    df = load_data(url=URL, max_tokens=MAX_TOKENS)
    df = embed_df_with_openai(df=df, client=chat.client)

    # This method does nothing if a Pinecone index is already set up.
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
```
