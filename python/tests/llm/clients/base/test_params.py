"""Tests related to handling of base params."""

from typing import get_type_hints

import pytest

from mirascope import llm


def test_ensure_all_params_accessed() -> None:
    """Verify that ensure_all_params_accessed raises RuntimeError when any param is not accessed.

    For each parameter in Params, create a params dict, access all parameters except one,
    and verify that exiting the context manager raises a RuntimeError.
    """
    params_keys = set(get_type_hints(llm.Params).keys())

    # Confirm failure if we skip any param
    for skipped_param in params_keys:
        with (
            pytest.raises(
                RuntimeError,
                match=f"Not all parameters were checked. Unaccessed parameters: \\['{skipped_param}'\\]",
            ),
            llm.clients.base._utils.ensure_all_params_accessed({}) as param_accessor,
        ):
            for param in params_keys:
                if param != skipped_param:
                    getattr(param_accessor, param)

    # Confirm success if we access every param
    with llm.clients.base._utils.ensure_all_params_accessed({}) as param_accessor:
        for param in params_keys:
            getattr(param_accessor, param)
