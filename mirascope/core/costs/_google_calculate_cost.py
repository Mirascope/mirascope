"""Calculate the cost of a Gemini API call."""

from ..base.types import CostMetadata

# Standard Gemini API pricing table
GEMINI_API_PRICING: dict[str, dict[str, float]] = {
    "gemini-2.0-pro": {
        "prompt_short": 0.000_001_25,
        "completion_short": 0.000_005,
        "prompt_long": 0.000_002_5,
        "completion_long": 0.000_01,
        "cached": 0.000_000_625,
    },
    "gemini-2.0-pro-preview-1206": {
        "prompt_short": 0.000_001_25,
        "completion_short": 0.000_005,
        "prompt_long": 0.000_002_5,
        "completion_long": 0.000_01,
        "cached": 0.000_000_625,
    },
    "gemini-2.0-flash": {
        "prompt_short": 0.000_000_10,
        "completion_short": 0.000_000_40,
        "prompt_long": 0.000_000_10,
        "completion_long": 0.000_000_40,
        "cached": 0.000_000_037_5,
    },
    "gemini-2.0-flash-latest": {
        "prompt_short": 0.000_000_10,
        "completion_short": 0.000_000_40,
        "prompt_long": 0.000_000_10,
        "completion_long": 0.000_000_40,
        "cached": 0.000_000_037_5,
    },
    "gemini-2.0-flash-001": {
        "prompt_short": 0.000_000_10,
        "completion_short": 0.000_000_40,
        "prompt_long": 0.000_000_10,
        "completion_long": 0.000_000_40,
        "cached": 0.000_000_037_5,
    },
    "gemini-2.0-flash-lite": {
        "prompt_short": 0.000_000_075,
        "completion_short": 0.000_000_30,
        "prompt_long": 0.000_000_075,
        "completion_long": 0.000_000_30,
        "cached": 0.000_000_037_5,
    },
    "gemini-2.0-flash-lite-preview-02-05": {
        "prompt_short": 0.000_000_075,
        "completion_short": 0.000_000_30,
        "prompt_long": 0.000_000_075,
        "completion_long": 0.000_000_30,
        "cached": 0.000_000_037_5,
    },
    "gemini-1.5-pro": {
        "prompt_short": 0.000_001_25,
        "completion_short": 0.000_005,
        "prompt_long": 0.000_002_5,
        "completion_long": 0.000_01,
        "cached": 0.000_000_625,
    },
    "gemini-1.5-pro-latest": {
        "prompt_short": 0.000_001_25,
        "completion_short": 0.000_005,
        "prompt_long": 0.000_002_5,
        "completion_long": 0.000_01,
        "cached": 0.000_000_625,
    },
    "gemini-1.5-pro-001": {
        "prompt_short": 0.000_001_25,
        "completion_short": 0.000_005,
        "prompt_long": 0.000_002_5,
        "completion_long": 0.000_01,
        "cached": 0.000_000_625,
    },
    "gemini-1.5-pro-002": {
        "prompt_short": 0.000_001_25,
        "completion_short": 0.000_005,
        "prompt_long": 0.000_002_5,
        "completion_long": 0.000_01,
        "cached": 0.000_000_625,
    },
    "gemini-1.5-flash": {
        "prompt_short": 0.000_000_075,
        "completion_short": 0.000_000_30,
        "prompt_long": 0.000_000_15,
        "completion_long": 0.000_000_60,
        "cached": 0.000_000_037_5,
    },
    "gemini-1.5-flash-latest": {
        "prompt_short": 0.000_000_075,
        "completion_short": 0.000_000_30,
        "prompt_long": 0.000_000_15,
        "completion_long": 0.000_000_60,
        "cached": 0.000_000_037_5,
    },
    "gemini-1.5-flash-001": {
        "prompt_short": 0.000_000_075,
        "completion_short": 0.000_000_30,
        "prompt_long": 0.000_000_15,
        "completion_long": 0.000_000_60,
        "cached": 0.000_000_037_5,
    },
    "gemini-1.5-flash-002": {
        "prompt_short": 0.000_000_075,
        "completion_short": 0.000_000_30,
        "prompt_long": 0.000_000_15,
        "completion_long": 0.000_000_60,
        "cached": 0.000_000_037_5,
    },
    "gemini-1.5-flash-8b": {
        "prompt_short": 0.000_000_037_5,
        "completion_short": 0.000_000_15,
        "prompt_long": 0.000_000_075,
        "completion_long": 0.000_000_30,
        "cached": 0.000_000_025,
    },
    "gemini-1.5-flash-8b-latest": {
        "prompt_short": 0.000_000_037_5,
        "completion_short": 0.000_000_15,
        "prompt_long": 0.000_000_075,
        "completion_long": 0.000_000_30,
        "cached": 0.000_000_025,
    },
    "gemini-1.5-flash-8b-001": {
        "prompt_short": 0.000_000_037_5,
        "completion_short": 0.000_000_15,
        "prompt_long": 0.000_000_075,
        "completion_long": 0.000_000_30,
        "cached": 0.000_000_025,
    },
    "gemini-1.5-flash-8b-002": {
        "prompt_short": 0.000_000_037_5,
        "completion_short": 0.000_000_15,
        "prompt_long": 0.000_000_075,
        "completion_long": 0.000_000_30,
        "cached": 0.000_000_025,
    },
    "gemini-1.0-pro": {
        "prompt_short": 0.000_000_5,
        "completion_short": 0.000_001_5,
        "prompt_long": 0.000_000_5,
        "completion_long": 0.000_001_5,
        "cached": 0.000_000,
    },
}

