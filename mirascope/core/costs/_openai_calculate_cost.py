"""Calculate the cost of a completion using the OpenAI API."""

from ..base.types import CostMetadata

# Constants for image token calculation
LOW_DETAIL_IMAGE_TOKENS = 85
HIGH_DETAIL_TILE_TOKENS = 170
HIGH_DETAIL_BASE_TOKENS = 85
TILE_SIZE = 512


def _calculate_image_tokens(metadata: CostMetadata) -> int | None:
    """Calculate tokens used by images based on their size and detail level.

    https://platform.openai.com/docs/guides/vision
    Following OpenAI's pricing structure:
    - Low detail: 85 tokens per image
    - High detail: 85 tokens base + 170 tokens per 512px tile
      (after scaling to fit within 2048x2048 and making shortest side 768px)
    """
    if not metadata.images or not metadata.images:
        return 0

    total_image_tokens = 0

    for img in metadata.images:
        if not img.width or not img.height:
            continue

        # If image already has precalculated tokens, use those
        if img.tokens is not None:
            total_image_tokens += img.tokens
            continue

        if img.detail is not None and img.detail != "auto":
            detail = img.detail
        else:
            # Default to high detail for auto
            # We can't determine detail level from image alone
            detail = "high"
        if detail == "low":
            # Low detail is a fixed cost regardless of size
            total_image_tokens += LOW_DETAIL_IMAGE_TOKENS
        else:
            # High detail calculation

            # Scale to fit within 2048x2048 square
            width, height = img.width, img.height
            if width > 2048 or height > 2048:
                aspect_ratio = width / height
                if width > height:
                    width = 2048
                    height = int(width / aspect_ratio)
                else:
                    height = 2048
                    width = int(height * aspect_ratio)

            # Scale so shortest side is 768px
            if min(width, height) > 768:
                if width < height:
                    scale_factor = 768 / width
                    width = 768
                    height = int(height * scale_factor)
                else:
                    scale_factor = 768 / height
                    height = 768
                    width = int(width * scale_factor)

            # Calculate number of 512px tiles needed
            tiles_x = (width + TILE_SIZE - 1) // TILE_SIZE
            tiles_y = (height + TILE_SIZE - 1) // TILE_SIZE
            num_tiles = tiles_x * tiles_y

            # Calculate token cost
            image_tokens = (
                HIGH_DETAIL_TILE_TOKENS * num_tiles
            ) + HIGH_DETAIL_BASE_TOKENS
            total_image_tokens += image_tokens

    return total_image_tokens


