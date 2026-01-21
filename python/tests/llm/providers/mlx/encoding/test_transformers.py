from unittest.mock import MagicMock

import pytest

from mirascope.llm.messages import system
from mirascope.llm.providers.mlx.encoding.transformers import (
    _encode_message,  # pyright: ignore[reportPrivateUsage]
)


def test_encode_message_system() -> None:
    """Test encoding a system message."""
    msg = system("sys")
    encoded = _encode_message(msg)
    assert encoded == {"role": "system", "content": "sys"}


def test_encode_message_invalid() -> None:
    """Test encoding an invalid message role."""
    # Create a mock message with an unsupported role
    mock_msg = MagicMock()
    mock_msg.role = "invalid"
    with pytest.raises(ValueError, match="Unsupported message type"):
        _encode_message(mock_msg)
