# Local Chat with Codebase

In this recipe, we will be using all Open Source Software to build a local ChatBot that has access to some documentation. We will be using Mirascope documentation in this example, but this should work on all types of documents. Also note that we will be using a smaller Llama 3.1 8B so the results will not be as impressive as larger models. Later, we will take a look at how OpenAI's GPT compares with Llama.

## Setup

```python
pip install llama-index, llama-index-llms-ollama, llama-index-embeddings-huggingface
```

[Ollama](https://github.com/ollama/ollama)

For this setup, we use Ollama but vLLM will also work.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Agents](../../learn/agents.md)

## Configuration

```python
from llama_index.core import Settings
Settings.llm = Ollama(model="llama3.1")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
```

We will be using LlamaIndex for RAG, and setting up the proper models we will be using for Re-ranking and the Embedding model.

## Store Embeddings

The first step is to grab our docs and embed them into a vectorstore. In this recipe, we will be storing our vectorstore locally, but using Pinecone or other cloud vectorstore providers will also work.

```python
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

documents = SimpleDirectoryReader("PATH/TO/YOUR/DOCS").load_data()
vector_store = SimpleVectorStore()
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
index.storage_context.persist()
```

## Load Embeddings

After we saved our embeddings, we can use the below code to retrieve it and load in memory:

```python
from llama_index.core import load_index_from_storage
from llama_index.core.storage import StorageContext

storage_context = StorageContext.from_defaults(persist_dir="storage")
loaded_index = load_index_from_storage(storage_context)
query_engine = loaded_index.as_query_engine()
```

## Code

We need to update LlamaIndex `default_parse_choice_select_answer_fn` for Llama 3.1. You may need to update the `custom_parse_choice_select_answer_fn` depending on which model you are using. Adding re-ranking is extremely important to get better quality retrievals so the LLM can make better context-aware answers.

We will be creating an Agent that will read Mirascope documentation called MiraBot which will answer questions regarding Mirascope docs.

```python
import re

from mirascope import openai, prompt_template


def custom_parse_choice_select_answer_fn(
    answer: str, num_choices: int, raise_error: bool = False
) -> tuple[list[int], list[float]]:
    """Custom parse choice select answer function."""
    answer_lines = answer.split("\n")
    answer_nums = []
    answer_relevances = []
    for answer_line in answer_lines:
        line_tokens = answer_line.split(",")
        if len(line_tokens) != 2:
            if not raise_error:
                continue
            else:
                raise ValueError(
                    f"Invalid answer line: {answer_line}. "
                    "Answer line must be of the form: "
                    "answer_num: <int>, answer_relevance: <float>"
                )
        split_tokens = line_tokens[0].split(":")
        if (
            len(split_tokens) != 2
            or split_tokens[1] is None
            or not split_tokens[1].strip().isdigit()
        ):
            continue
        answer_num = int(line_tokens[0].split(":")[1].strip())
        if answer_num > num_choices:
            continue
        answer_nums.append(answer_num)
        # extract just the first digits after the colon.
        _answer_relevance = re.findall(r"\d+", line_tokens[1].split(":")[1].strip())[0]
        answer_relevances.append(float(_answer_relevance))
    return answer_nums, answer_relevances

def get_documents(query: str) -> str:
    """The get_documents tool that retrieves Mirascope documentation based on the
    relevance of the query"""
    query_engine = loaded_index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=[
            LLMRerank(
                choice_batch_size=5,
                top_n=2,
                parse_choice_select_answer_fn=custom_parse_choice_select_answer_fn,
            )
        ],
        response_mode="tree_summarize",
    )

    response = query_engine.query(query)
    if isinstance(response, Response):
        return response.response or "No documents found."
    return "No documents found."

class MirascopeBot(BaseModel):
    @openai.call(
        model="llama3.1",
        client=OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
    )
    @prompt_template(
        """
        SYSTEM:
        You are an AI Assistant that is an expert at answering questions about Mirascope.
        Here is the relevant documentation to answer the question.

        Context:
        {context}

        USER:
        {question}
        """
    )
    def _step(self, context: str, question: str): ...

    def _get_response(self, question: str):
        context = get_documents(question)
        answer = self._step(context, question)
        print("(Assistant):", answer.content)
        return

    def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            self._get_response(question)

MirascopeBot().run()
# (User): How do I make an LLM call using Mirascope?
# (Assistant): To make an LLM (Large Language Model) call using Mirascope, you can use the `call` decorator provided by Mirascope.
#
# Here are the basic steps:
#
# 1. Import the `call` decorator from Mirascope.
# 2. Define a function that takes any number of arguments and keyword arguments. This will be the function that makes the LLM call.
# 3. Prepend this function definition with the `@call` decorator, specifying the name of the model you want to use (e.g., "gpt-4o").
# 4. Optionally, pass additional keyword arguments to customize the behavior of the LLM call.
#
# For example:
# ```python
# from mirascope import call
#
# @click('gpt-4o')
# def greet(name: str) -> dict:
#    return {'greeting': f"Hello, {name}!"}
# ```
# In this example, `greet` is the function that makes an LLM call to a GPT-4o model. The `@call('gpt-4o')` decorator turns this function into an LLM call.
```

!!! note

    Using gpt-4o gives better results than using Ollama for LLMRank and the LLM call.

Let us replace the LLM Rerank and LLM call with OpenAI GPT 4o-mini and see our results

```python
# (User): How do I make an LLM call using Mirascope?
# (Assistant): Every provider we support has a corresponding `call` decorator for **turning a function into a call to an LLM**. You can use this decorator on any function definition to make an LLM call, like so:

# ```python
# from mirascope.core import openai
#
# @openai.call("gpt-4o")
# def recommend_book(genre: str):
#     """Recommend a {genre} book."""
#    
# response = recommend_book("fantasy")
# print(response)
# ```
#
# This code snippet shows how to make an LLM call with Mirascope using the `call` decorator. The `@openai.call("gpt-4o")` line above the function definition tells Mirascope to use the "gpt-4o" model for this function, effectively turning it into a call to the Large Language Model (LLM).
```

!!! tip "Additional Real-World Applications"

    - **Improved Chat Application**: Maintain the most current documentation by storing it in a vector database or using a tool to retrieve up-to-date information in your chat application
    - **Code Autocomplete**: Integrate the vector database with the LLM to generate accurate, context-aware code suggestions."
    - **Interactive Internal Knowledge Base**: Index company handbooks and internal documentation to enable instant, AI-powered Q&A access.

When adapting this recipe, consider:

    - Experiment with different model providers and version for quality.
    - Use a different Reranking prompt as that impacts the quality of retrieval
    - Implement a feedback loop so the LLM hallucinates less frequently. 
