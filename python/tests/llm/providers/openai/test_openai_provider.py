"""Tests for OpenAIProvider"""

from pathlib import Path

from mirascope import llm
from mirascope.llm.providers.openai.provider import choose_api_mode


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
    openai_result = choose_api_mode("openai/new-mystery-model", messages)
    assert openai_result == "responses"

    third_party_result = choose_api_mode("anthropic/claude-sonnet-4-5", messages)
    assert third_party_result == "completions"
