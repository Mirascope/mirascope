"""
This example demonstrates how to use Mirascope with LLamaIndex to store and retrieve 
chat history.
"""
import os

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

Settings.chunk_size = 512
storage_context = StorageContext.from_defaults()
storage_context.persist(persist_dir="./data")
index = VectorStoreIndex.from_documents(
    [],
    storage_context=storage_context,
)


class Librarian(OpenAICall):
    prompt_template = """
	SYSTEM: You are the world's greatest librarian.
	MESSAGES: {history}
	USER: {question}
	"""

    question: str

    @property
    def history(self) -> list[ChatCompletionMessageParam]:
        query_engine = index.as_query_engine()
        response = query_engine.query(self.question).response
        if response != "Empty Response":
            return [{"role": "assistant", "content": response}]
        return []


librarian = Librarian(question="")
while True:
    librarian.question = input("(User): ")
    if librarian.question == "exit":
        break
    response = librarian.call()
    index.insert(Document(text=librarian.question))
    index.insert(Document(text=response.content))
    print(f"(Assistant): {response.content}")
