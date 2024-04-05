from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, ClassVar, Coroutine

from openai import AsyncOpenAI, OpenAI
from openai.types import CreateEmbeddingResponse

from ..base import BaseEmbedder
from .types import OpenAIEmbeddingParams


class OpenAIEmbedder(BaseEmbedder[CreateEmbeddingResponse]):
    embedding_params: ClassVar[OpenAIEmbeddingParams] = OpenAIEmbeddingParams()

    def create_embeddings(self, inputs: list[str]) -> list[CreateEmbeddingResponse]:
        """Call the embedder with multiple inputs"""
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.embed, input) for input in inputs]
            return [future.result() for future in as_completed(futures)]

    def embed(self, input: str) -> CreateEmbeddingResponse:
        """Call the embedder with a single input"""
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        embedding_params = self.embedding_params.model_copy(update={"input": input})
        kwargs = embedding_params.kwargs()
        return client.embeddings.create(**kwargs)

    async def create_embeddings_async(
        self, inputs: list[str]
    ) -> list[CreateEmbeddingResponse]:
        """Asynchronously call the embedder with multiple inputs"""
        async with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.embed_async, input) for input in inputs]
            return [await future.result() for future in as_completed(futures)]

    async def embed_async(self, input: str) -> CreateEmbeddingResponse:
        """Asynchronously call the embedder with a single input"""
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        return await client.embeddings.create(input=input, **self.embedding_params)
