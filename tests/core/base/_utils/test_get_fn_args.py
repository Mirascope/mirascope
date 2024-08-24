"""Tests the `_utils.get_fn_args` module."""

from mirascope.core.base._utils._get_fn_args import get_fn_args


def test_get_fn_args() -> None:
    """Tests the `get_fn_args` function."""

    def fn(a: int, b: str, c: list[int], d: dict[str, str], **kwargs) -> None:
        """Dummy fn."""

    args = (1, "2", [3, 4], {"5": "6"})
    kwargs = {}
    assert get_fn_args(fn, args, kwargs) == {
        "a": 1,
        "b": "2",
        "c": [3, 4],
        "d": {"5": "6"},
    }

    args = (1, "2")
    kwargs = {"c": [3, 4], "d": {"5": "6"}}
    assert get_fn_args(fn, args, kwargs) == {
        "a": 1,
        "b": "2",
        "c": [3, 4],
        "d": {"5": "6"},
    }

    args = (1,)
    kwargs = {"b": "2", "c": [3, 4], "d": {"5": "6"}}
    assert get_fn_args(fn, args, kwargs) == {
        "a": 1,
        "b": "2",
        "c": [3, 4],
        "d": {"5": "6"},
    }

    args = ()
    kwargs = {"a": 1, "b": "2", "c": [3, 4], "d": {"5": "6"}, "e": 7}
    assert get_fn_args(fn, args, kwargs) == {
        "a": 1,
        "b": "2",
        "c": [3, 4],
        "d": {"5": "6"},
        "e": 7,
    }
