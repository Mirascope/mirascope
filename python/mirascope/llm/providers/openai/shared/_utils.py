"""Shared utils for all OpenAI clients."""

from typing import cast

MODELS_WITHOUT_JSON_SCHEMA_SUPPORT = {
    "chatgpt-4o-latest",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-0125-preview",
    "gpt-4-0613",
    "gpt-4-1106-preview",
    "gpt-4-turbo",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-turbo-preview",
    "gpt-4o-2024-05-13",
    "gpt-4o-audio-preview",
    "gpt-4o-audio-preview-2024-10-01",
    "gpt-4o-audio-preview-2024-12-17",
    "gpt-4o-audio-preview-2025-06-03",
    "gpt-4o-mini-audio-preview",
    "gpt-4o-mini-audio-preview-2024-12-17",
    "gpt-5-chat-latest",
    "o1-mini",
    "o1-mini-2024-09-12",
}

MODELS_WITHOUT_JSON_OBJECT_SUPPORT = {
    "gpt-4",
    "gpt-4-0613",
    "gpt-4o-audio-preview",
    "gpt-4o-audio-preview-2024-10-01",
    "gpt-4o-audio-preview-2024-12-17",
    "gpt-4o-audio-preview-2025-06-03",
    "gpt-4o-mini-audio-preview",
    "gpt-4o-mini-audio-preview-2024-12-17",
    "gpt-4o-mini-search-preview",
    "gpt-4o-mini-search-preview-2025-03-11",
    "gpt-4o-search-preview",
    "gpt-4o-search-preview-2025-03-11",
    "o1-mini",
    "o1-mini-2024-09-12",
}


def ensure_additional_properties_false(obj: object) -> None:
    """Recursively adds additionalProperties = False to a schema, required by OpenAI API."""
    if isinstance(obj, dict):
        obj = cast(dict[str, object], obj)
        if obj.get("type") == "object" and "additionalProperties" not in obj:
            obj["additionalProperties"] = False
        for value in obj.values():
            ensure_additional_properties_false(value)
    elif isinstance(obj, list):
        obj = cast(list[object], obj)
        for item in obj:
            ensure_additional_properties_false(item)
