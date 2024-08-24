"""This module contains the `get_template_values` function."""

from typing import Any


def get_template_values(
    template_variables: list[tuple[str, str | None]], attrs: dict[str, Any]
) -> dict[str, Any]:
    """Returns the values of the given `template_variables` from the provided `attrs`.

    Args:
        template_variables: The variables to extract from the `attrs`.
        attrs: The attributes to extract the variables from.

    Returns:
        The values of the template variables.
    """
    values = {}
    if "self" in attrs:
        values["self"] = attrs.get("self")
    for var, format_spec in template_variables:
        if var.startswith("self"):
            values["self"] = attrs.get("self")
        elif "." in var:
            var = var.split(".")[0]
            values[var] = attrs.get(var)
            continue
        elif format_spec in ["list", "lists"]:
            value = attrs[var]
            if format_spec == "list":
                if not isinstance(value, list):
                    raise ValueError(
                        f"Template variable '{var}' must be a list when using the "
                        "'list' format spec."
                    )
                values[var] = "\n".join([str(item) for item in attrs[var]])
            else:
                if not isinstance(value, list) or (
                    value
                    and not all(isinstance(item, list | tuple | set) for item in value)
                ):
                    raise ValueError(
                        f"Template variable '{var}' must be a list of lists when using "
                        "the 'lists' format spec."
                    )
                values[var] = "\n\n".join(
                    ["\n".join([str(subitem) for subitem in item]) for item in value]
                )
        else:
            values[var] = attrs[var] if attrs[var] is not None else ""
    return values
