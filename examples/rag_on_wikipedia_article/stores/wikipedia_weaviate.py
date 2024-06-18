from mirascope.weaviate import WeaviateVectorStore
from mirascope.weaviate.types import WeaviateSettings, WeaviateParams
from mirascope.rag import TextChunker
import weaviate.classes as wvc
import os


class WikipediaStore(WeaviateVectorStore):
    index_name = "wikipedia"
    client_settings = WeaviateSettings(
        headers={"X-OpenAI-Api-Key": str(os.getenv("OPENAI_API_KEY"))}
    )
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)

    vectorstore_params = WeaviateParams(
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai()
    )
