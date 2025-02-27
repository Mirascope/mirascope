"""Calculate the cost of a Litellm call."""

from litellm.cost_calculator import completion_cost

from ..core.base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str,
) -> float | None:
    """Calculate the cost of a Litellm call."""
    return completion_cost(metadata.litellm_response)
