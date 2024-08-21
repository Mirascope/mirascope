from openai.types import Embedding
from openai.types.create_embedding_response import CreateEmbeddingResponse

from ..base.embedding_response import BaseEmbeddingResponse


class OpenAIEmbeddingResponse(BaseEmbeddingResponse[CreateEmbeddingResponse]):
    """A convenience wrapper around the OpenAI `CreateEmbeddingResponse` response."""

    @property
    def embeddings(self) -> list[list[float]]:
        """Returns the raw embeddings."""
        embeddings_model: list[Embedding] = list(self.response.data)
        return [embedding.embedding for embedding in embeddings_model]
