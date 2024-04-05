import os
import time
import uuid

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.openai import OpenAIEmbedder
from mirascope.openai.types import OpenAIEmbeddingParams

load_dotenv(".env")

home_dir = os.path.expanduser("~")
raw_documents = TextLoader(f"{home_dir}/Desktop/sotu.txt").load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)


# db = Chroma.from_documents(
#     documents,
#     OpenAIEmbeddings(
#         openai_api_key="sk-"
#     ),
# )

# def text_splitter(data, chunk_params: ChunkParam(chunk_size=500)) -> list[str]:
#     text_splitter = CharacterTextSplitter(
#         chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
#     )
#     return text_splitter.split_documents(self.data)


# def regex_splitter(
#     data, chunk_params: BaseChunkingParams = BaseChunkingParams()
# ) -> list[str]:
#     ...


# @chunk_fn(chunk)
# class BaseChunker(BaseModel):
#     chunking_params: ClassVar[BaseChunkingParams] = BaseChunkingParams()
#     data: list[str]

#     # def chunk...


# with open("...") as file:
#     data = file.read()
#     my_name = MyName()
#     my_name.add_documents(data)
#     # chunked_data = chunker.chunk(data)
#     # embeded_data = embedder.embed(chunked_data)
#     # my_name._index.upsert(embeded_data)

# local
# mirascope rag my_name --dir ./documents

# embedding_vector = OpenAIEmbeddings(
#     openai_api_key="sk-"
# ).embed_query(query)


# query = "What did the president say about Ketanji Brown Jackson"
def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 0) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks


class Embedder(OpenAIEmbedder):
    api_key: str = ""


class MyName(ChromaVectorStore):
    embedder: OpenAIEmbedder = Embedder()
    index_name: str = "test"


with open(f"{home_dir}/Desktop/sotu.txt") as file:
    # LOAD DATA
    data = file.read()
    split_text = split_text(data)
    my_name = MyName()
    embeddings = my_name.embedder.create_embeddings(split_text)
    data = [embedding.data[0].embedding for embedding in embeddings]
    ids = [str(uuid.uuid4()) for _ in embeddings]
    my_name.add_documents(embeddings=data, ids=ids)

    # QUERY
    query = "What did the president say about Ketanji Brown Jackson"
    embedding = my_name.embedder.embed(query)
    documents = my_name.get_documents(query_embeddings=embedding.data[0].embedding)
    print(documents)
