"""Tests for FinishReason enum."""

from enum import Enum

from mirascope.llm.responses.finish_reason import FinishReason


class TestFinishReason:
    """Test FinishReason enum."""

    def test_finish_reason_is_str_enum(self):
        """Test that FinishReason is a string enum."""
        assert issubclass(FinishReason, str)
        assert issubclass(FinishReason, Enum)

    def test_finish_reason_values(self):
        """Test all FinishReason values."""
        assert FinishReason.STOP == "stop"
        assert FinishReason.MAX_TOKENS == "max_tokens"
        assert FinishReason.END_TURN == "end_turn"
        assert FinishReason.TOOL_USE == "tool_use"
        assert FinishReason.REFUSAL == "refusal"
        assert FinishReason.UNKNOWN == "unknown"

    def test_finish_reason_membership(self):
        """Test FinishReason membership."""
        all_values = [
            FinishReason.STOP,
            FinishReason.MAX_TOKENS,
            FinishReason.END_TURN,
            FinishReason.TOOL_USE,
            FinishReason.REFUSAL,
            FinishReason.UNKNOWN,
        ]

        for value in all_values:
            assert value in FinishReason

    def test_finish_reason_iteration(self):
        """Test iterating over FinishReason values."""
        expected_values = {
            "stop",
            "max_tokens",
            "end_turn",
            "tool_use",
            "refusal",
            "unknown",
        }

        actual_values = {reason.value for reason in FinishReason}
        assert actual_values == expected_values

    def test_finish_reason_count(self):
        """Test FinishReason has expected number of values."""
        assert len(FinishReason) == 6

    def test_finish_reason_string_behavior(self):
        """Test FinishReason string behavior."""
        # Test that we can use FinishReason values as strings
        reason = FinishReason.STOP

        assert str(reason) == "FinishReason.STOP"  # Enum string representation
        assert reason.value == "stop"  # The actual string value
        assert f"Reason: {reason.value}" == "Reason: stop"

        # Test string comparison with value
        assert reason == "stop"
        assert reason == "stop"

    def test_finish_reason_from_string(self):
        """Test creating FinishReason from string."""
        assert FinishReason("stop") == FinishReason.STOP
        assert FinishReason("max_tokens") == FinishReason.MAX_TOKENS
        assert FinishReason("end_turn") == FinishReason.END_TURN
        assert FinishReason("tool_use") == FinishReason.TOOL_USE
        assert FinishReason("refusal") == FinishReason.REFUSAL
        assert FinishReason("unknown") == FinishReason.UNKNOWN

    def test_finish_reason_invalid_value(self):
        """Test creating FinishReason with invalid value raises ValueError."""
        import pytest

        with pytest.raises(ValueError):
            FinishReason("invalid_reason")
