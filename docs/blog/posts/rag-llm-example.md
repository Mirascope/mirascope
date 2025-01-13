* **URL:** /rag-llm-example/  
* **Title:** Retrieval Augmented Generation: Examples & How to Build One  
* **Meta Description:** Understand how RAG works in AI with a real-world RAG LLM example and step-by-step instructions to build a question-answering chatbot application.

# Retrieval Augmented Generation: Examples & How to Build One

RAG is a way to make LLM responses more accurate and relevant by connecting the model to an external knowledge base that pulls in useful information to include in the prompt.

This overcomes certain limitations of relying on language models alone, as responses now include up-to-date, specific, and contextually relevant information that aren’t limited to what the model learned during its training.

It also contrasts with other techniques like semantic search, which retrieves relevant documents or snippets (based on the user’s meaning and intent) but leaves the task of understanding and contextualizing the information entirely to the user.

RAG helps reduce the risk of hallucination and offers benefits in fields where accuracy, timeliness, and specialized knowledge are highly valued, such as healthcare, science, legal, and others.

As an alternative to RAG you can [fine-tune a model](https://mirascope.com/blog/prompt-engineering-vs-fine-tuning/) to internalize domain-specific knowledge, which can result in faster and more consistent responses — as long as those tasks have specialized, fixed requirements — but it’s generally a time consuming and potentially expensive process.

Also, the model’s knowledge is static, meaning you’ll need to fine-tune the model again to update it.

RAG, in contrast, gives you up-to-date responses from a knowledge base that can be adapted on the fly.

Below, we explain how RAG works and then show you examples of using RAG for different applications. Finally, we walk you through an example of setting up a simple RAG application in Python.

For the tutorial we use LlamaIndex for data ingestion and storage, and also Mirascope, our user-friendly development library for integrating large language models with retrieval systems to implement  RAG.

## How Does RAG Work?

To send the right information (or “context”) to the LLM along with your query, you need to set up a pipeline that [orchestrates data flows](https://mirascope.com/blog/llm-orchestration/) for data ingestion, preprocessing, storage, retrieval, and response generation.

In this section, we describe the broad steps of such a pipeline but keep in mind it’s very generalized since RAG implementations can vary heavily according to project requirements.

For instance:

* Some applications (like an internal knowledge application for an insurance company) might work with proprietary documents, making confidentiality and user access controls important — so the [pipeline](https://mirascope.com/blog/llm-pipeline/) might include authentication measures, access permissions, and audit trails for secure and compliant retrieval.  
* Others, such as specialized domains like medicine or biotech, might use ontologies to organize and retrieve information from structured databases, or undergo strict quality checks (such as automated checks to ensure compliance with industry standards) before being sent to the LLM as context.

Below, we describe a generic RAG setup in three phases:

1. Ingesting documents and segmenting them into chunks  
2. Preprocessing each chunk and storing them  
3. Retrieving relevant chunks for language model generation

![][image1]

### Step 1: Data Ingestion and Segmentation

Depending on your needs, RAG can involve ingestion of both *unstructured* data like documents (e.g., PDFs, presentations, webpages, and call transcripts), images, and video recordings, and *structured* information like databases, logs, and spreadsheets.

During ingestion, documents are parsed for their useful content (e.g., headers are extracted from documents, content is extracted from HTML pages). [Frameworks](https://mirascope.com/blog/llm-frameworks/) like LlamaIndex and LangChain offer specialized loader classes for different types of documents and structured data types.

Data is next segmented into manageable chunks using text-splitting software. The size of these chunks, which are generally split according to a predetermined number of tokens or characters, has an impact on retrieval efficiency and often involves certain trade-offs.

For example, simply dividing a 2,000-word article into 200-word chunks without considering the meaning is a quick way to process text but makes it harder to retrieve relevant and coherent information, as connections between segments may be lost.

On the other hand, segmenting according to a document’s natural structure (e.g., by section, paragraph, etc.) and ensuring each chunk is a self-contained idea yields variable-sized chunks that are more complex to segment but leads to more contextually relevant retrievals.

### Step 2: Preprocessing and Storage

The goal of this step is to prepare the chunks to be represented numerically (i.e., as vectors or embeddings), that can be efficiently searched and understood by the retrieval system. 

(Note that vectors aren’t the only retrieval system that can be used in RAG, but it’s a popular option)

First, the raw text of chunks are “cleaned” to remove irrelevant elements that might interfere with the process, such as special characters.

Metadata like source information and dates might also be extracted to provide context during the generation step.

The processed text is also typically organized into an index for efficient searching and retrieval.

Finally, we use an embedding model to encode each chunk into a vector (also known as an embedding) and store them in a vector database. Companies like OpenAI and Cohere offer their own embeddings, though you can find many more in places like [Hugging Face](https://huggingface.co/mteb).

Vectors capture semantic meaning and make it easier to retrieve relevant information based on similarity even if the query doesn’t contain exact words or phrases from the document.

This similarity is typically measured by calculating the distance in vector space between query and content using metrics such as cosine similarity or Euclidean distance.

### Step 3: Retrieval and Response Generation

User queries are converted into vectors (using the original embedding model) in order to match them with information in the database.

A similarity search (using the method described in the previous section) retrieves a set of chunks with varying degrees of relevance to the query. The system also might rank these chunks and even assign a relevance score to each.

This context is then sent to the LLM, along with the user’s query. Responses might include numbered references to provide users with evidence for the information presented.

## 3 Real-World RAG Examples

Below we describe three use cases for RAG.

### Automating Email Responses

[An IT solutions provider](https://vstorm.co/case-study/rag-automation-e-mail-response-with-ai-and-llms/) has integrated a language model with their email inbox and product catalog to rapidly and accurately reply to customer questions about their products.

In the past, customers would email their questions and these would queue up in the company inbox to await a reply.

An employee would respond by first looking up the details in the company’s vast product catalog, which could be laborious as they had to sift through multitudes of products, filtering by country, category, and others to give precise answers.

These answers needed to be professional and follow company guidelines, which was time consuming to manually write up and send.

The company now uses RAG to both encode customer questions and use similarity searches to compare these against entries in their product database. The system retrieves the relevant entries and forwards these, along with the original question, to the LLM for a personalized response.

It uses two popular frameworks: LlamaIndex for preprocessing product catalog details and [LangChain](https://mirascope.com/blog/langchain-rag/) for overall data orchestration from query processing to sending the response back to the customer.

### Routing Support Calls

[A call center has implemented RAG](https://vstorm.co/case-study/llm-powered-voice-assistant-for-call-center/) to verify incoming customer calls and route these to the correct department (or to escalate them).

Instead of answering questions, the system uses past call records and customer emails as a knowledge base, which provides a basis for making informed decisions about how to handle customer queries.

This is in contrast to the old way of manually handling calls, which used to lead to delays in responses and wasn’t very scalable as the customer base grew, especially across countries and languages.

The current RAG implementation handles calls in real time and uses question-answering capabilities to further improve responses.

When the call center receives an inbound call, an LLM\-powered voice assistant initiates the process by verifying the caller’s identity and determining the purpose of their call.

It then processes the caller’s query in real time, using language models to analyze and understand the request. Once the type of query is identified, the system automatically routes the call to the appropriate department or escalates it if higher-level intervention is needed.

The system supports multiple languages and runs 24/7.

### Onboarding New Hires

A company can use RAG as an internal onboarding chatbot that consolidates training materials scattered across internal wikis, shared drives, and manuals to reduce the time that trainers spend on repetitive Q\&A.

Such materials can be organized as a [knowledge graph](https://mirascope.com/blog/how-to-build-a-knowledge-graph/) — whose nodes are stored in a vector database as embeddings, and retrieved via semantic search — allowing the system to deeply understand the relationship between nodes and the context of the query.

The grounding of RAG\-generated responses in authoritative documents minimizes bias and provides consistent, reliable guidance. Moreover, the system’s knowledge base can be continuously refreshed to remain up to date according to the changing needs of the organization.

With RAG handling routine and repetitive questions from users, trainers are free to focus on strategic mentorship and more complex aspects of onboarding, ultimately improving the overall experience of new employees and trainers.

## Building a RAG\-Based Chatbot for Question-Answering

Below, we build an example RAG system that answers questions about Alan Turing’s scientific papers.

We’ll use two libraries for our implementation:

* LlamaIndex for preprocessing and information retrieval  
* Mirascope for simplifying [prompt engineering](https://mirascope.com/blog/advanced-prompt-engineering/) and handling the response

LlamaIndex is a framework designed to handle large datasets and provides [tools](https://mirascope.com/blog/llm-tools/) for loading and preprocessing documents from a variety of data sources. It also converts these into embeddings for storage and indexing.

Mirascope is a library for interacting with language models in plain Python that provides developer-agnostic tools to optimize prompts, manage state, and [validate outputs](https://mirascope.com/blog/langchain-structured-output/).

In the steps below, we use LlamaIndex to ingest, preprocess, and store Turing’s scientific papers, as well as to instantiate a retriever object to find relevant papers for our queries. 

We then use Mirascope to send both the retrieved context and our queries to the LLM.

### Set Up the Environment

We import LlamaIndex modules for loading, indexing, and vectorizing the papers.

From Mirascope, we import modules for interfacing with the OpenAI API (setting up LLM calls) and for constructing prompts:

```py
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from mirascope.core import openai, prompt_template
```

Note that:

* We’ll use LlamaIndex’s `SimpleDirectoryReader` for data ingestion and preprocessing, and `VectorStoreIndex` for embedding and storage  
* `BaseRetriever` is the class from which we’ll instantiate the retriever object  
* We also import Mirascope’s modules for working with OpenAI and for formulating prompts

### 1\. Load and Preprocess the Documents

We load the papers and preprocess them by splitting them into chunks and vectorizing them:

```py
# Load documents and build index
documents = SimpleDirectoryReader("./alan_turing_papers").load_data()
retriever = VectorStoreIndex.from_documents(documents).as_retriever()
```

Here, `SimpleDirectoryReader` loads an entire subdirectory containing PDFs (this class also manages other formats like CSV, Microsoft Word documents, Jupytr notebooks, MP3s, and more), and extracts the text and metadata from each file.

We next use `VectorStoreIndex` to build a searchable index of the retrieved documents we’ve loaded by splitting them into chunks and preprocessing them (via `from_documents`).

Once these chunks (or “nodes” as [LlamaIndex](https://mirascope.com/blog/llamaindex-vs-langchain/) refers to them) are created, `VectorStoreIndex` uses a default embedding model to vectorize and store these in memory. (You can also use a separate vector store such as Pinecone.)

Lastly, we instantiate a retriever object to fetch relevant content given a user query using `.from_retriever`.

### 2\. Query and Retrieve Context

We define a function to query our Alan Turing library:

```py
# Define the function to ask "Alan Turing" a question
@openai.call("gpt-4o-mini", call_params={"temperature": 0.6})
@prompt_template("""
    SYSTEM:
    Your task is to respond to the user as though you are Alan Turing, drawing on ideas from 
    "Computing Machinery and Intelligence."

    Here are some excerpts from Turing’s paper relevant to the user query.
    Use them as a reference for how to respond.

    <excerpts>
    {excerpts}
    </excerpts>
    """)
def ask_alan_turing(query: str, retriever: BaseRetriever) -> openai.OpenAIDynamicConfig:
    """Retrieves excerpts from 'Computing Machinery and Intelligence' relevant to `query` and generates a response."""
    excerpts = [node.get_content() for node in retriever.retrieve(query)]
    return {"computed_fields": {"excerpts": excerpts}}
```

The `ask_alan_turing` function:

* Receives a query string and our retriever object, and returns a dictionary containing `excerpts` from the set of scientific papers.  
* Calls `retriever.retrieve(query)` to search the vector store for the most semantically relevant excerpts of Turing’s papers that relate to the user’s query.  
* Fetches and processes excerpts at runtime (to insert in the [prompt template](https://mirascope.com/blog/langchain-prompt-template/)) via `OpenAIDynamicConfig` and computed fields.

We add two Mirascope decorators to turn the function into an LLM API call:

* The `openai.call` decorator makes calls more readable by turning any Python function into an LLM call and is provider agnostic: we could’ve instead written, e.g., `anthropic.call`, `gemini.call`, `vertex.call` or any of a number of others, with minimal code adjustments.   
* Mirascope’s `prompt_template` decorator enables defining the prompt as a template that instructs the model to respond as if it’s Alan Turing and injects a list of the retrieved excerpts.

Both of these decorators, when added to any function, illustrate the best practice of colocation of prompts and calls, which makes the code eminently more readable as the logic for preparing input data, [building prompts](https://mirascope.com/blog/llm-prompt/), and LLM invocation is centralized in a single place.

### 3\. Generate a Response from the Query

Finally, the user asks a question about Turing’s research papers:

```py
# Get the user's query and ask "Alan Turing"
query = input("(User): ")
response = ask_alan_turing(query, retriever)
print(response.content)
# > How does Turing address the objections to the idea that machines can think?
> This question delves into the various arguments Turing discusses in his paper, such as the theological objection, the "heads in the sand" objection, ...
```

The code captures the user’s query and calls `ask_alan_turing`, which retrieves the relevant excerpts from the cache of Turing’s papers in `documents`. Both the query and the excerpts are then sent to the model as a response.

## Optimize Your RAG Pipeline

Take the complexity out of implementing retrieval augmented generation with Mirascope’s native Python\-based library. It lets you use RAG in your question-answering systems, allowing you to build smarter, more data-aware [LLM applications](https://mirascope.com/blog/llm-applications/) that answer questions with accuracy at scale.

Want to learn more? You can find more Mirascope code samples both on our [website](https://mirascope.com/WELCOME) and on our [GitHub page](https://github.com/mirascope/mirascope).

[image1]: <data:image/png;base64,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>
