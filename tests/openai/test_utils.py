"""Test for mirascope chat utility functions."""
import pytest

from mirascope.openai.utils import patch_openai_kwargs


def test_patch_openai_kwargs(fixture_foobar_prompt, fixture_my_tool):
    """Tests that `patch_openai_kwargs` returns the expected kwargs."""
    kwargs = {}
    patch_openai_kwargs(kwargs, fixture_foobar_prompt, [fixture_my_tool])
    assert kwargs == {
        "model": fixture_foobar_prompt.call_params.model,
        "messages": fixture_foobar_prompt.messages,
        "tools": [fixture_my_tool.tool_schema()],
        "tool_choice": "auto",
    }


def test_patch_openai_kwargs_existing_tool_choice(
    fixture_foobar_prompt, fixture_my_tool
):
    """Tests that `patch_openai_kwargs` returns the expected kwargs."""
    kwargs = {"tool_choice": {"name": "MyTool"}}
    patch_openai_kwargs(kwargs, fixture_foobar_prompt, [fixture_my_tool])
    assert kwargs == {
        "model": fixture_foobar_prompt.call_params.model,
        "messages": fixture_foobar_prompt.messages,
        "tools": [fixture_my_tool.tool_schema()],
        "tool_choice": {"name": "MyTool"},
    }


def test_patch_openai_kwargs_no_prompt_or_messages():
    """Tests that `patch_openai_kwargs` raises a ValueError with no prompt or messages."""
    kwargs = {}
    with pytest.raises(ValueError):
        patch_openai_kwargs(kwargs, None, None)
