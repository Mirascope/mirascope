from pathlib import Path

from docs.find_missing_snippets import all_missing_snippets

PROVIDERS = [
    "anthropic",
    "azure",
    "bedrock",
    "cohere",
    "gemini",
    "google",
    "groq",
    "litellm",
    "mistral",
    "openai",
    "vertex",
    "xai",
]


def test_no_missing_snippets():
    missing_snippets = {provider: [] for provider in PROVIDERS}
    for snippet in all_missing_snippets(Path(".")):
        str_path = str(snippet.path)
        for provider in missing_snippets:
            if provider in str_path:
                missing_snippets[provider].append(snippet)
                break
    assert all(
        len(missing_snippets) == 0 for _, missing_snippets in missing_snippets.items()
    )
