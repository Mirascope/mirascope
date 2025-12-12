"""Base parameters for LLM providers."""

from typing import TypedDict


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

    thinking: bool
    """Configures whether the model should use thinking.
    
    Thinking is a process where the model spends additional tokens thinking about the
    prompt before generating a response. You may configure thinking either by passing
    a bool to enable or disable it.

    If `params.thinking` is `True`, then thinking and thought summaries will be enabled
    (if supported by the model/provider), with a default budget for thinking tokens.

    If `params.thinking` is `False`, then thinking will be wholly disabled, assuming
    the model allows this (some models, e.g. `google:gemini-2.5-pro`, do not allow
    disabling thinking).

    If `params.thinking` is unset (or `None`), then we will use provider-specific default
    behavior for the chosen model.
    """

    encode_thoughts_as_text: bool
    """Configures whether `Thought` content should be re-encoded as text for model consumption.
    
    If `True`, then when an `AssistantMessage` contains `Thoughts` and is being passed back
    to an LLM, those `Thoughts` will be encoded as `Text`, so that the assistant can read
    those thoughts. That ensures the assistant has access to (at least the summarized output of)
    its reasoning process, and contrasts with provider default behaviors which may ignore
    prior thoughts, particularly if tool calls are not involved.

    When `True`, we will always re-encode Mirascope messages being passed to the provider,
    rather than reusing raw provider response content. This may disable provider-specific
    behavior like cached reasoning tokens.

    If `False`, then `Thoughts` will not be encoded as text, and whether reasoning context
    is available to the model depends entirely on the provider's behavior. 

    Defaults to `False` if unset.
    """
