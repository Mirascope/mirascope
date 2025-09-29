"""Base parameters for LLM providers."""

from typing import TypedDict


class Params(TypedDict, total=False):
    """Common parameters shared across LLM providers.

    Note: Each provider may handle these parameters differently or not support them at all.
    Please check provider-specific documentation for parameter support and behavior.
    """

    temperature: float | None
    """Controls randomness in the output (0.0 to 1.0).

    Lower temperatures are good for prompts that require a less open-ended or
    creative response, while higher temperatures can lead to more diverse or
    creative results.
    """

    max_tokens: int | None
    """Maximum number of tokens to generate."""

    top_p: float | None
    """Nucleus sampling parameter (0.0 to 1.0).
    
    Tokens are selected from the most to least probable until the sum of their 
    probabilities equals this value. Use a lower value for less random responses and a
    higher value for more random responses.
    """

    top_k: int | None
    """Limits token selection to the k most probable tokens (typically 1 to 100).

    For each token selection step, the ``top_k`` tokens with the
    highest probabilities are sampled. Then tokens are further filtered based
    on ``top_p`` with the final token selected using temperature sampling. Use
    a lower number for less random responses and a higher number for more
    random responses.
    """

    seed: int | None
    """Random seed for reproducibility.
    
    When ``seed`` is fixed to a specific number, the model makes a best
    effort to provide the same response for repeated requests.

    Not supported by all providers, and does not guarantee strict reproducibility.
    """

    stop_sequences: list[str] | None
    """Stop sequences to end generation.
    
    The model will stop generating text if one of these strings is encountered in the
    response.
    """
