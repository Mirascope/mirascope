"""Calculate the cost of a Litellm call."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str,
) -> float | None:
    """Calculate the cost of a Litellm call."""
    return metadata.cost
