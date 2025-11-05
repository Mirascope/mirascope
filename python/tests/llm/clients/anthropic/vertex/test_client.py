"""Tests for AnthropicVertexClient."""

import pytest

from mirascope import llm


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""
    global_client = llm.get_client("anthropic-vertex")

    client1 = llm.client(
        "anthropic-vertex", project_id="project-1", region="asia-east1"
    )
    client2 = llm.client(
        "anthropic-vertex", project_id="project-2", region="asia-east1"
    )

    assert llm.get_client("anthropic-vertex") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("anthropic-vertex") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("anthropic-vertex") is client2

        assert llm.get_client("anthropic-vertex") is client1

    assert llm.get_client("anthropic-vertex") is global_client


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client(
        "anthropic-vertex", project_id="project-1", region="asia-east1"
    )
    client2 = llm.client(
        "anthropic-vertex", project_id="project-1", region="asia-east1"
    )
    assert client1 is client2

    client3 = llm.client(
        "anthropic-vertex", project_id="project-2", region="asia-east1"
    )
    assert client1 is not client3

    client4 = llm.client("anthropic-vertex", region="asia-east1")
    client5 = llm.client("anthropic-vertex", region="us-east1")
    assert client4 is not client5

    client6 = llm.client(
        "anthropic-vertex", project_id="project-1", region="us-central1"
    )
    client7 = llm.client("anthropic-vertex", project_id="project-1", region="us-east1")
    assert client6 is not client7

    client8 = llm.client("anthropic-vertex")
    client9 = llm.get_client("anthropic-vertex")
    assert client8 is client9


def test_client_env_var_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that client() falls back to environment variables."""
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "env-project-1")
    monkeypatch.setenv("CLOUD_ML_REGION", "us-central1")
    vertex_client = llm.client("anthropic-vertex")
    assert vertex_client.client.project_id == "env-project-1"

    monkeypatch.setenv("GCP_PROJECT_ID", "env-project-2")
    vertex_client2 = llm.client("anthropic-vertex")
    assert vertex_client2.client.project_id == "env-project-1"

    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT")
    vertex_client3 = llm.client("anthropic-vertex")
    assert vertex_client3.client.project_id == "env-project-2"

    vertex_client4 = llm.client("anthropic-vertex", project_id="test-project")
    assert vertex_client4.client.region == "us-central1"

    monkeypatch.delenv("CLOUD_ML_REGION")
    monkeypatch.setenv("GOOGLE_CLOUD_REGION", "us-west1")
    vertex_client5 = llm.client("anthropic-vertex", project_id="test-project")
    assert vertex_client5.client.region == "us-west1"
