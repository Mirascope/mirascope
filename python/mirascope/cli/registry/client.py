"""HTTP client for the Mirascope registry."""

from __future__ import annotations

from typing import Any

import httpx


class RegistryClient:
    """Client for fetching items from the Mirascope registry."""

    def __init__(self, base_url: str = "https://mirascope.com/registry") -> None:
        """Initialize the registry client.

        Args:
            base_url: Base URL of the registry.
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=30.0)

    def fetch_index(self) -> dict[str, Any] | None:
        """Fetch the registry index.

        Returns:
            The registry index as a dictionary, or None if not found.
        """
        url = f"{self.base_url}/r/index.json"
        try:
            response = self._client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except httpx.RequestError:
            raise

    def fetch_item(self, name: str, language: str = "python") -> dict[str, Any] | None:
        """Fetch a registry item by name.

        Args:
            name: Name of the registry item.
            language: Language version to fetch (python or typescript).

        Returns:
            The registry item as a dictionary, or None if not found.
        """
        # Handle namespaced items (e.g., @mirascope/calculator)
        if name.startswith("@"):
            # For now, strip the namespace and use the item name
            parts = name.split("/")
            if len(parts) >= 2:
                name = parts[-1]

        url = f"{self.base_url}/r/{name}.{language}.json"
        try:
            response = self._client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except httpx.RequestError:
            raise

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> RegistryClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
