"""Tests for OpenAIClient"""

from pathlib import Path

from mirascope import llm
from mirascope.llm.clients.openai.clients import choose_api_mode


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client(
        "openai", api_key="test-key", base_url="https://api.example.com"
    )
    client2 = llm.client(
        "openai", api_key="test-key", base_url="https://api.example.com"
    )
    assert client1 is client2

    client3 = llm.client(
        "openai",
        api_key="different-key",
        base_url="https://api.example.com",
    )
    assert client1 is not client3

    client4 = llm.client(
        "openai",
        api_key="test-key",
        base_url="https://different.example.com",
    )
    assert client1 is not client4

    client5 = llm.client("openai", api_key=None, base_url=None)
    client6 = llm.client("openai")
    assert client5 is client6


def test_choose_api_mode_explicit_completions_suffix() -> None:
    """Test that :completions suffix forces completions mode."""
    messages = [llm.messages.user("Hello")]
    assert choose_api_mode("openai/gpt-4o:completions", messages) == "completions"


def test_choose_api_mode_explicit_responses_suffix() -> None:
    """Test that :responses suffix forces responses mode."""
    messages = [llm.messages.user("Hello")]
    assert choose_api_mode("openai/gpt-4o:responses", messages) == "responses"


def test_choose_api_mode_with_audio_content() -> None:
    """Test that audio content forces completions mode."""
    audio_path = str(
        Path(__file__).parent.parent.parent.parent
        / "e2e"
        / "assets"
        / "audio"
        / "tagline.mp3"
    )
    audio = llm.Audio.from_file(audio_path)
    messages = [llm.messages.user(["Hello", audio])]
    assert choose_api_mode("openai/gpt-4o", messages) == "completions"


def test_choose_api_mode_prefers_responses_when_available() -> None:
    """Test that responses API is preferred when available and no audio."""
    messages = [llm.messages.user("Hello")]
    # gpt-4o supports responses API
    assert choose_api_mode("openai/gpt-4o", messages) == "responses"


def test_choose_api_mode_falls_back_to_completions() -> None:
    """Test that completions is used when responses not available."""
    messages = [llm.messages.user("Hello")]
    # gpt-3.5-turbo-16k doesn't have a :responses variant, only :completions
    result = choose_api_mode("openai/gpt-3.5-turbo-16k", messages)
    assert result == "completions"


def test_choose_api_mode_unknown_model() -> None:
    """Test that completions is used when responses not available."""
    messages = [llm.messages.user("Hello")]
    # When we don't have info on either api variant, we go with responses
    # (good fit for new models that we haven't tested yet)
    result = choose_api_mode("openai/new-mystery-model", messages)
    assert result == "responses"
