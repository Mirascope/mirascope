import ast
import importlib.util

import pytest

from examples.cookbook.agents.documentation_agent.agent import (
    DocumentationAgent,
    llm_query_rerank,
)
from examples.cookbook.agents.documentation_agent.documents import (
    retrieved_dummy_docs,
    retrieved_mirascope_docs,
    retrieved_mirascope_ollama_docs,
    retrieved_mirascope_openai_docs,
)


def check_syntax(code_string: str) -> bool:
    try:
        compile(code_string, "<string>", "exec")
        return True
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False


def is_importable(code_string: str) -> bool:
    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom):
            module_name = (
                node.module if isinstance(node, ast.ImportFrom) else node.names[0].name
            )
            if not check_module(module_name):
                return False

            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if not check_attribute(module_name, alias.name):
                        return False

    return True


def check_module(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, AttributeError, ValueError):
        return False


def check_attribute(module_name, attribute):
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        module = importlib.util.module_from_spec(spec)
        if spec.loader:
            spec.loader.exec_module(module)
        return hasattr(module, attribute)
    except (ImportError, AttributeError):
        return False


@pytest.mark.parametrize(
    "import_str,expected",
    [
        ("from mirascope.core import openai", True),
        ("import math", True),
        ("from datetime import datetime", True),
        ("import non_existent_module", False),
        ("from os import path, nonexistent_function", False),
        ("from sys import exit, nonexistent_variable", False),
        ("from openai import OpenAI", True),
        ("from mirascope.core import openai", True),
    ],
)
def test_is_importable(import_str: str, expected: bool):
    assert is_importable(import_str) == expected


@pytest.mark.parametrize(
    "syntax,expected",
    [("print('Hello, World!')", True), ("print('Hello, World!'", False)],
)
def test_check_syntax(syntax: str, expected: bool):
    assert check_syntax(syntax) == expected


batch_query_rerank_golden_dataset = [
    ("What is Bob's favorite food", retrieved_dummy_docs, {3, 0}),
    (
        "How do I make a basic OpenAI call using Mirascope?",
        retrieved_mirascope_openai_docs,
        {4, 1, 5, 6, 0},
    ),
    (
        "Can you write me code for making a Mirascope call?",
        retrieved_mirascope_docs,
        {0, 1},
    ),
    (
        "How do I use an Ollama Custom Client instead of OpenAI client?",
        retrieved_mirascope_ollama_docs,
        {0, 9},
    ),
]


@pytest.mark.parametrize(
    "query,documents,top_n_ids",
    batch_query_rerank_golden_dataset,
)
def test_llm_query_rerank(query: str, documents: list[dict], top_n_ids: set[int]):
    """Tests that the LLM query rerank ranks more relevant documents higher."""
    response = llm_query_rerank(documents, query)
    results = sorted(response, key=lambda x: x.score or 0, reverse=True)
    assert all(result.score > 5 for result in results)
    assert top_n_ids.issuperset({result.id for result in results[: len(top_n_ids)]})


@pytest.mark.parametrize(
    "query,expected",
    [
        ("How do I make a basic OpenAI call using Mirascope?", None),
        ("What is Mirascope?", "a toolkit for building AI-powered applications"),
    ],
)
def test_documentation_agent(query: str, expected: str):
    documentation_agent = DocumentationAgent()
    response = documentation_agent._call(query)
    if response.classification == "code":
        assert check_syntax(response.content) and is_importable(response.content)
    else:
        assert expected in response.content
