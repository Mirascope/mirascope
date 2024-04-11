"""A module for calling OpenAI's Embeddings models."""
import asyncio
from typing import ClassVar

from openai import AsyncOpenAI, OpenAI
from openai.types import CreateEmbeddingResponse, Embedding

from ..rag import BaseEmbedder
from .types import OpenAIEmbeddingParams


class OpenAIEmbedder(BaseEmbedder[CreateEmbeddingResponse]):
    embedding_params: ClassVar[OpenAIEmbeddingParams] = OpenAIEmbeddingParams()

    def embed(self, inputs: list[str]) -> list[CreateEmbeddingResponse]:
        """Call the embedder with multiple inputs"""
        embedding_responses: list[CreateEmbeddingResponse] = []
        for input in inputs:
            embedding_responses.append(self._embed(input))
        return embedding_responses

    async def embed_async(self, inputs: list[str]) -> list[CreateEmbeddingResponse]:
        """Asynchronously call the embedder with multiple inputs"""
        embedding_responses: list[CreateEmbeddingResponse] = await asyncio.gather(
            *[self._embed_async(input) for input in inputs]
        )
        return embedding_responses

    def __call__(self, input: list[str]) -> list[list[float]]:
        embeddings: list[Embedding] = [
            embedding for response in self.embed(input) for embedding in response.data
        ]
        sorted_embeddings = sorted(embeddings, key=lambda e: e.index)
        return [result.embedding for result in sorted_embeddings]

    ############################## PRIVATE METHODS ###################################

    def _embed(self, input: str) -> CreateEmbeddingResponse:
        """Call the embedder with a single input"""
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        embedding_params = self.embedding_params.model_copy(update={"input": input})
        kwargs = embedding_params.kwargs()
        return client.embeddings.create(**kwargs)

    async def _embed_async(self, input: str) -> CreateEmbeddingResponse:
        """Asynchronously call the embedder with a single input"""
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        embedding_params = self.embedding_params.model_copy(update={"input": input})
        kwargs = embedding_params.kwargs()
        return await client.embeddings.create(**kwargs)
