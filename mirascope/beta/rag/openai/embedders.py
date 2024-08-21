"""A module for calling OpenAI's Embeddings models."""

import asyncio
import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import ClassVar

from openai import AsyncOpenAI, OpenAI
from openai.types import Embedding
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage

from ..base.embedders import BaseEmbedder
from .embedding_params import OpenAIEmbeddingParams
from .embedding_response import OpenAIEmbeddingResponse


class OpenAIEmbedder(BaseEmbedder[OpenAIEmbeddingResponse]):
    """OpenAI Embedder

    Example:

    ```python
    import os
    from mirascope.beta.rag.openai import OpenAIEmbedder

    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

    openai_embedder = OpenAIEmbedder()
    response = openai_embedder.embed(["your text to embed"])
    print(response)
    ```
    """

    dimensions: int | None = 1536
    embed_batch_size: int | None = 20
    max_workers: int | None = 64
    embedding_params: ClassVar[OpenAIEmbeddingParams] = OpenAIEmbeddingParams(
        model="text-embedding-3-small"
    )
    _provider: ClassVar[str] = "openai"

    def embed(self, inputs: list[str]) -> OpenAIEmbeddingResponse:
        """Call the embedder with multiple inputs"""
        if self.embed_batch_size is None:
            return self._embed(inputs)

        input_batches = [
            inputs[i : i + self.embed_batch_size]
            for i in range(0, len(inputs), self.embed_batch_size)
        ]

        embedding_responses: list[OpenAIEmbeddingResponse] = list(
            ThreadPoolExecutor(self.max_workers).map(
                lambda inputs: self._embed(inputs),
                input_batches,
            )
        )
        return self._merge_batch_embeddings(embedding_responses)

    async def embed_async(self, inputs: list[str]) -> OpenAIEmbeddingResponse:
        """Asynchronously call the embedder with multiple inputs"""
        if self.embed_batch_size is None:
            return await self._embed_async(inputs)

        input_batches = [
            inputs[i : i + self.embed_batch_size]
            for i in range(0, len(inputs), self.embed_batch_size)
        ]
        embedding_responses: list[OpenAIEmbeddingResponse] = await asyncio.gather(
            *[self._embed_async(inputs) for inputs in input_batches]
        )
        return self._merge_batch_embeddings(embedding_responses)

    def __call__(self, input: list[str]) -> list[list[float]]:
        """Call the embedder with a input

        Chroma expects parameter to be `input`.
        """
        embedding_response = self.embed(input)

        return embedding_response.embeddings

    ############################## PRIVATE METHODS ###################################

    def _embed(self, inputs: list[str]) -> OpenAIEmbeddingResponse:
        """Call the embedder with a single input"""
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        kwargs = self.embedding_params.kwargs()
        if self.embedding_params.model != "text-embedding-ada-002":
            kwargs["dimensions"] = self.dimensions
        start_time = datetime.datetime.now().timestamp() * 1000
        embeddings = client.embeddings.create(input=inputs, **kwargs)
        return OpenAIEmbeddingResponse(
            response=embeddings,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    async def _embed_async(self, inputs: list[str]) -> OpenAIEmbeddingResponse:
        """Asynchronously call the embedder with a single input"""
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        kwargs = self.embedding_params.kwargs()
        if self.embedding_params.model != "text-embedding-ada-002":
            kwargs["dimensions"] = self.dimensions
        start_time = datetime.datetime.now().timestamp() * 1000
        embeddings = await client.embeddings.create(input=inputs, **kwargs)
        return OpenAIEmbeddingResponse(
            response=embeddings,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    def _merge_batch_embeddings(
        self, openai_embeddings: list[OpenAIEmbeddingResponse]
    ) -> OpenAIEmbeddingResponse:
        """Merge a batch of embeddings into a single embedding"""
        embeddings: list[Embedding] = []
        usage = Usage(
            prompt_tokens=0,
            total_tokens=0,
        )
        start_time = float("inf")
        end_time: float = 0.0
        i: int = 0
        for openai_embedding in openai_embeddings:
            for embedding in openai_embedding.response.data:
                embedding.index = i
                embeddings.append(embedding)
                i += 1
            usage.prompt_tokens += openai_embedding.response.usage.prompt_tokens
            usage.total_tokens += openai_embedding.response.usage.total_tokens
            start_time = min(start_time, openai_embedding.start_time)
            end_time = max(end_time, openai_embedding.end_time)
        create_embedding_response = CreateEmbeddingResponse(
            data=embeddings,
            model=openai_embeddings[0].response.model,
            object=openai_embeddings[0].response.object,
            usage=usage,
        )
        return OpenAIEmbeddingResponse(
            response=create_embedding_response,
            start_time=start_time,
            end_time=end_time,
        )
