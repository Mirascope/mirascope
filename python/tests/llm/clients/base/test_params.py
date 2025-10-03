"""Tests related to handling of base params."""

from typing import get_type_hints

from mirascope import llm


def test_all_params_includes_every_param() -> None:
    """Verify that the `ParmasToKwargs` utility class includes every key in `Params`.

    This is required for type safety (that adding a new key to `Params` will be handled
    or explicitly ignored by every provider).
    """

    def get_type_hint_keys(cls: type) -> set[str]:
        """Get the set of keys from a class's type hints."""
        return set(get_type_hints(cls).keys())

    params_keys = get_type_hint_keys(llm.Params)
    params_to_kwargs_keys = get_type_hint_keys(llm.clients.base._utils.ParamsToKwargs)

    assert params_keys == params_to_kwargs_keys, (
        f"ParamsToKwargs is missing parameters: {params_keys - params_to_kwargs_keys}"
    )
