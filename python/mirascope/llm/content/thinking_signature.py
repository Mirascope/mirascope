"""The `ThinkingSignature` content class.

The `ThinkingSignature` has an id or signature that identifies the model's
reasoning. These strings are not interpretable, but serve as references that can be
passed back to the provider that generated them, in order to keep the reasoning tokens
in context for future responses.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..clients import ModelId, Provider


@dataclass(kw_only=True)
class ThinkingSignature:
    """Provider-specific signature that references the model's reasoning process.

    When passed back to the provider that generated it, it can keep the model's
    private reasoning process in context. Depending on the model, the signature may
    correlate with zero or more `Thought`s.
    """

    type: Literal["thinking_signature"] = "thinking_signature"

    signature: str
    """The provider-specific opaque signature or id of the model's thinking."""

    encrypted_reasoning: str | None
    """Encrypted reasoning tokens, if any.
    
    When present, these are encrypted contents of the model's entire reasoning process.
    They are included on the `ThinkingSignature` rather than as `Thought`s because they
    are not human-readable, but rather opaque data to be passed back to the provider.

    They are necessary to maintain reasoning context if the provider is not retaining
    the reasoning tokens on its servers (e.g. due to a zero data retention policy).
    """

    provider: "Provider"
    """The provider that generated this `ThinkingSignature`."""

    model_id: "ModelId"
    """The identifier of the model that generated this `ThinkingSignature`."""


@dataclass(kw_only=True)
class ThinkingSignatureStartChunk:
    """Streamed chunk containing a `ThinkingSignature`"""

    type: Literal["thinking_signature_start_chunk"] = "thinking_signature_start_chunk"

    content_type: Literal["thinking_signature"] = "thinking_signature"
    """The type of content reconstructed by this chunk."""

    provider: "Provider"
    """The provider that generated this `ThinkingSignature`."""

    model_id: "ModelId"
    """The identifier of the model that generated this `ThinkingSignature`."""


@dataclass(kw_only=True)
class ThinkingSignatureChunk:
    """Streamed chunk containing a `ThinkingSignature`"""

    type: Literal["thinking_signature_chunk"] = "thinking_signature_chunk"

    content_type: Literal["thinking_signature"] = "thinking_signature"
    """The type of content reconstructed by this chunk."""

    signature_delta: str | None
    """Incremental signature data, if any."""

    encrypted_reasoning_delta: str | None
    """Incremental encrypted contents, if any."""


@dataclass(kw_only=True)
class ThinkingSignatureEndChunk:
    """Streamed chunk containing a `ThinkingSignature`"""

    type: Literal["thinking_signature_end_chunk"] = "thinking_signature_end_chunk"

    content_type: Literal["thinking_signature"] = "thinking_signature"
    """The type of content reconstructed by this chunk."""
