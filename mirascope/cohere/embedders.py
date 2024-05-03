"""A module for calling OpenAI's Embeddings models."""
import datetime
from typing import ClassVar, Optional, Union

from cohere import AsyncClient, Client

from ..rag import BaseEmbedder
from .types import CohereEmbeddingParams, CohereEmbeddingResponse


class CohereEmbedder(BaseEmbedder[CohereEmbeddingResponse]):
    """Cohere Embedder

    model                           max_dimensions
    embed-english-v3.0              1024
    embed-multilingual-v3.0         1024
    embed-english-light-v3.0        384
    embed-multilingual-light-v3.0   384
    embed-english-v2.0              4096
    embed-english-light-v2.0        1024
    embed-multilingual-v2.0         768

    Example:

    ```python
    import os
    from mirascope.cohere import CohereEmbedder

    os.environ["CO_API_KEY"] = "YOUR_COHERE_API_KEY"

    cohere_embedder = CohereEmbedder()
    response = cohere_embedder.embed(["your text to embed"])
    print(response)
    ```
    """

    dimensions: Optional[int] = 1024
    embedding_params: ClassVar[CohereEmbeddingParams] = CohereEmbeddingParams(
        model="embed-english-v3.0"
    )

    def embed(self, inputs: list[str]) -> CohereEmbeddingResponse:
        """Call the embedder with multiple inputs"""
        co = Client(api_key=self.api_key, base_url=self.base_url)
        embedding_type = (
            self.embedding_params.embedding_types[0]
            if self.embedding_params.embedding_types
            else None
        )
        start_time = datetime.datetime.now().timestamp() * 1000
        embed = co.embed
        if self.embedding_params.logfire:
            embed = self.embedding_params.logfire(
                co.embed, "cohere", response_type=CohereEmbeddingResponse
            )  # pragma: no cover
        response = embed(texts=inputs, **self.embedding_params.kwargs())
        return CohereEmbeddingResponse(
            response=response,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            embedding_type=embedding_type,
        )

    async def embed_async(self, inputs: list[str]) -> CohereEmbeddingResponse:
        """Asynchronously call the embedder with multiple inputs"""
        co = AsyncClient(api_key=self.api_key, base_url=self.base_url)
        embedding_type = (
            self.embedding_params.embedding_types[0]
            if self.embedding_params.embedding_types
            else None
        )
        start_time = datetime.datetime.now().timestamp() * 1000
        embed = co.embed
        if self.embedding_params.logfire_async:
            embed = self.embedding_params.logfire_async(
                co.embed,
                "cohere",
                response_type=None,  # note: no content to extract, so we set to `None`
            )  # pragma: no cover
        response = await embed(texts=inputs, **self.embedding_params.kwargs())
        return CohereEmbeddingResponse(
            response=response,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            embedding_type=embedding_type,
        )

    def __call__(
        self, input: list[str]
    ) -> Optional[Union[list[list[float]], list[list[int]]]]:
        """Call the embedder with a input

        Chroma expects parameter to be `input`.
        """
        response = self.embed(input)
        embeddings = response.embeddings
        return embeddings
