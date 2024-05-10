"""Tests for the Mirascope + Langfuse integration."""
import os
from unittest.mock import MagicMock, patch

from openai.types.chat import ChatCompletion

from mirascope.langfuse import with_langfuse
from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "test"


class MyCall(OpenAICall):
    prompt_template = "test"


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@patch("mirascope.langfuse.langfuse.Langfuse", new_callable=MagicMock)
def test_call_with_langfuse(
    mock_langfuse: MagicMock,
    mock_create: MagicMock,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests that `OpenAICall.call` returns the expected response with langfuse."""
    mock_langfuse.trace = MagicMock()
    mock_create.return_value = fixture_chat_completion

    @with_langfuse
    class MyNestedCall(MyCall):
        ...

    my_call = MyNestedCall()
    my_call.call()
    assert my_call.call_params.langfuse is not None
    mock_langfuse.return_value.trace.assert_called_once()
    # mock_trace.assert_called_once()
