# Chat History

Large Language Models (LLMs) are inherently stateless, meaning they lack a built-in mechanism to retain information from one interaction to the next. However, incorporating chat history introduces a stateful element, enabling LLMs to recall past interactions with a user, thus personalizing the interaction experience. Mirascope provides a seamless solution to implement state and effectively manage scenarios where context limitations might otherwise be an issue.

## MESSAGES keyword

Let us take a simple chat application as our example. Every time the user makes a call to the LLM, the question and response is stored for the next call. To do this, use the `MESSAGES` keyword:

```python hl_lines="12"
import os

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

class Librarian(OpenAICall):
    prompt_template = """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {history}
    USER: {question}
    """

    question: str
    history: list[ChatCompletionMessageParam] = []

librarian = Librarian(question="", history=[])
while True:
    librarian.question = input("(User): ")
    response = librarian.call()
    if response.user_message_param:
        librarian.history.append(response.user_message_param)
    librarian.history.append(response.message_param)
    print(f"(Assistant): {response.content}")

#> (User): What fantasy book should I read?
#> (Assistant): Have you read the Name of the Wind?
#> (User): I have! What do you like about it?
#> (Assistant): I love the intricate world-building...
```

This will insert the history or context between the `SYSTEM` role and the `USER` role as additional messages in the messages array passed to the LLM.

!!! note
    Different model providers have constraints on their roles, so make sure you follow them when injecting `MESSAGES`. For example, Anthropic requires a back-and-forth between single user and assistant messages, and supplying two sequential user messages will throw an error.

## Streaming with Chat History

Using the same example as above, replace the `call` with `stream` and use our convenient `OpenAIStream` class to insert chat history with `user_message_param` and `message_param`:

```python
import os

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall, OpenAIStream

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Librarian(OpenAICall):
    prompt_template = """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {history}
    USER: {question}
    """

    question: str
    history: list[ChatCompletionMessageParam] = []


librarian = Librarian(question="", history=[])
while True:
    librarian.question = input("(User): ")
    if librarian.question == "exit":
        break
    stream = OpenAIStream(librarian.stream())
    print("(Assistant): ", end="")
    for chunk, tool in stream:
        if chunk.user_message_param:
            print(chunk.content, end="", flush=True)
    print()
    if stream.user_message_param:
        librarian.history.append(stream.user_message_param)
    librarian.history.append(stream.message_param)
```

## Overriding messages function

Alternatively, if you do not want to use the prompt_template parser, you can override the `messages` function instead.

```python hl_lines="16"
import os

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

class Librarian(OpenAICall):
    question: str
    history: list[ChatCompletionMessageParam] = []

    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {"role": "system", "content": "You are the world's greatest librarian."},
            *self.history,
            {"role": "user", "content": f"{self.question}"},
        ]

librarian = Librarian(question="", history=[])
while True:
    librarian.question = input("(User): ")
    response = librarian.call()
    if response.user_message_param:
        librarian.history.append(response.user_message_param)
    librarian.history.append(response.message_param)
    print(f"(Assistant): {response.content}")

#> (User): What fantasy book should I read?
#> (Assistant): Have you read the Name of the Wind?
#> (User): I have! What do you like about it?
#> (Assistant): I love the intricate world-building...
```

## Overcoming context limits with RAG

As your chat gets longer and longer, you will soon approach the context limit for the particular model. One not so great solution is to remove the oldest messages to stay within the context limit. For example:

```python hl_lines="27"
import os

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

class Librarian(OpenAICall):
    prompt_template = """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {history}
    USER: {question}
    """

    question: str
    history: list[ChatCompletionMessageParam] = []

librarian = Librarian(question="", history=[])
while True:
    librarian.question = input("(User): ")
    response = librarian.call()
    if response.user_message_param:
        librarian.history.append(response.user_message_param)
    librarian.history.append(response.message_param)
    # Limit to only the last 10 messages -- i.e. short term memory loss
    librarian.history = librarian.history[-10:]
    print(f"(Assistant): {response.content}")

#> (User): What fantasy book should I read?
#> (Assistant): Have you read the Name of the Wind?
#> (User): I have! What do you like about it?
#> (Assistant): I love the intricate world-building...
```

Better would be to implement a RAG (Retrieval-Augmented Generation) system for storing all chat history and querying for relevant previous messages for each interaction.

When the user makes a call, a search is made to find the most relevant information, which is then inserted as context to LLM, like so:

```python
import os
from uuid import uuid4

from openai.types.chat import ChatCompletionMessageParam

from mirascope.chroma import ChromaSettings, ChromaVectorStore
from mirascope.openai import OpenAICall, OpenAIEmbedder
from mirascope.rag import Document, TextChunker

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class LibrarianKnowledge(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "librarian-0001"
    client_settings = ChromaSettings()


store = LibrarianKnowledge()


class Librarian(OpenAICall):
    prompt_template = """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {history}
    USER: {question}
    """

    question: str

    @property
    def history(self) -> list[ChatCompletionMessageParam]:
        retrieval = store.retrieve(self.question, include=["metadatas", "documents"])
        documents = retrieval.documents[0]
        metadatas = retrieval.metadatas[0]
        return [
            {
                "role": metadatas[i]["role"],
                "content": document,
            }
            for i, document in enumerate(documents)
        ]


librarian = Librarian(question="", history=[])
while True:
    librarian.question = input("(User): ")
    if librarian.question == "exit":
        break
    response = librarian.call()

    store.add(
        [
            Document(
                id=str(uuid4()), text=librarian.question, metadata={"role": "user"}
            ),
            Document(
                id=str(uuid4()), text=response.content, metadata={"role": "assistant"}
            ),
        ]
    )
    print(f"(Assistant): {response.content}")
```

Check out [Mirascope RAG](./rag_(retrieval_augmented_generation).md) for a more in-depth look on creating a RAG application with Mirascope.
