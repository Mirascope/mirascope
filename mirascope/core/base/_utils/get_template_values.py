"""This module contains the `get_template_values` function."""

from typing import Any


def get_template_values(
    template_variables: list[str], attrs: dict[str, Any]
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
    for var in template_variables:
        if var.startswith("self"):
            continue
        if "." in var:
            var = var.split(".")[0]
            values[var] = attrs.get(var)
            print(values[var])
            continue
        attr = attrs[var]
        if isinstance(attr, list):
            if len(attr) == 0:
                values[var] = ""
            elif isinstance(attr[0], list):
                values[var] = "\n\n".join(
                    ["\n".join([str(subitem) for subitem in item]) for item in attr]
                )
            else:
                values[var] = "\n".join([str(item) for item in attr])
        else:
            values[var] = str(attr)
    return values
