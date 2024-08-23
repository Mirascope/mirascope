import re

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.base.response.schema import Response
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from openai import OpenAI
from pydantic import BaseModel

from mirascope.core import openai, prompt_template

Settings.llm = Ollama(model="llama3.1")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# ONE TIME SETUP
documents = SimpleDirectoryReader("PATH/TO/YOUR/DOCS").load_data()
vector_store = SimpleVectorStore()
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
index.storage_context.persist()
# END ONE TIME SETUP

storage_context = StorageContext.from_defaults(persist_dir="storage")
loaded_index = load_index_from_storage(storage_context)
query_engine = loaded_index.as_query_engine()


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
