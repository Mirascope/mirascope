"""Tests that OpenAI cache-write tokens are reported in the usage."""

from openai.types import CompletionUsage
from openai.types.responses import ResponseUsage
from openai.types.responses.response_usage import InputTokensDetails

from mirascope.llm.providers.openai.completions._utils import decode as completions
from mirascope.llm.providers.openai.responses._utils import decode as responses


def test_completions_usage_has_cache_write_tokens() -> None:
    # Validated from a dict like the real JSON, since older SDKs don't declare the field.
    usage = completions._decode_usage(  # pyright: ignore[reportPrivateUsage]
        CompletionUsage.model_validate(
            {
                "prompt_tokens": 100,
                "completion_tokens": 5,
                "total_tokens": 105,
                "prompt_tokens_details": {
                    "cached_tokens": 20,
                    "cache_write_tokens": 30,
                },
            }
        )
    )

    assert usage is not None
    assert usage.cache_read_tokens == 20
    assert usage.cache_write_tokens == 30


def test_completions_usage_without_details_has_no_cache_write_tokens() -> None:
    usage = completions._decode_usage(  # pyright: ignore[reportPrivateUsage]
        CompletionUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    )

    assert usage is not None
    assert usage.cache_write_tokens == 0


def test_responses_usage_has_cache_write_tokens() -> None:
    usage = responses._decode_usage(  # pyright: ignore[reportPrivateUsage]
        ResponseUsage.model_validate(
            {
                "input_tokens": 100,
                "output_tokens": 5,
                "total_tokens": 105,
                "input_tokens_details": {"cached_tokens": 20, "cache_write_tokens": 30},
                "output_tokens_details": {"reasoning_tokens": 0},
            }
        )
    )

    assert usage is not None
    assert usage.cache_read_tokens == 20
    assert usage.cache_write_tokens == 30


def test_responses_usage_without_cache_write_tokens() -> None:
    # `cache_write_tokens` is a required field from openai 2.54.0 and absent before it, so
    # the details are constructed without validation to model a payload that omits it.
    usage = responses._decode_usage(  # pyright: ignore[reportPrivateUsage]
        ResponseUsage.model_validate(
            {
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
                "input_tokens_details": InputTokensDetails.model_construct(
                    cached_tokens=2
                ),
                "output_tokens_details": {"reasoning_tokens": 0},
            }
        )
    )

    assert usage is not None
    assert usage.cache_write_tokens == 0
