"""Tests for base provider error wrapping."""

from typing import Any, ClassVar
from unittest.mock import Mock

import pytest

from mirascope import llm
from mirascope.llm.providers.base import BaseProvider, ProviderErrorMap


# Create a concrete test provider for testing error wrapping
# pyright: reportPrivateUsage=false
class _StubProvider(BaseProvider[Mock]):
    """Concrete stub provider for testing base provider functionality."""

    id: ClassVar[llm.ProviderId] = "stub"
    default_scope: ClassVar[str | list[str]] = "test/"
    error_map: ClassVar[ProviderErrorMap] = {}

    def __init__(self, error_map: ProviderErrorMap | None = None) -> None:
        self.client = Mock()
        if error_map is not None:
            # Override class-level error_map for this instance
            object.__setattr__(
                self,
                "__class__",
                type(
                    "_StubProviderWithErrorMap",
                    (_StubProvider,),
                    {"error_map": error_map},
                ),
            )

    def get_error_status(self, e: Exception) -> int | None:
        return getattr(e, "status_code", None)

    # Abstract method stubs - not used in error wrapping tests
    def _call(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    async def _call_async(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def _context_call(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    async def _context_call_async(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def _stream(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    async def _stream_async(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def _context_stream(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    async def _context_stream_async(self, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError


class TestErrorWrapping:
    """Tests for the _wrap_errors context manager."""

    def test_wrap_errors_maps_to_api_error(self) -> None:
        """Test that SDK errors are mapped to APIError subclasses with status_code."""

        class SDKRateLimitError(Exception):
            status_code = 429

        provider = _StubProvider(error_map={SDKRateLimitError: llm.RateLimitError})

        with pytest.raises(llm.RateLimitError) as exc_info, provider._wrap_errors():
            error = SDKRateLimitError("Rate limit exceeded")
            error.status_code = 429
            raise error

        assert exc_info.value.status_code == 429
        assert exc_info.value.provider == "stub"
        assert "Rate limit exceeded" in str(exc_info.value)

    def test_wrap_errors_maps_to_provider_error(self) -> None:
        """Test that SDK errors are mapped to ProviderError (non-APIError) subclasses."""

        class SDKConnectionError(Exception):
            pass

        provider = _StubProvider(error_map={SDKConnectionError: llm.ConnectionError})

        with pytest.raises(llm.ConnectionError) as exc_info, provider._wrap_errors():
            raise SDKConnectionError("Connection failed")

        assert exc_info.value.provider == "stub"
        assert exc_info.value.original_exception is not None
        assert "Connection failed" in str(exc_info.value)

    def test_wrap_errors_maps_to_timeout_error(self) -> None:
        """Test that timeout errors are mapped correctly."""

        class SDKTimeoutError(Exception):
            pass

        provider = _StubProvider(error_map={SDKTimeoutError: llm.TimeoutError})

        with pytest.raises(llm.TimeoutError) as exc_info, provider._wrap_errors():
            raise SDKTimeoutError("Request timed out")

        assert exc_info.value.provider == "stub"
        assert "Request timed out" in str(exc_info.value)

    def test_wrap_errors_uses_mro_for_base_class_mapping(self) -> None:
        """Test that error_map walks MRO to find matching base class."""

        class SDKBaseError(Exception):
            pass

        class SDKSpecificError(SDKBaseError):
            pass

        # Only map the base class
        provider = _StubProvider(error_map={SDKBaseError: llm.ProviderError})

        with pytest.raises(llm.ProviderError) as exc_info, provider._wrap_errors():
            raise SDKSpecificError("Specific error")

        assert "Specific error" in str(exc_info.value)

    def test_wrap_errors_prefers_specific_mapping(self) -> None:
        """Test that more specific error mappings take precedence."""

        class SDKBaseError(Exception):
            pass

        class SDKSpecificError(SDKBaseError):
            status_code = 500

        # Map both base and specific
        provider = _StubProvider(
            error_map={
                SDKSpecificError: llm.ServerError,
                SDKBaseError: llm.ProviderError,
            }
        )

        with pytest.raises(llm.ServerError) as exc_info, provider._wrap_errors():
            error = SDKSpecificError("Server error")
            error.status_code = 500
            raise error

        assert exc_info.value.status_code == 500

    def test_wrap_errors_callable_mapping(self) -> None:
        """Test that callable error mappings work correctly."""

        class SDKError(Exception):
            def __init__(self, message: str, code: str) -> None:
                super().__init__(message)
                self.code = code
                self.status_code = 400

        def map_sdk_error(e: Exception) -> type[llm.ProviderError]:
            if isinstance(e, SDKError) and e.code == "not_found":
                return llm.NotFoundError
            return llm.BadRequestError

        provider = _StubProvider(error_map={SDKError: map_sdk_error})

        # Test not_found code maps to NotFoundError
        with pytest.raises(llm.NotFoundError), provider._wrap_errors():
            raise SDKError("Model not found", code="not_found")

        # Test other code maps to BadRequestError
        with pytest.raises(llm.BadRequestError), provider._wrap_errors():
            raise SDKError("Invalid request", code="invalid")

    def test_wrap_errors_reraises_unmapped_errors(self) -> None:
        """Test that errors not in error_map are re-raised unchanged."""
        provider = _StubProvider(error_map={})

        with pytest.raises(ValueError) as exc_info, provider._wrap_errors():
            raise ValueError("Not a provider error")

        assert str(exc_info.value) == "Not a provider error"

    def test_wrap_errors_preserves_original_exception(self) -> None:
        """Test that original_exception is set correctly."""

        class SDKError(Exception):
            pass

        provider = _StubProvider(error_map={SDKError: llm.ProviderError})

        with pytest.raises(llm.ProviderError) as exc_info, provider._wrap_errors():
            raise SDKError("Original error")

        assert exc_info.value.original_exception is not None
        assert isinstance(exc_info.value.original_exception, SDKError)
        assert str(exc_info.value.original_exception) == "Original error"

    def test_wrap_errors_sets_cause(self) -> None:
        """Test that __cause__ is set for exception chaining."""

        class SDKError(Exception):
            pass

        provider = _StubProvider(error_map={SDKError: llm.ProviderError})

        with pytest.raises(llm.ProviderError) as exc_info, provider._wrap_errors():
            raise SDKError("Original error")

        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, SDKError)

    def test_wrap_errors_no_exception(self) -> None:
        """Test that no exception is raised when code succeeds."""
        provider = _StubProvider(error_map={})

        result = None
        with provider._wrap_errors():
            result = "success"

        assert result == "success"
