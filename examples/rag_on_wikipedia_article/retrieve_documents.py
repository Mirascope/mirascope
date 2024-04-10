"""Retrieve documents from the Chroma vector store."""
import os

from rag_config import settings
from stores.wikipedia_chroma import WikipediaStore

from mirascope.anthropic import AnthropicCall

if settings.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class WikipediaCall(AnthropicCall):
    prompt_template = """
    SYSTEM: Answer the question based on the context.
    {context}
    USER: {question}
    """

    question: str

    @property
    def context(self):
        store = WikipediaStore()
        documents = store.retrieve(self.question)
        documents = "\n".join([doc for sublist in documents for doc in sublist])
        return documents


query = "When was caligraphy introduced to Japan and Korea"
response = WikipediaCall(question=query).call()
print(response.content)
