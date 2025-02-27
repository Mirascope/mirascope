"""Calculate the cost of a completion using the Bedrock API."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str,
) -> float | None:
    """Calculate the cost of a completion using the Bedrock API."""
    # NOTE: We are currently investigating a dynamic approach to determine costs
    # for Bedrock models. This is needed due to the large number of models
    # available through Bedrock, making it impractical to hardcode all pricing
    # information in this initial implementation.
    return None
