"""Calculate the cost of a completion using the Mistral API."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str = "open-mistral-7b",
) -> float | None:
    """Calculate the cost of a completion using the Mistral API.

    https://mistral.ai/technology/#pricing

    Model                     Input               Cached     Output
    mistral-large-latest      $2/1M tokens                   $6/1M tokens
    pixtral-large-latest      $2/1M tokens                   $6/1M tokens
    mistral-small-latest      $0.1/1M tokens                 $0.3/1M tokens
    mistral-saba-latest       $0.2/1M tokens                 $0.6/1M tokens
    codestral-latest          $0.3/1M tokens                 $0.9/1M tokens
    ministral-8b-latest       $0.1/1M tokens                 $0.1/1M tokens
    ministral-3b-latest       $0.04/1M tokens                $0.04/1M tokens
    mistral-embed             $0.1/1M tokens                 -
    mistral-moderation-latest $0.1/1M tokens                 -
    open-mistral-nemo         $0.3/1M tokens                 $0.3/1M tokens
    open-mistral-7b           $0.25/1M tokens                $0.25/1M tokens
    open-mixtral-8x7b         $0.7/1M tokens                 $0.7/1M tokens
    open-mixtral-8x22b        $2/1M tokens                   $6/1M tokens
    """
    pricing = {
        "mistral-large-latest": {"prompt": 0.000_002, "completion": 0.000_006},
        "pixtral-large-latest": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-small-latest": {"prompt": 0.000_000_1, "completion": 0.000_000_3},
        "mistral-saba-latest": {"prompt": 0.000_000_2, "completion": 0.000_000_6},
        "codestral-latest": {"prompt": 0.000_000_3, "completion": 0.000_000_9},
        "ministral-8b-latest": {"prompt": 0.000_000_1, "completion": 0.000_000_1},
        "ministral-3b-latest": {"prompt": 0.000_000_04, "completion": 0.000_000_04},
        "mistral-embed": {"prompt": 0.000_000_1, "completion": 0},
        "mistral-moderation-latest": {"prompt": 0.000_000_1, "completion": 0},
        "open-mistral-nemo": {"prompt": 0.000_000_3, "completion": 0.000_000_3},
        "open-mistral-nemo-2407": {"prompt": 0.000_000_3, "completion": 0.000_000_3},
        "open-mistral-7b": {"prompt": 0.000_000_25, "completion": 0.000_000_25},
        "open-mixtral-8x7b": {"prompt": 0.000_000_7, "completion": 0.000_000_7},
        "open-mixtral-8x22b": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-large-2407": {"prompt": 0.000_003, "completion": 0.000_009},
        "mistral-medium-latest": {"prompt": 0.000_002_75, "completion": 0.000_008_1},
        "pixtral-12b-2409": {"prompt": 0.000_002, "completion": 0.000_006},
    }

    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    # Calculate cost for text tokens
    prompt_cost = metadata.input_tokens * model_pricing["prompt"]
    completion_cost = metadata.output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    # Calculate cost for images if present
    image_cost = 0.0
    if metadata.images:
        for image in metadata.images:
            # Use precalculated tokens if available
            if image.tokens is not None:
                image_tokens = image.tokens
            else:
                # For Mistral: Per their documentation, each image is divided into 16x16 pixel batches
                # Images larger than 1024x1024 are downscaled while maintaining aspect ratio

                # Apply downscaling if necessary
                width, height = image.width, image.height
                if width > 1024 or height > 1024:
                    if width > height:
                        height = int((height / width) * 1024)
                        width = 1024
                    else:
                        width = int((width / height) * 1024)
                        height = 1024

                # Calculate tokens: (width/16) * (height/16)
                image_tokens = (width / 16) * (height / 16)

            # Images are charged at the prompt token rate
            image_cost += image_tokens * model_pricing["prompt"]

    # Add image cost to total
    total_cost += image_cost

    return total_cost
