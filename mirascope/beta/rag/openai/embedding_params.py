from typing import Literal

from httpx import Timeout
from openai._types import Body, Headers, Query

from ..base.embedding_params import BaseEmbeddingParams


class OpenAIEmbeddingParams(BaseEmbeddingParams):
    model: str = "text-embedding-3-small"
    encoding_format: Literal["float", "base64"] | None = None
    user: str | None = None
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | Timeout | None = None
