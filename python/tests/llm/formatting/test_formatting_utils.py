"""Tests for the formatting utils."""

from typing import cast

from pydantic import BaseModel

from mirascope import llm


def test_ensure_formattable_decorates_if_necessary() -> None:
    class Undecorated(BaseModel): ...

    format = llm.formatting._utils.ensure_formattable(Undecorated)
    assert format.name == "Undecorated"
    assert format.mode == "strict-or-tool"
    assert (
        cast(llm.formatting.Formattable, Undecorated).__mirascope_format_info__
        == format
    )


def test_ensure_formattable_doesnt_override() -> None:
    @llm.format(mode="json")
    class Decorated(BaseModel): ...

    format = llm.formatting._utils.ensure_formattable(Decorated)
    assert format.mode == "json"


def test_ensure_formattable_allows_subsequent_override() -> None:
    class Model(BaseModel): ...

    format = llm.formatting._utils.ensure_formattable(Model)
    assert format.mode == "strict-or-tool"

    llm.format(Model, mode="json")
    format = llm.formatting._utils.ensure_formattable(Model)
    assert format.mode == "json"
