"""Calculate the cost of a completion using the Groq API."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str = "mixtral-8x7b-32768",
) -> float | None:
    """Calculate the cost of a completion using the Groq API.

    https://wow.groq.com/

    Model                                  Input                  Output
    llama-3.3-70b-versatile                $0.59 / 1M tokens      $0.79 / 1M tokens
    llama-3.3-70b-specdec                  $0.59 / 1M tokens      $0.99 / 1M tokens
    llama-3.1-8b-instant                   $0.05 / 1M tokens      $0.08 / 1M tokens
    llama3-70b-8192                        $0.59 / 1M tokens      $0.79 / 1M tokens
    llama3-8b-8192                         $0.05 / 1M tokens      $0.08 / 1M tokens
    llama-guard-3-8b                       $0.20 / 1M tokens      $0.20 / 1M tokens
    mixtral-8x7b-32768                     $0.24 / 1M tokens      $0.24 / 1M tokens
    gemma-7b-it                            $0.07 / 1M tokens      $0.07 / 1M tokens
    gemma2-9b-it                           $0.20 / 1M tokens      $0.20 / 1M tokens
    mistral-saba-24b                       $0.79 / 1M tokens      $0.79 / 1M tokens
    qwen-2.5-32b                           $0.79 / 1M tokens      $0.79 / 1M tokens
    qwen-2.5-coder-32b                     $0.79 / 1M tokens      $0.79 / 1M tokens
    deepseek-r1-distill-qwen-32b           $0.69 / 1M tokens      $0.69 / 1M tokens
    deepseek-r1-distill-llama-70b          $0.75 / 1M tokens      $0.99 / 1M tokens
    deepseek-r1-distill-llama-70b-specdec  $0.75 / 1M tokens      $0.99 / 1M tokens
    llama-3.2-1b-preview                   $0.04 / 1M tokens      $0.04 / 1M tokens
    llama-3.2-3b-preview                   $0.06 / 1M tokens      $0.06 / 1M tokens
    """
    pricing = {
        "llama-3.3-70b-versatile": {
            "prompt": 0.000_000_59,
            "completion": 0.000_000_79,
        },
        "llama-3.3-70b-specdec": {
            "prompt": 0.000_000_59,
            "completion": 0.000_000_99,
        },
        "llama3-groq-70b-8192-tool-use-preview": {
            "prompt": 0.000_000_89,
            "completion": 0.000_000_89,
        },
        "llama3-groq-8b-8192-tool-use-preview": {
            "prompt": 0.000_000_19,
            "completion": 0.000_000_19,
        },
        "llama-3.1-8b-instant": {
            "prompt": 0.000_000_05,
            "completion": 0.000_000_08,
        },
        "llama-guard-3-8b": {
            "prompt": 0.000_000_2,
            "completion": 0.000_000_2,
        },
        "llama3-70b-8192": {
            "prompt": 0.000_000_59,
            "completion": 0.000_000_79,
        },
        "llama3-8b-8192": {
            "prompt": 0.000_000_05,
            "completion": 0.000_000_08,
        },
        "mixtral-8x7b-32768": {
            "prompt": 0.000_000_24,
            "completion": 0.000_000_24,
        },
        "gemma-7b-it": {
            "prompt": 0.000_000_07,
            "completion": 0.000_000_07,
        },
        "gemma2-9b-it": {
            "prompt": 0.000_000_2,
            "completion": 0.000_000_2,
        },
        "mistral-saba-24b": {
            "prompt": 0.000_000_79,
            "completion": 0.000_000_79,
        },
        "qwen-2.5-32b": {
            "prompt": 0.000_000_79,
            "completion": 0.000_000_79,
        },
        "qwen-2.5-coder-32b": {
            "prompt": 0.000_000_79,
            "completion": 0.000_000_79,
        },
        "deepseek-r1-distill-qwen-32b": {
            "prompt": 0.000_000_69,
            "completion": 0.000_000_69,
        },
        "deepseek-r1-distill-llama-70b": {
            "prompt": 0.000_000_75,
            "completion": 0.000_000_99,
        },
        "deepseek-r1-distill-llama-70b-specdec": {
            "prompt": 0.000_000_75,
            "completion": 0.000_000_99,
        },
        "llama-3.2-1b-preview": {
            "prompt": 0.000_000_04,
            "completion": 0.000_000_04,
        },
        "llama-3.2-3b-preview": {
            "prompt": 0.000_000_06,
            "completion": 0.000_000_06,
        },
    }

    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = metadata.input_tokens * model_pricing["prompt"]
    completion_cost = metadata.output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