# Vertex AI pricing table
VERTEX_AI_PRICING: dict[str, dict[str, float]] = {
    "gemini-2.0-flash": {
        "text_input": 0.000_000_15,
        "image_input": 0.000_000_15,
        "video_input": 0.000_000_15,
        "audio_input": 0.000_001_00,
        "output": 0.000_000_60,
        "cached": 0.000_000_037_5,
        "cache_storage_per_hour": 0.000_001_00,
    },
    "gemini-2.0-flash-lite": {
        "text_input": 0.000_000_075,
        "image_input": 0.000_000_075,
        "video_input": 0.000_000_075,
        "audio_input": 0.000_000_075,
        "output": 0.000_000_30,
        "cached": 0.000_000_037_5,
        "cache_storage_per_hour": 0.000_001_00,
    },
    # Vertex AI pricing for Gemini 1.5 models is based on modalities rather than tokens
    "gemini-1.5-flash": {
        "text_input": 0.000_000_075,  # per 1K chars (approx. 250 tokens)
        "image_input": 0.000_02,  # per image
        "video_input": 0.000_02,  # per second
        "audio_input": 0.000_002,  # per second
        "output": 0.000_000_30,  # per 1K chars
        "cached_text": 0.000_000_046_875,  # per 1K chars
        "cached_image": 0.000_005,  # per image
        "cached_video": 0.000_005,  # per second
        "cached_audio": 0.000_000_5,  # per second
        "cache_storage_text": 0.000_25,  # per 1K chars per hour
        "cache_storage_image": 0.000_263,  # per image per hour
        "cache_storage_video": 0.000_263,  # per second per hour
        "cache_storage_audio": 0.000_025,  # per second per hour
    },
    "gemini-1.5-pro": {
        "text_input": 0.000_001_25,  # per 1K chars (approx. 250 tokens)
        "image_input": 0.000_32875,  # per image
        "video_input": 0.000_32875,  # per second
        "audio_input": 0.000_03125,  # per second
        "output": 0.000_005,  # per 1K chars
        "cached_text": 0.000_000_078125,  # per 1K chars
        "cached_image": 0.000_0821875,  # per image
        "cached_video": 0.000_0821875,  # per second
        "cached_audio": 0.000_0078125,  # per second
        "cache_storage_text": 0.001125,  # per 1K chars per hour
        "cache_storage_image": 0.0011835,  # per image per hour
        "cache_storage_video": 0.0011835,  # per second per hour
        "cache_storage_audio": 0.0001125,  # per second per hour
    },
}


def _calculate_context_cache_cost(
    metadata: CostMetadata,
    model_pricing: dict[str, float],
    model: str,
    use_vertex_ai: bool = False,
) -> float:
    """Calculate cost for context caching."""
    if metadata.context_cache_tokens is None or metadata.context_cache_hours is None:
        return 0.0

    if use_vertex_ai:
        # Vertex AI pricing depends on the model family
        if model.startswith("gemini-2.0"):
            return (
                metadata.context_cache_tokens
                * model_pricing.get("cache_storage_per_hour", 0)
                * metadata.context_cache_hours
            )
        elif model.startswith("gemini-1.5"):
            # Convert cache tokens to characters (approx)
            cache_chars = metadata.context_cache_tokens * 4
            return (
                (cache_chars / 1000)
                * model_pricing["cache_storage_text"]
                * metadata.context_cache_hours
            )

    # Standard Gemini API pricing - storage cost per token-hour
    storage_rate_per_token = 0.000001  # $1.00 per million tokens per hour
    if "flash-8b" in model:
        storage_rate_per_token = 0.00000025  # $0.25 per million tokens for 8B models

    return (
        metadata.context_cache_tokens
        * storage_rate_per_token
        * metadata.context_cache_hours
    )


def _calculate_grounding_cost(metadata: CostMetadata, model: str) -> float:
    """Calculate cost for grounding requests."""
    if metadata.google is None or metadata.google.grounding_requests is None:
        return 0.0

    # First 1,500 requests per day are free for Gemini 2.0 Flash models in Vertex AI
    if (
        model == "gemini-2.0-flash"
        and metadata.google.use_vertex_ai
        and metadata.google.grounding_requests <= 1500
    ):
        return 0.0

    # $35 per 1,000 requests for excess
    if metadata.google.use_vertex_ai and model == "gemini-2.0-flash":
        excess_requests = max(0, metadata.google.grounding_requests - 1500)
    else:
        excess_requests = metadata.google.grounding_requests

    return (excess_requests / 1000) * 35.0


