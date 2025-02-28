from pathlib import Path

from docs.find_missing_snippets import all_missing_snippets


def test_no_missing_snippets():
    missing_snippets = []
    for snippet in all_missing_snippets(Path(".")):
        str_path = str(snippet.path)
        if "xai" in str_path:
            # TODO: Remove this once the xai snippets are fixed (after finishing #811)
            continue
        if "google" in str_path and "integrations" in str_path:
            # TODO: Remove this once missing google integration snippets are added
            continue
        missing_snippets.append(snippet)  # pragma: no cover
    assert len(missing_snippets) == 0
