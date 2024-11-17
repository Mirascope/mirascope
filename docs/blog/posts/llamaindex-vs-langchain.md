---
title: LlamaIndex vs LangChain vs Mirascope - An In-Depth Comparison
description: >
  Explore our comprehensive guide on LlamaIndex vs LangChain. We also introduce Mirascope's modular toolkit for LLM application development.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-05-15
slug: llamaindex-vs-langchain
---

# LlamaIndex vs LangChain vs Mirascope: An In-Depth Comparison

In the context of building Large Language Model (LLM) applications—and notably Retrieval Augmented Generation (RAG) applications—the consensus seems to be that:

- LlamaIndex excels in scenarios requiring robust data ingestion and management.
- LangChain is suitable for chaining LLM calls and for designing autonomous agents.

In truth, the functionalities of both frameworks often overlap. For instance, LangChain offers document loader classes for data ingestion, while LlamaIndex lets you build autonomous agents.

<!-- more -->

**Which framework you actually choose will depend on a lot of different factors, such as:**

- What kind of application you’re building, e.g., are you building a RAG or other app requiring vectorization and storage of large amounts of data?
  ‍
- Which LLM you’re using, i.e., which framework offers better integration with the LLM you want.
  ‍
- What features you’re looking to use, e.g., LangChain offers high-level abstractions for building agents, whereas this would require more code in LlamaIndex.

But even here, decisions about which framework to use can still be based mostly on subjective preferences, personal experience, or even hearsay.

**To help sort out the ambiguity, this article points out some of the similarities and differences between LlamaIndex and LangChain in terms of four key differentiators:**

- How do you accomplish prompting in each framework?
- What RAG-specific functionality is provided?
- How easy is it to scale your solution when building production-grade LLM applications?
- How is chaining implemented?

