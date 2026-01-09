"""Base parameters for LLM providers."""

from typing import Literal, TypedDict
from typing_extensions import Required

ThinkingLevel = Literal["none", "default", "minimal", "low", "medium", "high", "max"]
"""Level of effort/reasoning to apply to thinking."""


class ThinkingConfig(TypedDict, total=False):
    """Configuration for extended reasoning/thinking in LLM responses.

    Thinking is a process where the model spends additional tokens reasoning about
    the prompt before generating a response. Providing any `ThinkingConfig` will enable
    thinking (unless it is specifically disabled via level="minimal"). Depending on
    the provider and model, thinking may always be active regardless of user settings.
    """

    level: Required[ThinkingLevel]
    """Level of effort/reasoning to apply to thinking.

    - none: Disable thinking entirely. Minimizes cost and latency.
    - default: Use the provider's default
    - minimal: Use the provider's lowest setting for reasoning
    - medium: Use a moderate amount of reasoning tokens 
    - high: Allow extensive resources for thinking
    - max: Uses as much thinking as allowed by the provider.

    Mirascope makes a best effort to apply the chosen thinking level, but exact behavior
    varies by provider and model. For example, some models may not support thinking,
    while other models may not allow disabling it.
    """

    include_summaries: bool
    """Whether to generate reasoning summaries (human readable Thoughts) from model output.
    
    Generally, providers do not return raw model thinking output, but may produce
    thought summaries. When `include_summaries` is true, these will be requested from
    the provider (if available). Otherwise, they will not be requested.
    """

    encode_thoughts_as_text: bool
    """Re-encode Thought content as text for model consumption.

    If `True`, when an `AssistantMessage` contains `Thoughts` and is passed back
    to an LLM, those `Thoughts` will be encoded as `Text`, ensuring the assistant
    can read its prior reasoning. This contrasts with provider defaults which may
    ignore prior thoughts, particularly if tool calls are not involved.

    When `True`, Mirascope will re-encode messages rather than reusing raw provider
    response content, which may disable provider-specific optimizations like cached
    reasoning tokens.

    Defaults to `False` if unset.
    """


class Params(TypedDict, total=False):
    """Common parameters shared across LLM providers.

    Note: Each provider may handle these parameters differently or not support them at all.
    Please check provider-specific documentation for parameter support and behavior.
    """

    temperature: float
    """Controls randomness in the output (0.0 to 1.0).

    Lower temperatures are good for prompts that require a less open-ended or
    creative response, while higher temperatures can lead to more diverse or
    creative results.
    """

    max_tokens: int
    """Maximum number of tokens to generate."""

    top_p: float
    """Nucleus sampling parameter (0.0 to 1.0).
    
    Tokens are selected from the most to least probable until the sum of their 
    probabilities equals this value. Use a lower value for less random responses and a
    higher value for more random responses.
    """

    top_k: int
    """Limits token selection to the k most probable tokens (typically 1 to 100).

    For each token selection step, the ``top_k`` tokens with the
    highest probabilities are sampled. Then tokens are further filtered based
    on ``top_p`` with the final token selected using temperature sampling. Use
    a lower number for less random responses and a higher number for more
    random responses.
    """

    seed: int
    """Random seed for reproducibility.
    
    When ``seed`` is fixed to a specific number, the model makes a best
    effort to provide the same response for repeated requests.

    Not supported by all providers, and does not guarantee strict reproducibility.
    """

    stop_sequences: list[str]
    """Stop sequences to end generation.
    
    The model will stop generating text if one of these strings is encountered in the
    response.
    """

    thinking: ThinkingConfig | None
    """Configuration for extended reasoning/thinking.

    Pass a `ThinkingConfig` to configure thinking behavior. The `level` field controls
    whether thinking is enabled and how much reasoning to use. Level may be one of 
    "minimal", "low", "medium", or "high". If level is unset, then thinking is enabled
    with a provider-specific default level.

    `ThinkingConfig` can also include `encode_thoughts_as_text`, which is an advanced
    feature for providing past thoughts back to the model as text content. This is
    primarily useful for making thoughts transferable when passing a conversation
    to a different model or provider than the one that generated the thinking.
    """
