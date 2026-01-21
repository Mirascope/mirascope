"""Tests for SDK settings management."""

from __future__ import annotations

from mirascope.api.settings import CURRENT_SETTINGS, get_settings, settings


def test_settings_update_skips_none_values() -> None:
    """Update settings values while ignoring fields explicitly set to None."""
    initial_api_key = "initial"
    initial_base_url = "https://base"
    updated_api_key = "updated"

    with settings(api_key=initial_api_key, base_url=initial_base_url) as scoped:
        scoped.update(api_key=updated_api_key, base_url=None)
        assert scoped.api_key == updated_api_key
        assert scoped.base_url == initial_base_url


def test_settings_nested_context_restores_previous() -> None:
    """Restore outer settings after exiting a nested override."""
    outer_api_key = "outer-key"
    outer_base_url = "https://outer.example"
    inner_api_key = "inner-key"
    inner_base_url = "https://inner.example"

    original = get_settings()
    with settings(api_key=outer_api_key, base_url=outer_base_url):
        with settings(api_key=inner_api_key, base_url=inner_base_url):
            inner = get_settings()
            assert inner.api_key == inner_api_key
            assert inner.base_url == inner_base_url
        outer = get_settings()
        assert outer.api_key == outer_api_key
        assert outer.base_url == outer_base_url
    restored = get_settings()
    assert restored.api_key == original.api_key
    assert restored.base_url == original.base_url


def test_settings_context_initializes_from_default() -> None:
    """Initialize settings from defaults when no current context exists."""
    fresh_api_key = "fresh-key"
    fresh_base_url = "https://fresh.example"

    token = CURRENT_SETTINGS.set(None)
    try:
        with settings(api_key=fresh_api_key, base_url=fresh_base_url) as scoped:
            assert scoped.api_key == fresh_api_key
            assert scoped.base_url == fresh_base_url
            assert CURRENT_SETTINGS.get() is scoped
    finally:
        CURRENT_SETTINGS.reset(token)