In addition, we’ll compare and contrast these libraries with [Mirascope](https://github.com/mirascope/mirascope), our own Python toolkit for building with LLMs.

## Prompting the LLM

### LlamaIndex: Retrieves Indexed Information for Sophisticated Querying

In the context of RAG, prompting in LlamaIndex is based on [`QueryEngine`](https://docs.llamaindex.ai/en/stable/understanding/querying/querying/). This is a class that takes your input, then goes and searches its index for information related to your input, and sends both together as a single, enriched prompt to the LLM.

Central to LlamaIndex is, of course, its index of vectorized information, which is a data structure consisting of documents that are referred to as “nodes.” LlamaIndex offers several types of indices, but the most popular variant is its VectorStoreIndex that stores information as vector embeddings, to be extracted in the context of queries via semantic search.

Sending such enriched prompts to the LLM (queries plus information from the index) have the advantage of increasing LLM accuracy and reducing hallucinations.

As for the prompts themselves, LlamaIndex makes available several predefined templates for you to customize to your particular use case. Such templates are particularly suited for developing RAG applications.

In this [example reproduced from their documentation](https://docs.llamaindex.ai/en/stable/module_guides/models/prompts/), the `PromptTemplate` class is imported and can then be customized with a query string:

```python
from llama_index.core import PromptTemplate

template = (
    "We have provided context information below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given this information, please answer the question: {query_str}\n"
)
qa_template = PromptTemplate(template)

# you can create text prompt (for completion API)
prompt = qa_template.format(context_str=..., query_str=...)

# or easily convert to message prompts (for chat API)
messages = qa_template.format_messages(context_str=..., query_str=...)
```

### LangChain: Offers Prompt Templates for Different Use Cases

Similar to LlamaIndex, LangChain offers a number of [prompt templates](https://mirascope.com/blog/langchain-prompt-template) corresponding to different use cases:

- `PromptTemplate` is the standard prompt for many use cases.
- `FewShotPromptTemplate` for few-shot learning.
- `ChatPromptTemplate` for multi-role chatbot interactions.

LangChain encourages you to customize these templates, though you’re free to code your own prompts. You can also merge different LangChain templates as needed.

An example of a `FewShotPromptTemplate` from [LangChain’s documentation](https://python.langchain.com/docs/modules/model_io/prompts/few_shot_examples/):

```python
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

examples = [
    {
        "question": "Who lived longer, Muhammad Ali or Alan Turing?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: How old was Muhammad Ali when he died?
Intermediate answer: Muhammad Ali was 74 years old when he died.
Follow up: How old was Alan Turing when he died?
Intermediate answer: Alan Turing was 41 years old when he died.
So the final answer is: Muhammad Ali
""",
    },
    {
        "question": "When was the founder of craigslist born?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: Who was the founder of craigslist?
Intermediate answer: Craigslist was founded by Craig Newmark.
Follow up: When was Craig Newmark born?
Intermediate answer: Craig Newmark was born on December 6, 1952.
So the final answer is: December 6, 1952
""",
    },
]
```

‍LangChain’s prompting templates are straightforward to use; however the framework provides neither automatic error checking (e.g., for prompt inputs), nor inline documentation for your code editor. It’s up to developers to handle errors.

When it comes to prompt versioning, LangChain offers this capability in its LangChain Hub, which is a centralized prompt repository that implements versioning as commit hashes.

### Mirascope: One Prompt That Type Checks Inputs Automatically

Rather than attempt to tell you how you should formulate prompts, Mirascope provides its [`prompt_template`](https://mirascope.com/learn/prompts) decorator so you can write prompt templates as standard Python functions.

Our `prompt_template` decorator allows you to automatically generate prompt messages simply by calling the function, which returns the list of `BaseMessageParam` instances.

You can also incorporate values computed inside the function into the prompt either directly (through f-strings) or as `computed_fields` when using string templates.

As a result, you can integrate complex calculations or conditional formatting directly into your output without manually updating the content each time the underlying data changes.

In the example below, `list` and `list[list]` are automatically formatted with `\n` and `\n\n` separators, before being stringified:

```python
from mirascope.core import BaseDynamicConfig, prompt_template


@prompt_template(
    """
    Recommend some books on the following topic and genre pairs:
    {topics_x_genres:list}
    """
)
def recommend_book_prompt(topics: list[str], genres: list[str]) -> BaseDynamicConfig:
    topics_x_genres = [
        f"Topic: {topic}, Genre: {genre}" for topic in topics for genre in genres
    ]
    return {"computed_fields": {"topics_x_genres": topics_x_genres}}


messages = recommend_book_prompt(["history", "science"], ["biography", "thriller"])
print(messages)
# > [BaseMessageParam(role='user', content='Recommend some books on the following topic and genre pairs:\nTopic: history, Genre: biography\nTopic: history, Genre: thriller\nTopic: science, Genre: biography\nTopic: science, Genre: thriller')]
print(messages[0].content)
# > Recommend some books on the following topic and genre pairs:
#   Topic: history, Genre: biography
#   Topic: history, Genre: thriller
#   Topic: science, Genre: biography
#   Topic: science, Genre: thriller
```

Because Mirascope prompt templates are written as functions, you can use Pydantic's [`validate_call`](https://docs.pydantic.dev/latest/concepts/validation_decorator/) decorator to ensure that inputs are correctly typed according to their argument type hints and handle any validation errors gracefully.

your own custom validation using Pydantic’s `AfterValidator` class. This is helpful for cases like verifying whether data processing rules are compliant with GDPR regulations:

```python
from enum import Enum
from typing import Annotated, Type

from mirascope.core import openai, prompt_template
from pydantic import AfterValidator, BaseModel, ValidationError


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"


@openai.call(model="gpt-4o-mini", response_model=ComplianceStatus)
@prompt_template(
    """
    Is the following data processing procedure compliant with GDPR standards?
    {procedure_text}
    """
)
def check_gdpr_compliance(procedure_text: str): ...


def validate_compliance(procedure_text: str) -> str:
    """Check if the data processing procedure is compliant with GDPR standards."""
    compliance_status = check_gdpr_compliance(procedure_text=procedure_text)
    assert (
        compliance_status == ComplianceStatus.COMPLIANT
    ), "Procedure is not GDPR compliant."
    return procedure_text


class DataProcessingProcedure(BaseModel):
    text: Annotated[str, AfterValidator(validate_compliance)]


@openai.call(model="gpt-4o-mini", response_model=DataProcessingProcedure)
@prompt_template(
    """
    Write a detailed description of a data processing procedure.
    It MUST be compliant with GDPR standards.
    """
)
def write_procedure(): ...


try:
    print(write_procedure())
except ValidationError as e:
    print(e)
    # > 1 validation error for DataProcessingProcedure
    # procedure_text
    # Assertion failed, Procedure is not GDPR compliant.
    # [type=assertion_error, input_value="The procedure text here...", input_type=str]
    # For further information visit https://errors.pydantic.dev/2.6/v/assertion_error
```

Mirascope also offers a prompt engineering framework called [Lilypad](https://lilypad.so/docs), which versions and traces every LLM function call and prompt automatically. By removing the worry of manually tracking changes systematically, Lilypad provides you the headspace to rapidly iterate on and optimize prompts, ensuring that all your fine-tuning efforts are recorded and retrievable.

Furthermore, Lilypad is also fully open-source and can be run locally.

```python
|
|-- .lilypad/
|-- |-- config.json
|-- lily/
|   |-- __init__.py
|   |-- {llm_function_name}.py
|-- pad.db
```

The framework structure primarily includes:

- The `lily/` director for all your LLM functions
- The `pad.db` SQLite database for local development where versions and traces are stored.

The `Lilypad` CLI also provides commands such a `create` for easily creating a new LLM function shim and `run` to reasily run LLM functions in development.

## Functionality for RAG Applications

### LlamaIndex: Uses Advanced Data Embedding and Retrieval

LlamaIndex is well known for its indexing, storage, and retrieval capabilities in the context of developing RAG applications, and provides a number of [high-level abstractions](https://docs.llamaindex.ai/en/stable/getting_started/concepts/) for:

- Importing and processing different data types such as PDFs, text files, websites, databases, etc., through document loaders and nodes.
- Creating vector embeddings (indexing) from the data previously loaded, for fast and easy retrieval.
- Storing data in a vector store, along with metadata for enabling more context-aware search.
- Retrieving data that’s relevant to a given query and sending these both together to the LLM for added context and accuracy.

Such abstractions let you build data pipelines for handling large volumes of data. LlamaIndex's RAG functionality is based on its Query Engine, which queries and retrieves information from indexed data, and then sends these as a prompt enriched by retrieved data to the LLM.

### LangChain: Offers Abstractions for Indexing, Storage, and Retrieval

LangChain offers similar abstractions to that of LlamaIndex for building data pipelines for [RAG applications](https://python.langchain.com/docs/use_cases/question_answering/quickstart/). These abstractions correspond to two broad phases:

- An **indexing phase** , where data is loaded (via document loaders), split into separate chunks, and stored in a vector store and embedding model.
- A **retrieval and generation phase** , where embeddings relevant to a query are retrieved, passed to the LLM, and responses generated.

Such abstractions include DocumentLoaders, text splitters, VectorStores, and embedding models.

### Mirascope: RAG Beta

Mirascope’s current abstractions for RAG emphasize ease of use and speed of development, allowing you to create pipelines for querying and retrieving information for accurate LLM outputs. Mirascope currently offers three main classes to reduce the complexity typically associated with building RAG systems, but we aren't certain that existing RAG frameworks (or our current implementation) live at the right level of abstraction. This is why the majority of our RAG features still remain in beta.

If you have any strong opinions about what's missing from existing RAG frameworks, let us know!

#### `BaseChunker`

We provide a class to simplify the chunking of documents into manageable pieces for efficient semantic search. In the code below, we instantiate a simple `TextChunker` but you can extend `BaseChunker` as needed:

```python
import uuid

from mirascope.beta.rag import BaseChunker, Document


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

#### `BaseEmbedder`

With this class you transform text chunks into vectors with minimal setup. At the moment Mirascope supports OpenAI and Cohere embeddings, but you can extend `BaseEmbedder` to suit your particular use case.

```python
from mirascope.beta.rap.openai import OpenAIEmbedder


embedder = OpenAIEmbedder()
response = embedder.embed(["your_message_to_embed"])
```

#### ‍ Vector Stores

Besides chunking and vectorizing information, Mirascope also provides storage via integrations with well-known solutions such as Chroma DB and Pinecone.

The code below shows usage of both `TextChunker` and the `OpenAIEmbedder` together with `ChromaVectorStore`:

```python
# your_repo.stores.py
from mirascope.beta.rag.base import TextChunker
from mirascope.beta.rag.chroma import ChromaVectorStore
frim mirascope.beta.rag.openai import OpenAIEmbedder


class MyStore(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "my_index"
```

‍Mirascope provides additional methods for adding and retrieving documents to and from the vector store, as well as accessing the client store and index. You can find out more about these, as well as our integrations with LlamaIndex and [other frameworks](https://mirascope.com/blog/langchain-alternatives), in our documentation.

## Scaling Solutions for Production-Grade LLM Applications

### LlamaIndex: Offers a Wide Scope of Integrations and Data Types

As a data framework, LlamaIndex is designed to handle large datasets efficiently, provided it’s correctly set up and configured. It features literally [hundreds of loaders and integrations](https://llamahub.ai/) for connecting custom data sources to LLMs.

However, it seems to us that, when it comes to building RAG applications, LlamaIndex can be rigid in certain ways. For instance, its `VectorStoreIndex` class doesn’t permit setting the embedding model post-initialization, limiting how developers can adapt LlamaIndex to different use cases or existing systems. This can hinder scalability as it complicates the integration of custom models and workflows.

### LangChain: A General Framework Covering Many Use Cases

LangChain offers functionalities covering a wide range of use cases, such that if you can think of a use case, it’s likely you can set it up in LangChain. For example, just like LlamaIndex, it similarly provides document and [BigQuery loaders](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/language/orchestration/langchain/langchain_bigquery_data_loader.ipynb) for data ingestion.

On the other hand, like LlamaIndex, it rigidly defines how you implement some of your use cases. As an example, it requires you to predetermine [memory allocation](https://python.langchain.com/docs/modules/memory/types/buffer/) for AI chat conversations. Developers also find that LangChain requires many dependencies, even for simple tasks.

### Mirascope: Centralizes Everything Around the LLM Call to Simplify Application Development

We understand the value of a library that scales well, so we’ve designed Mirascope to be as simple and easy to use as possible.

For instance, we minimize the number of special abstractions you must learn when building LLM pipelines, and offer convenience only where this makes sense, such as for wrapping API calls. You can accomplish much with vanilla Python and OpenAI’s API, so why create complexity where you can just leverage Python’s inherent strengths?

Therefore all you need to know is vanilla Python and the Pydantic library. We also try to push design and implementation decisions onto developers to offer them maximum adaptability and control.

And unlike other frameworks, we believe that everything that can impact the quality of an LLM call (from model parameters to prompts) should live together with the call. The LLM call is therefore the [central organizing unit of our code](https://mirascope.com/blog/engineers-should-handle-prompting-llms) around which everything gets versioned and tested.

A prime example of this is Mirascope’s use of [`call_params`](https://mirascope.com/learn/calls/#provider-specific-parameters), which contains all the parameters of the LLM call and typically lives inside the call:

```python
from mirascope.core import openai


@openai.call(model="gpt-4o-mini", call_params={"temperature": 0.6})
def plan_travel_itinerary(destination: str) -> str:
    return f"Plan a travel itinerary that includes activities in {destination}"


response = plan_travel_itinerary("Paris")
print(response.content)  # prints the string content of the call
```

In Mirascope, prompts are written as Python functions, making code changes affecting the call easier to trace, thereby reducing errors and making your code simpler to maintain.

## Chaining LLM Calls

### LlamaIndex: Chains Modules Together Using QueryPipeline

LlamaIndex offers [`QueryPipeline`](https://docs.llamaindex.ai/en/stable/examples/pipeline/query_pipeline/) for chaining together different modules to orchestrate LLM application development workflows. Through `QueryPipeline`, LlamaIndex defines four use cases for chaining:

- Chaining together a prompt with an LLM call.
- Chaining together query rewriting (prompt + natural language model) with retrieval.
- Chaining together a full RAG query pipeline (query rewriting, retrieval, reranking, response synthesis).
- Setting up a custom query component that allows you to integrate custom operations into a larger query processing pipeline.

Although these are useful to implement, `QueryPipeline` is a built-in abstraction that hides the lower-level details and entails a learning curve to use.

### LangChain: Requires an Explicit Definition of Chains and Flows

LangChain similarly offers its own abstractions for chaining, requiring explicit definition of chains and flows via its LangChain Expression Language (LCEL). This provides a unified interface for building chains and notably implements `Runnable`, which defines common methods such as `invoke`, `batch`, and `stream`.

A typical example of a chain in LangChain is shown below, which uses `RunnablePassthrough`, an object that forwards data to where it needs to go in the chain without changes:

```python
# Setup for temperature conversion using a query pipeline
runnable = (
    {"temperature_query": RunnablePassthrough()}
    | prompt
    | model.bind(stop="CONVERSION_COMPLETED")
    | StrOutputParser()
)
print(runnable.invoke("Convert 35 degrees Celsius to Fahrenheit"))
```

‍Here, `RunnablePassthrough` is passing `temperature_query` unaltered to `prompt`, while `Runnable.bind` in this instance allows users to define a stop condition at runtime when the token or text “CONVERSION_COMPLETED” is encountered. The condition sets up the model to behave in a certain way after it’s been invoked.

Binding arguments to the model at runtime in such a way is the functional equivalent of Mirascope’s `call_params` (described above) and can be useful in situations where you want to take into account user interactions, in this case allowing users to mark a solution as being solved.

On the other hand, such conditions need to be carefully managed in all instances of chains to avoid negative impacts on the system.

### Mirascope: Leverages Python’s Functional Syntax for Chaining

Mirascope chains multiple calls together using a more implicit approach than that of LlamaIndex and LangChain, relying on structured that already exist in Python.

In the example below, chaining is implemented simply by calling each part of the chain inside of the parent function, using `computed_fields` to propagate each part of the chain up into the final response, ensuring that all input and output values along the chain will be visible from the dump of the final call.

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
def get_brand_expert(vehicle_type: str) -> str:
    return f"Name a {vehicle_type} vehicle expert. Return only their name."


@openai.call("gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Imagine that you are the expert {brand_expert}.
    Your task is to recommend cars that you, {brand_expert}, would be excited to suggest.

    USER:
    Recommend a {vehicle_type} car that fits the following criteria: {criteria}.
    """
)
def recommend_car(vehicle_type: str, criteria: str) -> openai.OpenAIDynamicConfig:
    brand_expert = get_brand_expert(vehicle_type=vehicle_type)
    return {"computed_fields": {"brand_expert": brand_expert}}


response = recommend_car(
    vehicle_type="electric", criteria="best range and safety features"
)
print(response.content)
# > Certainly! Here's a great electric car with the best range and safety features: ...
```

‍Making only a single call in this way keeps the application’s response times quick and reduces both expensive API calls and the load on the underlying systems.

As well, relying on Pythonic structures you already know keeps your code readable and maintainable, even as your chains and specific needs grow in complexity.

## Mirascope Allows You to Easily Leverage the Strengths of External Libraries

Mirascope’s building block approach to developing generative AI applications means you can easily pick and choose useful pieces from other libraries when you need them.

Just import the functionality you want—and nothing more—from libraries like LangChain and LlamaIndex to get the benefit of what those libraries do best. For instance, Mirascope makes it easy to import LlamaIndex’s `VectorStoreIndex` for document storage in the context of RAG, and to further inject information retrieved from this vector store into your LLM calls.

Our approach allows you to use and combine the best available open-source tools for any specific task in your LLM app development workflows.

Want to learn more? You can find more Mirascope code samples on both our [documentation site](https://mirascope.com) and on [GitHub](https://github.com/mirascope/mirascope/).
