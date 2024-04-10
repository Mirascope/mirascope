"""Add documents to the Chroma vector store."""
import os

from rag_config import settings
from stores.wikipedia_chroma import WikipediaStore

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(f"{current_dir}/semi_cursive_script_wikipedia.txt") as file:
    data = file.read()
    store = WikipediaStore()
    store.add(data)
