"""Tests related to handling of base params."""

from typing import get_type_hints

import pytest

from mirascope import llm


def test_ensure_all_params_accessed() -> None:
    """Verify that ensure_all_params_accessed raises AssertionError when any param is not accessed.

    For each parameter in Params, create a params dict, access all parameters except one,
    and verify that exiting the context manager raises a AssertionError.
    """
    params_keys = set(get_type_hints(llm.Params).keys())
    params_keys.discard("temperature")  # Simulate one parameter being unsupported

    # Confirm failure if we skip any param
    for skipped_param in params_keys:
        with (
            pytest.raises(
                AssertionError,
                match="Mismatch between unsupported and unaccessed params",
            ),
            llm.providers.base._utils.ensure_all_params_accessed(  # pyright: ignore[reportPrivateUsage]
                params={}, provider_id="google", unsupported_params=["temperature"]
            ) as param_accessor,
        ):
            for param in params_keys:
                if param != skipped_param:
                    getattr(param_accessor, param)

    # Confirm success if we access every param
    with llm.providers.base._utils.ensure_all_params_accessed(  # pyright: ignore[reportPrivateUsage]
        params={}, provider_id="google", unsupported_params=["temperature"]
    ) as param_accessor:
        for param in params_keys:
            getattr(param_accessor, param)


def test_error_if_checking_unsupported_param() -> None:
    """Verify that ensure_all_params_accessed raises AssertionError if an unsupported param gets accessed."""
    params_keys = set(get_type_hints(llm.Params).keys())

    with (
        pytest.raises(
            AssertionError, match="Mismatch between unsupported and unaccessed params"
        ),
        llm.providers.base._utils.ensure_all_params_accessed(  # pyright: ignore[reportPrivateUsage]
            params={}, provider_id="google", unsupported_params=["temperature"]
        ) as param_accessor,
    ):
        for param in params_keys:
            getattr(param_accessor, param)
