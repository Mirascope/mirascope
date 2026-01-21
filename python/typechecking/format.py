from mirascope import llm


class InvalidFormat: ...


llm.format(InvalidFormat, mode="tool")  # pyright: ignore[reportArgumentType]