def calculate_cost(
    metadata: CostMetadata,
    model: str = "gpt-3.5-turbo-16k",
) -> float | None:
    """Calculate the cost of a completion using the OpenAI API.

    https://openai.com/pricing

    Model                                     Input               Cached               Output
    gpt-4.5-preview                           $75.00 / 1M tokens  $37.50 / 1M tokens   $150.00 / 1M tokens
    gpt-4.5-preview-2025-02-27                $75.00 / 1M tokens  $37.50 / 1M tokens   $150.00 / 1M tokens
    gpt-4o                                    $2.50  / 1M tokens  $1.25 / 1M tokens    $10.00 / 1M tokens
    gpt-4o-2024-11-20                         $2.50  / 1M tokens  $1.25 / 1M tokens    $10.00 / 1M tokens
    gpt-4o-2024-08-06                         $2.50  / 1M tokens  $1.25 / 1M tokens    $10.00 / 1M tokens
    gpt-4o-2024-05-13                         $5.00  / 1M tokens                       $15.00 / 1M tokens
    gpt-4o-audio-preview                      $2.50  / 1M tokens  $1.25 / 1M tokens    $10.00 / 1M tokens
    gpt-4o-audio-preview-2024-12-17           $2.50  / 1M tokens  $1.25 / 1M tokens    $10.00 / 1M tokens
    gpt-4o-audio-preview-2024-10-01           $2.50  / 1M tokens  $1.25 / 1M tokens    $10.00 / 1M tokens
    gpt-4o-realtime-preview                   $5.00  / 1M tokens  $2.50 / 1M tokens    $20.00 / 1M tokens
    gpt-4o-realtime-preview-2024-12-17        $5.00  / 1M tokens  $2.50 / 1M tokens    $20.00 / 1M tokens
    gpt-4o-realtime-preview-2024-10-01        $5.00  / 1M tokens  $2.50 / 1M tokens    $20.00 / 1M tokens
    gpt-4o-mini                               $0.150 / 1M tokens  $0.075 / 1M tokens   $0.600 / 1M tokens
    gpt-4o-mini-2024-07-18                    $0.150 / 1M tokens  $0.075 / 1M tokens   $0.600 / 1M tokens
    gpt-4o-mini-audio-preview                 $0.150 / 1M tokens  $0.075 / 1M tokens   $0.600 / 1M tokens
    gpt-4o-mini-audio-preview-2024-12-17      $0.150 / 1M tokens  $0.075 / 1M tokens   $0.600 / 1M tokens
    gpt-4o-mini-realtime-preview              $0.60  / 1M tokens  $0.30 / 1M tokens    $2.40  / 1M tokens
    gpt-4o-mini-realtime-preview-2024-12-17   $0.60  / 1M tokens  $0.30 / 1M tokens    $2.40  / 1M tokens
    o1                                        $15.00 / 1M tokens  $7.50 / 1M tokens    $60.00 / 1M tokens
    o1-2024-12-17                             $15.00 / 1M tokens  $7.50 / 1M tokens    $60.00 / 1M tokens
    o1-preview                                $15.00 / 1M tokens  $7.50 / 1M tokens    $60.00 / 1M tokens
    o1-preview-2024-09-12                     $15.00 / 1M tokens  $7.50 / 1M tokens    $60.00 / 1M tokens
    o3-mini                                   $1.10  / 1M tokens  $0.55 / 1M tokens    $4.40  / 1M tokens
    o3-mini-2025-01-31                        $1.10  / 1M tokens  $0.55 / 1M tokens    $4.40  / 1M tokens
    o1-mini                                   $1.10  / 1M tokens  $0.55 / 1M tokens    $4.40  / 1M tokens
    o1-mini-2024-09-12                        $1.10  / 1M tokens  $0.55 / 1M tokens    $4.40  / 1M tokens
    chatgpt-4o-latest                         $5.00  / 1M tokens                       $15.00 / 1M tokens
    gpt-4-turbo                               $10.00 / 1M tokens                       $30.00 / 1M tokens
    gpt-4-turbo-2024-04-09                    $10.00 / 1M tokens                       $30.00 / 1M tokens
    gpt-3.5-turbo-0125                        $0.50  / 1M tokens                       $1.50  / 1M tokens
    gpt-3.5-turbo-1106                        $1.00  / 1M tokens                       $2.00  / 1M tokens
    gpt-4-0125-preview                        $10.00 / 1M tokens                       $30.00 / 1M tokens
    gpt-4-1106-preview                        $10.00 / 1M tokens                       $30.00 / 1M tokens
    gpt-4-vision-preview                      $10.00 / 1M tokens                       $30.00 / 1M tokens
    gpt-4                                     $30.00 / 1M tokens                       $60.00 / 1M tokens
    gpt-4-32k                                 $60.00 / 1M tokens                       $120.00 / 1M tokens
    text-embedding-3-small                    $0.02  / 1M tokens
    text-embedding-3-large                    $0.13  / 1M tokens
    text-embedding-ada-002                    $0.10  / 1M tokens
    """
    pricing = {
        "gpt-4.5-preview": {
            "prompt": 0.000_075,
            "cached": 0.000_037_5,
            "completion": 0.000_15,
            "batch_prompt": 0.000_037_5,
            "batch_completion": 0.000_075,
        },
        "gpt-4.5-preview-2025-02-27": {
            "prompt": 0.000_075,
            "cached": 0.000_037_5,
            "completion": 0.000_15,
        },
        "gpt-4o": {
            "prompt": 0.000_002_5,
            "cached": 0.000_001_25,
            "completion": 0.000_01,
            "batch_prompt": 0.000_001_25,
            "batch_completion": 0.000_005,
        },
        "gpt-4o-2024-11-20": {
            "prompt": 0.000_002_5,
            "cached": 0.000_001_25,
            "completion": 0.000_01,
        },
        "gpt-4o-2024-08-06": {
            "prompt": 0.000_002_5,
            "cached": 0.000_001_25,
            "completion": 0.000_01,
        },
        "gpt-4o-2024-05-13": {
            "prompt": 0.000_005,
            "cached": 0.000_002_5,
            "completion": 0.000_015,
        },
        "gpt-4o-audio-preview": {
            "prompt": 0.000_002_5,
            "cached": 0.000_001_25,
            "completion": 0.000_01,
        },
        "gpt-4o-audio-preview-2024-12-17": {
            "prompt": 0.000_002_5,
            "cached": 0.000_001_25,
            "completion": 0.000_01,
        },
        "gpt-4o-audio-preview-2024-10-01": {
            "prompt": 0.000_002_5,
            "cached": 0.000_001_25,
            "completion": 0.000_01,
        },
        "gpt-4o-realtime-preview": {
            "prompt": 0.000_005,
            "cached": 0.000_002_5,
            "completion": 0.000_02,
        },
        "gpt-4o-realtime-preview-2024-12-17": {
            "prompt": 0.000_005,
            "cached": 0.000_002_5,
            "completion": 0.000_02,
        },
        "gpt-4o-realtime-preview-2024-10-01": {
            "prompt": 0.000_005,
            "cached": 0.000_002_5,
            "completion": 0.000_02,
        },
        "gpt-4o-mini": {
            "prompt": 0.000_000_15,
            "cached": 0.000_000_075,
            "completion": 0.000_000_6,
        },
        "gpt-4o-mini-2024-07-18": {
            "prompt": 0.000_000_15,
            "cached": 0.000_000_075,
            "completion": 0.000_000_6,
        },
        "gpt-4o-mini-audio-preview": {
            "prompt": 0.000_000_15,
            "cached": 0.000_000_075,
            "completion": 0.000_000_6,
        },
        "gpt-4o-mini-audio-preview-2024-12-17": {
            "prompt": 0.000_000_15,
            "cached": 0.000_000_075,
            "completion": 0.000_000_6,
        },
        "gpt-4o-mini-realtime-preview": {
            "prompt": 0.000_000_6,
            "cached": 0.000_000_3,
            "completion": 0.000_002_4,
        },
        "gpt-4o-mini-realtime-preview-2024-12-17": {
            "prompt": 0.000_000_6,
            "cached": 0.000_000_3,
            "completion": 0.000_002_4,
        },
        "o1": {
            "prompt": 0.000_015,
            "cached": 0.000_007_5,
            "completion": 0.000_06,
        },
        "o1-2024-12-17": {
            "prompt": 0.000_015,
            "cached": 0.000_007_5,
            "completion": 0.000_06,
        },
        "o1-preview": {
            "prompt": 0.000_015,
            "cached": 0.000_007_5,
            "completion": 0.000_06,
        },
        "o1-preview-2024-09-12": {
            "prompt": 0.000_015,
            "cached": 0.000_007_5,
            "completion": 0.000_06,
        },
        "o3-mini": {
            "prompt": 0.000_001_1,
            "cached": 0.000_000_55,
            "completion": 0.000_004_4,
        },
        "o3-mini-2025-01-31": {
            "prompt": 0.000_001_1,
            "cached": 0.000_000_55,
            "completion": 0.000_004_4,
        },
        "o1-mini": {
            "prompt": 0.000_001_1,
            "cached": 0.000_000_55,
            "completion": 0.000_004_4,
        },
        "o1-mini-2024-09-12": {
            "prompt": 0.000_001_1,
            "cached": 0.000_000_55,
            "completion": 0.000_004_4,
        },
        "chatgpt-4o-latest": {
            "prompt": 0.000_005,
            "cached": 0,
            "completion": 0.000_015,
        },
        "gpt-4-turbo": {
            "prompt": 0.000_01,
            "cached": 0,
            "completion": 0.000_03,
        },
        "gpt-4-turbo-2024-04-09": {
            "prompt": 0.000_01,
            "cached": 0,
            "completion": 0.000_03,
        },
        "gpt-3.5-turbo-0125": {
            "prompt": 0.000_000_5,
            "cached": 0,
            "completion": 0.000_001_5,
        },
        "gpt-3.5-turbo-1106": {
            "prompt": 0.000_001,
            "cached": 0,
            "completion": 0.000_002,
        },
        "gpt-4-0125-preview": {
            "prompt": 0.000_01,
            "cached": 0,
            "completion": 0.000_03,
        },
        "gpt-4-1106-preview": {
            "prompt": 0.000_01,
            "cached": 0,
            "completion": 0.000_03,
        },
        "gpt-4-vision-preview": {
            "prompt": 0.000_01,
            "cached": 0,
            "completion": 0.000_03,
        },
        "gpt-4": {
            "prompt": 0.000_03,
            "cached": 0,
            "completion": 0.000_06,
        },
        "gpt-4-32k": {
            "prompt": 0.000_06,
            "cached": 0,
            "completion": 0.000_12,
        },
        "gpt-3.5-turbo-4k": {
            "prompt": 0.000_015,
            "cached": 0,
            "completion": 0.000_02,
        },
        "gpt-3.5-turbo-16k": {
            "prompt": 0.000_003,
            "cached": 0,
            "completion": 0.000_004,
        },
        "gpt-4-8k": {
            "prompt": 0.000_03,
            "cached": 0,
            "completion": 0.000_06,
        },
        "text-embedding-3-small": {
            "prompt": 0.000_000_02,
            "cached": 0,
            "completion": 0,
            "batch_prompt": 0.000_000_01,
        },
        "text-embedding-ada-002": {
            "prompt": 0.000_000_1,
            "cached": 0,
            "completion": 0,
            "batch_prompt": 0.000_000_05,
        },
        "text-embedding-3-large": {
            "prompt": 0.000_000_13,
            "cached": 0,
            "completion": 0,
            "batch_prompt": 0.000_000_065,
        },
    }

    # Audio pricing for audio models (per-minute rates in dollars)

    if metadata.cost is not None:
        return metadata.cost

    # Audio input/output costs
    # ChatCompletion.usage has brake down of audio input and output.
    # The total cost already includes the audio input/output cost.

    # Initialize cached tokens if not provided
    if metadata.cached_tokens is None:
        metadata.cached_tokens = 0

    # Try to get model pricing
    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    image_tokens = _calculate_image_tokens(metadata) or 0

    input_tokens = (metadata.input_tokens or 0) + image_tokens

    # Calculate costs for each component
    prompt_cost = input_tokens * model_pricing["prompt"]
    cached_cost = metadata.cached_tokens * model_pricing["cached"]
    completion_cost = (metadata.output_tokens or 0) * model_pricing["completion"]

    # Special handling for embedding models (only input tokens matter)
    if "embedding" in model:
        total_cost = prompt_cost
    else:
        total_cost = prompt_cost + cached_cost + completion_cost

    # Apply batch discounts if applicable
    if metadata.batch_mode:
        # Based on the OpenAI pricing table, batch mode typically provides
        # approximately 50% discount for both input and output tokens
        if "embedding" in model.lower():
            # Embedding models have specific batch pricing
            if model == "text-embedding-3-small":
                prompt_cost = (
                    input_tokens * 0.000_000_01
                )  # $0.01 per 1M tokens in batch mode
            elif model == "text-embedding-3-large":
                prompt_cost = (
                    input_tokens * 0.000_000_065
                )  # $0.065 per 1M tokens in batch mode
            elif model == "text-embedding-ada-002":
                prompt_cost = (
                    input_tokens * 0.000_000_05
                )  # $0.05 per 1M tokens in batch mode
        else:
            # For LLM models, typically 50% discount
            prompt_cost *= 0.5
            cached_cost *= 0.5
            completion_cost *= 0.5

        # Recalculate total cost with batch pricing
        if "embedding" in model:
            total_cost = prompt_cost
        else:
            total_cost = prompt_cost + cached_cost + completion_cost

    return total_cost
