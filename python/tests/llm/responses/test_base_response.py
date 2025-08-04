"""Tests for BaseResponse ABC."""

from abc import ABC

from mirascope.llm.responses.base_response import BaseResponse


class TestBaseResponse:
    """Test BaseResponse ABC."""

    def test_base_response_is_abc(self):
        """Test that BaseResponse is an abstract base class."""
        assert issubclass(BaseResponse, ABC)
