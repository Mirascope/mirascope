from unittest.mock import MagicMock

from mirascope.llm.providers.base import Params
from mirascope.llm.providers.mlx._utils import encode_params, extract_finish_reason
from mirascope.llm.responses import FinishReason


def test_extract_finish_reason_none() -> None:
    """Test extracting finish reason from None response."""
    assert extract_finish_reason(None) is None


def test_extract_finish_reason_length() -> None:
    """Extract finish reason from length response."""
    finish_reason = MagicMock()
    finish_reason.finish_reason = "length"
    assert extract_finish_reason(finish_reason) == FinishReason.MAX_TOKENS


def test_extract_finish_reason_stop() -> None:
    """Extract finish reason from stop response."""
    finish_reason = MagicMock()
    finish_reason.finish_reason = "stop"
    assert extract_finish_reason(finish_reason) is None


def test_encode_params_empty() -> None:
    """Test extracting params from empty params dict."""
    seed, kwargs = encode_params(Params())
    assert seed is None
    assert kwargs.get("max_tokens") == -1
    assert "sampler" in kwargs


def test_encode_params_with_max_tokens() -> None:
    """Test extracting params with max_tokens."""
    seed, kwargs = encode_params(Params(max_tokens=100))
    assert seed is None
    assert kwargs.get("max_tokens") == 100
    assert "sampler" in kwargs


def test_encode_params_with_sampler() -> None:
    """Test extracting params with temperature."""
    seed, kwargs = encode_params(Params(temperature=0.7, top_k=50, top_p=0.9))
    assert seed is None
    assert "sampler" in kwargs


def test_encode_params_with_seed() -> None:
    """Test extracting params with seed."""
    seed, kwargs = encode_params(Params(seed=42))
    assert seed == 42
    assert "sampler" in kwargs


def test_encode_params_with_all_params() -> None:
    """Test extracting params with all supported parameters."""
    seed, kwargs = encode_params(
        Params(
            max_tokens=200,
            temperature=0.5,
            top_k=40,
            top_p=0.95,
            seed=123,
        )
    )
    assert seed == 123
    assert kwargs.get("max_tokens") == 200
    assert "sampler" in kwargs