def _calculate_vertex_2_0_cost(
    metadata: CostMetadata, model_pricing: dict[str, float], model: str
) -> float:
    """Calculate cost for Vertex AI's Gemini 2.0 models."""
    # Text tokens cost
    prompt_cost = (metadata.input_tokens or 0) * model_pricing["text_input"]
    completion_cost = (metadata.output_tokens or 0) * model_pricing["output"]
    cached_cost = (metadata.cached_tokens or 0) * model_pricing.get("cached", 0)

    # Context cache costs
    context_cache_cost = _calculate_context_cache_cost(
        metadata, model_pricing, model, use_vertex_ai=True
    )

    # Grounding costs
    grounding_cost = _calculate_grounding_cost(metadata, model)

    # Apply batch mode discount (50% for Vertex AI)
    if metadata.batch_mode:
        prompt_cost *= 0.5
        completion_cost *= 0.5
        context_cache_cost *= 0.5
        # Note: We don't discount grounding costs

    total_cost = (
        prompt_cost
        + completion_cost
        + cached_cost
        + context_cache_cost
        + grounding_cost
    )

    return total_cost


def _calculate_vertex_1_5_cost(
    metadata: CostMetadata, model_pricing: dict[str, float], model: str
) -> float:
    """Calculate cost for Vertex AI's Gemini 1.5 models."""
    # Text cost - convert tokens to characters (approx 4 chars per token)
    text_chars = (metadata.input_tokens or 0) * 4  # Approximation
    text_cost = (text_chars / 1000) * model_pricing["text_input"]

    # Output cost
    output_chars = (metadata.output_tokens or 0) * 4  # Approximation
    output_cost = (output_chars / 1000) * model_pricing["output"]

    # Context cache costs
    context_cache_cost = _calculate_context_cache_cost(
        metadata, model_pricing, model, use_vertex_ai=True
    )

    # Grounding costs
    grounding_cost = _calculate_grounding_cost(metadata, model)

    # Apply batch mode discount if applicable (50% off for Vertex AI)
    if metadata.batch_mode:
        text_cost *= 0.5
        output_cost *= 0.5
        context_cache_cost *= 0.5
        # Note: We don't discount grounding costs

    total_cost = text_cost + output_cost + context_cache_cost + grounding_cost

    return total_cost


def _calculate_standard_gemini_cost(
    metadata: CostMetadata,
    model_pricing: dict[str, float],
    model: str,
    use_long_context: bool,
) -> float:
    """Calculate cost for standard Gemini API."""
    # Determine prices based on context length
    prompt_price = model_pricing["prompt_long" if use_long_context else "prompt_short"]
    cached_price = model_pricing["cached"]
    completion_price = model_pricing[
        "completion_long" if use_long_context else "completion_short"
    ]

    # Basic token costs
    prompt_cost = (metadata.input_tokens or 0) * prompt_price
    cached_cost = (metadata.cached_tokens or 0) * cached_price
    completion_cost = (metadata.output_tokens or 0) * completion_price

    # Media token costs is included in the prompt/completion cost

    # Context cache costs
    context_cache_cost = _calculate_context_cache_cost(
        metadata, model_pricing, model, use_vertex_ai=False
    )

    # Grounding costs - only applies to certain models
    grounding_cost = _calculate_grounding_cost(metadata, model)

    total_cost = (
        prompt_cost
        + cached_cost
        + completion_cost
        + context_cache_cost
        + grounding_cost
    )

    return total_cost


def calculate_cost(
    metadata: CostMetadata,
    model: str,
) -> float | None:
    """Calculate the cost of a Google API call.

    This function supports both direct Gemini API and Vertex AI pricing.
    It handles different media types (text, image, video, audio) and special features
    like context caching and grounding.

    https://ai.google.dev/pricing
    https://cloud.google.com/vertex-ai/generative-ai/pricing

    Args:
        metadata: Additional metadata required for cost calculation
        model: Model name to use for pricing calculation

    Returns:
        Total cost in USD or None if invalid input
    """
    # Basic validation
    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    # Initialize default values
    if metadata.cached_tokens is None:
        metadata.cached_tokens = 0

    # Check if we're using Vertex AI pricing
    use_vertex_ai = metadata.google and metadata.google.use_vertex_ai

    # Determine if we're using long context pricing
    use_long_context = (
        metadata.context_length is not None and metadata.context_length > 128_000
    ) or (metadata.input_tokens > 128_000)

    # Get the appropriate pricing table
    try:
        if use_vertex_ai and model in VERTEX_AI_PRICING:
            model_pricing = VERTEX_AI_PRICING[model]
        else:
            model_pricing = GEMINI_API_PRICING[model]
    except KeyError:
        # Unknown model
        return None

    # Calculate cost based on API type
    if use_vertex_ai:
        if model.startswith("gemini-2.0"):
            return _calculate_vertex_2_0_cost(metadata, model_pricing, model)
        elif model.startswith("gemini-1.5"):  # pragma: no cover
            return _calculate_vertex_1_5_cost(metadata, model_pricing, model)
    else:
        # Standard Gemini API pricing
        return _calculate_standard_gemini_cost(
            metadata, model_pricing, model, use_long_context
        )
