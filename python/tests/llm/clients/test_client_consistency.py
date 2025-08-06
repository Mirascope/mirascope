"""Shared tests that run against all LLM clients with provider-specific snapshots."""

import os

import pytest
from dotenv import load_dotenv
from inline_snapshot import snapshot

from mirascope import llm


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration for shared client tests."""
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": [
            # OpenAI
            "authorization",
            # Anthropic
            "x-api-key",
            "anthropic-organization-id",
            # Google
            "x-goog-api-key",
        ],
        "filter_post_data_parameters": [],
    }


CLIENTS = [
    (
        "anthropic",
        "ANTHROPIC_API_KEY",
        llm.clients.AnthropicClient,
        "claude-3-5-sonnet-latest",
    ),
    ("openai", "OPENAI_API_KEY", llm.clients.OpenAIClient, "gpt-4o-mini"),
    ("google", "GOOGLE_API_KEY", llm.clients.GoogleClient, "gemini-2.0-flash"),
]


def create_client_instances():
    """Create all client instances with appropriate API keys."""
    load_dotenv()
    clients = {}
    for name, env_var, client_class, model in CLIENTS:
        api_key = os.getenv(env_var) or "dummy-key-for-vcr-tests"
        clients[name] = (client_class(api_key=api_key), model)
    return clients


def run_test_across_clients(messages, client_subset=None):
    """Run a test across all clients and collect responses."""
    clients = create_client_instances()
    if client_subset:
        clients = {k: v for k, v in clients.items() if k in client_subset}

    results = {}
    for client_name, (client, model) in clients.items():
        response = client.call(model=model, messages=messages)
        results[client_name] = response.pretty()

    return results


@pytest.mark.vcr()
def test_simple_greeting_message():
    """Test basic greeting across all clients."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]
    results = run_test_across_clients(messages)

    assert results == snapshot(
        {
            "anthropic": "Hi! How are you today?",
            "google": "Hi!",
            "openai": "Hi! How can I assist you today?",
        }
    )


@pytest.mark.vcr()
def test_system_message_override():
    """Test system message behavior across all clients."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]
    results = run_test_across_clients(messages)

    assert results == snapshot(
        {
            "anthropic": "Hello world",
            "google": "Hello world",
            "openai": "Hello world.",
        }
    )


@pytest.mark.vcr()
def test_multiple_system_messages(caplog):
    """Test handling of multiple system messages."""
    messages = [
        llm.messages.system("Respond only in Spanish."),
        llm.messages.system("Also, respond in ALL CAPS with ENTHUSIASM."),
        llm.messages.user("How are you doing today?"),
    ]

    results = run_test_across_clients(messages)

    warning_messages = [
        record.message for record in caplog.records if record.levelname == "WARNING"
    ]
    expected_warnings = (
        2  # Expect warnings from anthropic and google clients (but not openai)
    )
    assert len(warning_messages) == expected_warnings
    for warning in warning_messages:
        assert "Skipping system message at index 1" in warning

    assert (
        results
        == snapshot(
            {
                "anthropic": "¡Hola! Estoy muy bien, gracias por preguntar. ¿Y tú? ¿Cómo te encuentras hoy?",  # codespell:ignore te
                "openai": "¡ESTOY MUY BIEN, GRACIAS POR PREGUNTAR! ¡¿Y TÚ?! ",
                "google": "Estoy funcionando de maravilla. ¿Cómo puedo ayudarte hoy?",
            }
        )
    )
