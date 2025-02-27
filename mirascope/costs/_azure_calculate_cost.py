"""Calculate the cost of a completion using the Azure API."""

from ..core.base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str,
) -> float | None:
    """Calculate the cost of a completion using the Azure API."""
    return None
