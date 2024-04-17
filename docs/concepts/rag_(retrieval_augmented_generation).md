# RAG (Retrieval-Augmented Generation)

Retrieval-Augmented Generation (RAG) at a high level is a technique used to pull in knowledge outside an LLM’s training data to generate a response. This technique uses a vector database to store custom information such as company documents, databases, or other private information that is typically inaccessible in a vector format. When a user submits a query to the LLM, it first makes a semantic search in the vector database. The relevant data is then retrieved and included into the LLM's context giving more accurate results with reduced hallucination.

## Why use RAG?

RAG plays a crucial role in addressing significant challenges associated with LLMs:

1. **Hallucinations**: By providing the LLM with context and current information, RAG helps produce more accurate and relevant responses. This enhancement fosters user trust and reliability.
2. **Cost**: Training new models with expanded knowledge is both time-consuming and financially demanding. RAG circumvents these issues by supplements the model with additional data without the need for retraining.
3. **Domain Knowledge**: LLMs are trained on diverse data sets and lack the specificity required for certain tasks. RAG enables targeted knowledge making LLMs more adept at handling specialized requirements.

## RAG in Mirascope

A big focus on Mirascope RAG is not to reinvent how RAG is implemented but to speed up development by providing convenience. This is broken down into three main parts, `Chunkers` , `Embedders`, and `VectorStores` .

### Chunkers (Splitters)

Chunkers are the first step in setting up a RAG flow. To put it simply, long text or other forms of documents are split into smaller chunks to be stored. These smaller chunks help semantic search find information quicker and more accurately. In Mirascope, every Chunker extends `BaseChunker` which only has one requirement, the chunk function:

```python
import uuid
from mirascope.rag.chunkers import BaseChunker
from mirascope.rag.types import Document

class TextChunker(BaseChunker):
    """A text chunker that splits a text into chunks of a certain size and overlaps."""

    chunk_size: int
    chunk_overlap: int

    def chunk(self, text: str) -> list[Document]:
        chunks: list[Document] = []
        start: int = 0
        while start < len(text):
            end: int = min(start + self.chunk_size, len(text))
            chunks.append(Document(text=text[start:end], id=str(uuid.uuid4())))
            start += self.chunk_size - self.chunk_overlap
        return chunks

```

This is a simple example. You can use pre-existing chunkers like `TextChunker` or create your own by extending `BaseChunker` and implementing your own chunk function.

### Embedders

The next step would be to take the text chunks and embed them into vectors.

We currently only support [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings) but will soon support more.

```python
import os
from mirascope.openai import OpenAIEmbedder

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

embedder = OpenAIEmbedder()
response = embedder.embed(["your_message_to_embed"])
```

Most of the time you will not need to call our Embedder classes directly, but you are free to extend our `BaseEmbedder` for more specific types of embeddings.

### VectorStores

The final step to put it all together is to connect to a VectorStore and start using RAG. In this example we will be using [Chroma DB](https://www.trychroma.com/), with the same `TextChunker` and `OpenAIEmbedder` :

```python
# your_repo.stores.py
from mirascope.chroma import ChromaSettings, ChromaVectorStore
from mirascope.openai import OpenAIEmbedder
from mirascope.rag import TextChunker

class MyStore(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "my_index"

```

Just like that, your RAG system is ready to be used. Note that we are settings class variables to snapshot this configuration for a particular index, so when you use this store across multiple applications, there is consistency.

#### Add Documents

Anytime you have new documents, you can add to your vectorstore with a few lines of code.

```python
import os
from your_repo.stores import MyStore

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

for file_name in os.listdir("YOUR_DIRECTORY"):
    with open(f"YOUR_DIRECTORY/{file_name}") as file:
        data = file.read()
        store = MyStore()
        store.add(data)

```

#### Retrieve Documents

Combined with Mirascope [Calls](https://docs.mirascope.io/latest/concepts/generating_content/), you now have a RAG powered application.

```python
import os
from your_repo.stores import MyStore
from mirascope import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

class QuestionAnswerer(OpenAICall):
    prompt_template = """
    SYSTEM: 
    Answer the question based on the context.
    {context}
    USER: 
    {question}
    """

    question: str
    
    store: MyStore = MyStore()
    
    @property
    def context(self):
        return self.store.retrieve(self.question).documents

response = QuestionAnswerer(question="{YOUR_QUESTION_HERE}").call()
print(response.content)
```

#### Access Client and Index

You can access the VectorStore client and index by getting the private property `_client` and `_index` respectively. This is useful when you need to access VectorStore functionality such as `delete`.

```python
from your_repo.stores import MyStore

store = MyStore()
store._client
store._index
```

### Other Integrations

You can swap out your `Chunkers`, `Embedders`, and `VectorStores` by simply updating the imports. Let us know who you would like us to integrate with next.

## Roadmap

- [X]  Pinecone
- [ ]  Astra DB
- [ ]  Cohere Embeddings
- [ ]  HuggingFace
