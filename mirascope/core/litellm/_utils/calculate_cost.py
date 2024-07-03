"""Calculate the cost of a LiteLLM API call."""

from litellm.batches.main import ModelResponse


def calculate_cost(response: ModelResponse, model: str) -> float | None:
    """Calculate the cost of a Gemini API call."""
    return None
