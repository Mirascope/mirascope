# Retrieval Augmented Generation (RAG)

When you need to provide additional information to your model that it hasn't been pretrained on, we retrieve the relevant information from an external source and provide it as context to our model.

## A Barebones Retrieval Example

!!! note

    Take a look at the [code](https://github.com/Mirascope/mirascope/blob/main/cookbook/basic_rag_example/local_embeddings.py) in our repo.

Here are four simple statements about the 2022/3 soccer season that our chat model does not know:

```python
soccer_info = [
    "Manchester City won the league, continuing their domestic dominance.",
    "In La Liga, FC Barcelona emerged victorious with a sturdy defense.",
    "Dortmund slipped up in the last matchday to hand Bayern the Bundesliga title.",
    "For the first time since Maradona's days, Napoli lifted the Serie A trophy.",
]
```

The end goal is to be able to ask our model: which team in {insert_country} won the league in the 2023 season? Then, we want to put this additional context in our prompt to obtain the correct answer.

### Embeddings

To pick the text most relevant to our question from our information pool, we first need to embed each of the statements in `soccer_info`. Through our wrapper class [`OpenAIChat`](../api/chat/models.md#mirascope.chat.models.OpenAIChat), we can access the `OpenAI` model through the `OpenAI.client` attribute, then call [OpenAI's embeddings](https://platform.openai.com/docs/guides/embeddings):

```python
from mirascope import OpenAIChat, Prompt

chat = OpenAIChat(api_key="YOUR_OPENAI_API_KEY")
embeddings_model = "text-embedding-ada-002"

embeddings = [
    chat.client.embeddings.create(model=embeddings_model, input=[text])
    .data[0]
    .embedding
    for text in soccer_info
]

df = pd.DataFrame({"texts": soccer_info, "embeddings": embeddings})
```

### Retrieval

Here is the `Prompt` we will be using to ask our model:

```python
class SoccerPrompt(Prompt):
    """
    Here is some context about what happened in soccer in the 2022-23 season:
    {context}


    Based on this information, answer the following question:
    {question}
    """

    context: str
    question: str
```

But to provide `context`, we need to implement the retrieval functionality. To do this, we embed our question (`query_embedding`), then rank the similarities between `query_embedding` and each of the embeddings from `soccer_info` using the dot product between the vectors. The text with the highest value (and thus, similarity) is passed in as the context. And just like that, our basic RAG example is complete.

```python
def ask_soccer(query):
    """Answers a question about soccer from retrieved context."""
    query_embedding = (
        chat.client.embeddings.create(model=embeddings_model, input=[query])
        .data[0]
        .embedding
    )
    # Embedded texts are all the same length, so dot is equivalent to cosine
    df["similarities"] = df.embeddings.apply(lambda x: np.dot(x, query_embedding))
    most_similar = df.sort_values("similarities", ascending=False).iloc[0]["texts"]

    prompt = SoccerPrompt(context=most_similar, question=query)
    completion = chat.create(prompt)
    print(completion)


countries = ["English", "Spanish", "German", "Italian"]
for country in countries:
    ask_soccer(f"Who won the {country} top flight?")
```

## A More Realistic Approach...

!!! note

    This tutorial's code snippets have been rearranged to clearly demonstrate each step of the functionality. For a runnable script, take a look at the [code](https://github.com/Mirascope/mirascope/blob/main/cookbook/basic_rag_example/pinecone_embeddings.py) in our repo. Note that the repo code contains additional functionality and logic flows to make re-runs of the script as efficient as possible.

In reality, we could have passed the entirety of `soccer_info` into the prompt due to its small size. Let's take a look at a practical, scaled up example using the vector database Pinecone to manage the larger data.

Our dataset will be a collection of news articles from 2004 pulled from this [public Github database.](https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv) We will pick a topic, then ask our chat model to give a summary of 4 relevant articles.

### Dataset/Preprocessing

Chat and embedding models have token limits on a single call - this wasn't an issue in the soccer example, but these constraints come into play with much larger texts and datasets. For the purposes of this recipe, we split the large texts into roughly equal sizes using helper function `split_text()`. Since we want to be able to fit multiple articles into our final prompt, let's set `max_tokens=1000` and split the text into how many thousands of tokens the original text comprises of.

```python
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
MODEL = "gpt-3.5-turbo"
TEXT_COLUMN = "Text"
URL = "https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv"

df = load_data(URL)

encoder = tiktoken.encoding_for_model(MODEL)
split_articles = []

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
```

### Batched Embeddings

As before, we embed our texts. However, we can speed up the process and minimize token usage by embedding in batches. Since `max_tokens=1000` and the model `text-embedding-ada-002` has a token limit of 8096, we can pass in batches of 8.
```python
chat = OpenAIChat(model=MODEL)

EMBEDDINGS_COLUMN = "embeddings"

batch_size = 8    
embeddings = []

for start in range(0, len(df), batch_size):
    end = start + batch_size
    batch = df[TEXT_COLUMN][start:end].tolist()
    embeddings_response = chat.client.embeddings.create(
        model=embeddings_model, input=batch
    )
    embeddings += [datum.embedding for datum in embeddings_response.data]

df[EMBEDDINGS_COLUMN] = embeddings
```

### Pinecone Setup

For a large dataset, we can speed up querying with a vector database service like [Pinecone](https://www.pinecone.io/). We set up a Pinecone index and upsert our embedded vectors to it in batches to keep requests small. Note that this time around, we specify cosine similarity in our index to account for the different lengths of each text in our database.

```python
pc = Pinecone(api_key="YOUR_API_KEY")

pc.create_index(
    name="news-articles",
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
        vectors.append({"id": str(i), "values": row[EMBEDDINGS_COLUMN]})
    index.upsert(vectors=vectors, namespace="articles")
```

### Final Product

We're almost there! Just like the soccer example, we set up a `Prompt` to handle the chat structure. This time, we make our prompt a bit more complex, taking advantage of Mirascope's Pydantic prompts to nicely format the retrieved articles.

```python
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
```

Another change from the soccer example is how we query our context, in this case `articles`. Instead of calculating the vector similarities locally, we call `Index.query()` on our Pinecone index to let them efficiently do the hard work for us. Once the articles are retrieved, we take their indices and search them up in our `pd.Dataframe` to match them to the articles, and let Mirascope take care of the rest.

```python
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
```
