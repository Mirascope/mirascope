from typing import Any


def remove_invalid_title_keys_from_parameters(d: dict[str, Any] | Any) -> None:
    """
    For each property, remove the title key. However, we make sure to only remove
    the title key in each schema
    Before
    {
        "properties": {
            "books": {
                "items": {
                    "properties": {
                        "author_name": {"title": "Author Name", "type": "string"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["author_name", "title"],
                    "title": "Book",
                    "type": "object",
                },
                "title": "Books",
                "type": "array",
            }
        },
        "required": ["books"],
        "title": "Books",
        "type": "object",
    }

    AFTER
    {
        "properties": {
            "books": {
                "items": {
                    "properties": {
                        "author_name": {"type": "string"},
                        "title": {"type": "string"},
                    },
                    "required": ["author_name", "title"],
                    "type": "object",
                },
                "type": "array",
            }
        },
        "required": ["books"],
        "type": "object",
    }

    """
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == "title" and "type" in d.keys():
                del d[key]
            else:
                remove_invalid_title_keys_from_parameters(d[key])
