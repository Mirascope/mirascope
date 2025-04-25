"""The `FromCallArgs` class annotation for marking a field as a call argument."""


class FromCallArgs:
    """A marker class for indicating that a field is a call argument.

    This ensures that the LLM call does not attempt to generate this field. Instead, it
    will populate this field with the call argument with a matching name.

    This is useful for colocating e.g. validation of a generated output against and
    input argument (such as the length of an output given a number input).
    """
