# Retrieval Augmented Generation (RAG)

When we need to provide additional information to the model that it hasn't yet been trained on, we can retrieve the relevant information from an external source and provide it as context to our model. For our example, we will use a dataset of [news articles from 2004](https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv). We will query the dataset with a topic of our choosing, retrieve a number of relevent articles, then ask our chat model to summarize the relevant ones. We will show how to query the dataset both locally and using a vector database (Pinecone), and how we can use Mirascope's Pydantic capabilities to let the prompts do all the work for us.

!!! note

    The following code snippets have been moved around for the sake of clarity in the walkthrough, and may not work if you copy and paste them. For a fully functional script, take a look at the [code](https://github.com/Mirascope/mirascope/blob/main/cookbook/rag_examples/) in our repo.

## Before we get started

To avoid any confusion, take note of the variables in the `config.py` and `.env` files:

`config.py`
```python
MODEL = "gpt-3.5-turbo"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
TEXT_COLUMN = "Text"
EMBEDDINGS_COLUMN = "embeddings"
FILENAME = "news_article_dataset.pkl"
URL = "https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv"
PINECONE_INDEX = "news-articles"
PINECONE_NAMESPACE = "articles"
```

`.env`
```python
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
```

## Load and preprocess the data

Before we just load raw data into a pandas `Dataframe`, we have to remember that calls to both chat and embeddings models have a token limit. In our case, where we will be putting multiple articles into a single prompt as context, the limiting factor is the chat's token limit. The solution is then to chunk larger articles into smaller pieces so we may still fit several retrieved texts into the context window. Using `tiktoken`, we calculate each article's token count and crudely chunk it into equal token sizes such that each chunk is less than a thousand tokens (considering the `gpt-3.5-turbo` has a context window of 4096 tokens):

```python
# utils.py

def load_data(url: str) -> pd.DataFrame:
    """Loads data from a url after splitting larger texts into smaller chunks."""
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
```

```python
df = load_data(url=URL)
```

Great! Now our `Dataframe` is loaded in where each article snippet is less than a thousand tokens.

### Embeddings

To be able to compare our articles with a topic of our choosing and determine relevancy, we need to embed each of them. Through our wrapper class [`OpenAIChat`](../api/chat/models.md#mirascope.chat.models.OpenAIChat), we can access the `OpenAI` model through the `OpenAI.client` attribute, then call [OpenAI's embeddings](https://platform.openai.com/docs/guides/embeddings):

```python
# utils.py

def embed_with_openai(
    text: Union[str, list[str]], chat: OpenAIChat
) -> list[list[float]]:
    """Embeds a string using OpenAI's embedding model.

    Args:
        text: A `str` or list of `str` to embed.
        chat: The `OpenAIChat` instance used for embedding.

    Returns:
        The embeddings of the text.
    """
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
    """Embeds a Pandas Series of texts in batches using minimal OpenAI calls.

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
```

```python
chat = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))
df = embed_df_with_openai(df=df, chat=chat)
```

Note that we can embed our texts in batches to save on calls to OpenAI, so we implement a simple greedy algorithm in `embed_df_with_openai()`. Also note that we will not see the `chat` variable for a while, but this will be the same `OpenAIChat` we use at the end of the project as our chat model.

### Retrieval ... but built into our prompts

We mentioned earlier that we will show how to perform retrieval in two ways: locally and via a vector database (Pinecone). In your own projects, you may want to perform retrieval in an entirely different way! Mirascope lets you build these functionalities into the prompts themselves, allowing for maximum refactorability and a clean prompt engineering experience. At the end of the day, we want to minimize superfluous scripting and trim all the fat which isn't the prompt engineering itself by letting you add pythonic structure and functionality to your prompts. Other than a [one-time pinecone setup](https://github.com/Mirascope/mirascope/blob/main/cookbook/rag_examples/setup_pinecone.py), our end goal is to be able to switch between non-prompting functionalities with one line.

First, we define some helper functions to take a topic, embed it, then compare its distance to the embeddings of all of our texts.

```python
# utils.py

# Local Retrieval
def query_dataframe(
    df: pd.DataFrame,
    query: str,
    num_results: int,
    chat: OpenAIChat,
) -> list[str]:
    """Searches a dataframe with embeddings for the most similar texts to a query.

    Since all embeddings vectors are the same length, the dot product is equivalent
    to cosine similarity and suffices.

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


# Pinecone Retrieval
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
```

Now, we can make bake these functionalities into the prompts themselves, with a shared parent class to make editing the core parts of the prompt as easy as possible.

```python
# rag_prompts/news_rag_prompt.py

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENAI_API_KEY: str
    PINECONE_API_KEY: str


@messages
class NewsRagPrompt(Prompt, abc.ABC):
    """
    SYSTEM:
    You are an expert at:
    1) determining the relevancy of articles to a topic, and
    2) summarizing articles concisely and eloquently.

    When given a topic and a list of possibly relevant texts, you determine for each
    text if it is truly relevant to the topic, and only if so, do you summarize it. You
    format your responses as only a list, where each item is a summary of an article or
    an explanation as to why it is not relevant.

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
    @abc.abstractmethod
    def context(self) -> str:
        """Finds most similar articles to topic using embeddings."""
        ...


class LocalNewsRagPrompt(NewsRagPrompt):
    __doc__ = inspect.getdoc(NewsRagPrompt)

    @property
    def context(self) -> str:
        """Finds most similar articles in dataframe using embeddings."""

        statements = query_dataframe(
            df=self.df,
            query=self.topic,
            num_results=self.num_statements,
            chat=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
        )
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
        )


class PineconeNewsRagPrompt(NewsRagPrompt):
    __doc__ = inspect.getdoc(NewsRagPrompt)

    _index: Pinecone.Index

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self._index = pc.Index(PINECONE_INDEX)

    @property
    def context(self) -> str:
        """Finds most similar articles in pinecone using embeddings."""
        indices = query_pinecone(
            index=self._index,
            query=self.topic,
            chat=OpenAIChat(api_key=os.getenv("OPENAI_API_KEY")),
            num_results=self.num_statements,
        )
        statements = self.df.iloc[indices][TEXT_COLUMN].to_list()
        return "\n".join(
            [f"{i+1}. {statement}" for i, statement in enumerate(statements)]
```

Thanks to Pydantic, through the `context` property, we can handle the retrieval functionality internally, as different as they may be. With this power, we can execute different versions of the program with only the following lines:

```python
topics = [
    "soccer teams/players going through trouble",
    "environmental factors affecting economy",
    "celebrity or politician scandals",
]
for topic in topics:
    # Run locally
    print(
        chat.create(LocalNewsRagPrompt(num_statements=3, topic=topic, df=df))
    )

    # Run on Pinecone
    print(
        chat.create(PineconeNewsRagPrompt(num_statements=3, topic=topic, df=df))
    )

```
