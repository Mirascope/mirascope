"""List command - List available registry items."""

from __future__ import annotations

import sys


def run_list(
    item_type: str | None,
    registry_url: str,
) -> int:
    """List available registry items.

    Args:
        item_type: Filter by item type (tool, agent, prompt, integration).
        registry_url: URL of the registry to list items from.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    from mirascope.cli.registry.client import RegistryClient

    client = RegistryClient(registry_url)

    try:
        index = client.fetch_index()
    except Exception as e:
        print(f"Error: Failed to fetch registry index: {e}", file=sys.stderr)
        return 1

    if index is None:
        print("Error: Could not fetch registry index.", file=sys.stderr)
        return 1

    items = index.get("items", [])

    # Filter by type if specified
    if item_type:
        items = [i for i in items if i.get("type") == item_type]

    if not items:
        if item_type:
            print(f"No items found with type '{item_type}'.")
        else:
            print("No items found in registry.")
        return 0

    # Group by type
    by_type: dict[str, list[dict[str, str]]] = {}
    for item in items:
        t = item.get("type", "other")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(item)

    print(f"Available items from {registry_url}:\n")

    for type_name, type_items in sorted(by_type.items()):
        print(f"{type_name.title()}s:")
        for item in type_items:
            name = item.get("name", "unknown")
            desc = item.get("description", "")
            print(f"  {name:<20} {desc}")
        print()

    print("Use `mirascope add <name>` to install.")
    return 0
