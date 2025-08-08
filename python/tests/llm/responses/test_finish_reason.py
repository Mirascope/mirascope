"""Tests for FinishReason enum."""

from enum import Enum

from mirascope import llm


class TestFinishReason:
    """Test FinishReason enum."""

    def test_finish_reason_is_str_enum(self) -> None:
        """Test that FinishReason is a string enum."""
        assert issubclass(llm.FinishReason, str)
        assert issubclass(llm.FinishReason, Enum)

    def test_finish_reason_values(self) -> None:
        """Test all FinishReason values."""
        assert llm.FinishReason.STOP == "stop"
        assert llm.FinishReason.MAX_TOKENS == "max_tokens"
        assert llm.FinishReason.END_TURN == "end_turn"
        assert llm.FinishReason.TOOL_USE == "tool_use"
        assert llm.FinishReason.REFUSAL == "refusal"
        assert llm.FinishReason.UNKNOWN == "unknown"

    def test_finish_reason_membership(self) -> None:
        """Test FinishReason membership."""
        all_values = [
            llm.FinishReason.STOP,
            llm.FinishReason.MAX_TOKENS,
            llm.FinishReason.END_TURN,
            llm.FinishReason.TOOL_USE,
            llm.FinishReason.REFUSAL,
            llm.FinishReason.UNKNOWN,
        ]

        for value in all_values:
            assert value in llm.FinishReason

    def test_finish_reason_iteration(self) -> None:
        """Test iterating over FinishReason values."""
        expected_values = {
            "stop",
            "max_tokens",
            "end_turn",
            "tool_use",
            "refusal",
            "unknown",
        }

        actual_values = {reason.value for reason in llm.FinishReason}
        assert actual_values == expected_values

    def test_finish_reason_count(self) -> None:
        """Test FinishReason has expected number of values."""
        assert len(llm.FinishReason) == 6

    def test_finish_reason_string_behavior(self) -> None:
        """Test FinishReason string behavior."""
        # Test that we can use FinishReason values as strings
        reason = llm.FinishReason.STOP

        assert str(reason) == "FinishReason.STOP"  # Enum string representation
        assert reason.value == "stop"  # The actual string value
        assert f"Reason: {reason.value}" == "Reason: stop"

        # Test string comparison with value
        assert reason == "stop"
        assert reason == "stop"

    def test_finish_reason_from_string(self) -> None:
        """Test creating FinishReason from string."""
        assert llm.FinishReason("stop") == llm.FinishReason.STOP
        assert llm.FinishReason("max_tokens") == llm.FinishReason.MAX_TOKENS
        assert llm.FinishReason("end_turn") == llm.FinishReason.END_TURN
        assert llm.FinishReason("tool_use") == llm.FinishReason.TOOL_USE
        assert llm.FinishReason("refusal") == llm.FinishReason.REFUSAL
        assert llm.FinishReason("unknown") == llm.FinishReason.UNKNOWN

    def test_finish_reason_invalid_value(self) -> None:
        """Test creating FinishReason with invalid value raises ValueError."""
        import pytest

        with pytest.raises(ValueError):
            llm.FinishReason("invalid_reason")
