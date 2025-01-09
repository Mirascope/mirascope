"""Tests the `openai._utils.setup_call` module."""

import inspect
from unittest.mock import MagicMock, patch

from litellm import completion

from mirascope.core.litellm._utils._setup_call import setup_call


@patch("mirascope.core.litellm._utils._setup_call.OpenAI", new_callable=MagicMock)
@patch(
    "mirascope.core.litellm._utils._setup_call.setup_call_openai",
    new_callable=MagicMock,
)
def test_setup_call(
    mock_setup_call_openai: MagicMock,
    mock_openai: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_setup_call_openai.return_value = [MagicMock() for _ in range(5)]
    mock_openai.return_value = MagicMock()
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="gpt-4o",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )
    mock_setup_call_openai.assert_called_once_with(
        model="gpt-4o",
        client=mock_openai.return_value,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )
    assert inspect.signature(create) == inspect.signature(completion)
    assert prompt_template == mock_setup_call_openai.return_value[1]
    assert messages == mock_setup_call_openai.return_value[2]
    assert tool_types == mock_setup_call_openai.return_value[3]
    assert call_kwargs == mock_setup_call_openai.return_value[4]
