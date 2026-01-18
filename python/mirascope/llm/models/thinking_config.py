"""Configuration for extended reasoning/thinking in LLM responses."""

from typing import Literal
from typing_extensions import Required, TypedDict

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
