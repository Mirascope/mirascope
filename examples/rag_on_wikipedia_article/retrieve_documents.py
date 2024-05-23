"""Retrieve documents from the Chroma vector store."""

import os

from rag_config import settings
from stores.wikipedia_chroma import WikipediaStore

from mirascope.anthropic import AnthropicCall

# from stores.wikipedia_cohere import WikipediaStore
# from stores.wikipedia_pinecone import WikipediaStore

if settings.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
if settings.co_api_key:
    os.environ["CO_API_KEY"] = settings.co_api_key
if settings.pinecone_api_key:
    os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key


class WikipediaCall(AnthropicCall):
    prompt_template = """
    SYSTEM: 
    Answer the question based on the context.
    {context}
    USER: 
    {question}
    """

    question: str

    @property
    def context(self):
        store = WikipediaStore()
        return store.retrieve(self.question).documents


query = "When was caligraphy introduced to Japan and Korea"
response = WikipediaCall(question=query).call()
print(response.content)
