"""Tests the `_utils.get_metadata` module."""

from mirascope.core.base._utils._get_metadata import get_metadata
from mirascope.core.base.metadata import Metadata
from mirascope.core.base.prompt import BasePrompt, metadata


def test_get_metadata() -> None:
    """Tests the `get_metadata` function."""

    data: Metadata = {"tags": {"version:0001"}}

    class Prompt(BasePrompt):
        """prompt"""

    assert get_metadata(Prompt, None) == {}
    assert get_metadata(metadata(data)(Prompt), None) == data
    assert get_metadata(Prompt, {"metadata": {"tags": {"version:0002"}}}) == {
        "tags": {"version:0002"}
    }

    def fn() -> None:
        """prompt"""

    assert get_metadata(fn, None) == {}
    assert get_metadata(metadata(data)(fn), None) == data
    assert get_metadata(fn, {"metadata": {"tags": {"version:0002"}}}) == {
        "tags": {"version:0002"}
    }
