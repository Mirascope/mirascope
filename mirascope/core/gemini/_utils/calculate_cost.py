"""Calculate the cost of a Gemini API call."""

from google.generativeai.types import GenerateContentResponse  # type: ignore


def calculate_cost(response: GenerateContentResponse, model: str) -> float | None:
    """Calculate the cost of a Gemini API call."""
    return None
