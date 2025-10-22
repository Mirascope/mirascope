"""Tests for llm.clients.MLXClient."""

from mirascope import llm


def test_context_manager() -> None:
    global_client = llm.get_client("mlx")
    with llm.client("mlx") as client1:
        assert client1 is global_client
        assert llm.get_client("mlx") is client1


def test_client_caching() -> None:
    client1 = llm.client("mlx")
    client2 = llm.client("mlx")

    assert client1 is client2
