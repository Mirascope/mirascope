from typing import Literal

from cohere.types import EmbedByTypeResponseEmbeddings, EmbedResponse
from pydantic import SkipValidation

from ..base.embedding_response import BaseEmbeddingResponse


class CohereEmbeddingResponse(BaseEmbeddingResponse[SkipValidation[EmbedResponse]]):
    """A convenience wrapper around the Cohere `EmbedResponse` response."""

    embedding_type: Literal["float", "int8", "uint8", "binary", "ubinary"] | None = None

    @property
    def embeddings(
        self,
    ) -> list[list[float]] | list[list[int]] | None:
        """Returns the embeddings"""
        if self.response.response_type == "embeddings_floats":
            return self.response.embeddings
        else:
            embedding_type = self.embedding_type
            if embedding_type == "float":
                embedding_type = "float_"

            # TODO: Update to model_dump when Cohere updates to Pydantic v2
            embeddings_by_type: EmbedByTypeResponseEmbeddings = self.response.embeddings
            embedding_dict = embeddings_by_type.dict()
            return embedding_dict.get(str(embedding_type), None)
