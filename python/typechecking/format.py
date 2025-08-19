from mirascope import llm


class InvalidFormat: ...


# These examples must both throw type errors, because InvalidFormat does not inherit
# from BaseModel.
llm.format()(InvalidFormat)  # pyright: ignore[reportArgumentType]
llm.format(InvalidFormat)  # pyright: ignore[reportArgumentType]
