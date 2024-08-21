from collections.abc import Sequence
from typing import Any, Literal, NotRequired

from typing_extensions import TypedDict

from ..base.embedding_params import BaseEmbeddingParams


class RequestOptions(TypedDict):
    """Redefining their class to use `typing_extensions.TypedDict` for Pydantic."""

    timeout_in_seconds: NotRequired[int]
    max_retries: NotRequired[int]
    additional_headers: NotRequired[dict[str, Any]]
    additional_query_parameters: NotRequired[dict[str, Any]]
    additional_body_parameters: NotRequired[dict[str, Any]]


class CohereEmbeddingParams(BaseEmbeddingParams):
    model: str = "embed-english-v3.0"
    input_type: Literal[
        "search_document", "search_query", "classification", "clustering"
    ] = "search_query"
    embedding_types: (
        Sequence[Literal["float", "int8", "uint8", "binary", "ubinary"]] | None
    ) = None
    truncate: Literal["none", "end", "start"] | None = "end"
    request_options: RequestOptions | None = None
    batching: bool | None = True
