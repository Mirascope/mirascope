"""URL mappings for Python builtin types and common library types.

This module provides URL mappings for Python builtin types and common library types
to their documentation pages, which can be used to enhance type information in the API docs.
"""

# Base Python documentation URL
PYTHON_DOCS_BASE = "https://docs.python.org/3/library/"

# Dictionary mapping Python builtin types to their documentation URLs
# Format: 'type_name': 'documentation_url'
BUILTIN_TYPE_URLS: dict[str, str] = {
    # Basic types
    "str": f"{PYTHON_DOCS_BASE}stdtypes.html#str",
    "int": f"{PYTHON_DOCS_BASE}functions.html#int",
    "float": f"{PYTHON_DOCS_BASE}functions.html#float",
    "bool": f"{PYTHON_DOCS_BASE}functions.html#bool",
    "bytes": f"{PYTHON_DOCS_BASE}stdtypes.html#bytes",
    "bytearray": f"{PYTHON_DOCS_BASE}stdtypes.html#bytearray",
    "memoryview": f"{PYTHON_DOCS_BASE}stdtypes.html#memoryview",
    "complex": f"{PYTHON_DOCS_BASE}functions.html#complex",
    "object": f"{PYTHON_DOCS_BASE}functions.html#object",
    "None": f"{PYTHON_DOCS_BASE}constants.html#None",
    # Sequence types
    "list": f"{PYTHON_DOCS_BASE}stdtypes.html#list",
    "tuple": f"{PYTHON_DOCS_BASE}stdtypes.html#tuple",
    "range": f"{PYTHON_DOCS_BASE}stdtypes.html#range",
    # Mapping types
    "dict": f"{PYTHON_DOCS_BASE}stdtypes.html#dict",
    # Set types
    "set": f"{PYTHON_DOCS_BASE}stdtypes.html#set",
    "frozenset": f"{PYTHON_DOCS_BASE}stdtypes.html#frozenset",
    # Other builtin types
    "type": f"{PYTHON_DOCS_BASE}functions.html#type",
    "Exception": f"{PYTHON_DOCS_BASE}exceptions.html#Exception",
    "BaseException": f"{PYTHON_DOCS_BASE}exceptions.html#BaseException",
    "StopIteration": f"{PYTHON_DOCS_BASE}exceptions.html#StopIteration",
    "GeneratorExit": f"{PYTHON_DOCS_BASE}exceptions.html#GeneratorExit",
    "KeyboardInterrupt": f"{PYTHON_DOCS_BASE}exceptions.html#KeyboardInterrupt",
    "ImportError": f"{PYTHON_DOCS_BASE}exceptions.html#ImportError",
    "ModuleNotFoundError": f"{PYTHON_DOCS_BASE}exceptions.html#ModuleNotFoundError",
    "OSError": f"{PYTHON_DOCS_BASE}exceptions.html#OSError",
    "EnvironmentError": f"{PYTHON_DOCS_BASE}exceptions.html#EnvironmentError",
    "IOError": f"{PYTHON_DOCS_BASE}exceptions.html#IOError",
    # Callable types
    "callable": f"{PYTHON_DOCS_BASE}functions.html#callable",
    # Typing module
    "Any": f"{PYTHON_DOCS_BASE}typing.html#typing.Any",
    "Union": f"{PYTHON_DOCS_BASE}typing.html#typing.Union",
    "Optional": f"{PYTHON_DOCS_BASE}typing.html#typing.Optional",
    "List": f"{PYTHON_DOCS_BASE}typing.html#typing.List",
    "Dict": f"{PYTHON_DOCS_BASE}typing.html#typing.Dict",
    "Set": f"{PYTHON_DOCS_BASE}typing.html#typing.Set",
    "FrozenSet": f"{PYTHON_DOCS_BASE}typing.html#typing.FrozenSet",
    "Tuple": f"{PYTHON_DOCS_BASE}typing.html#typing.Tuple",
    "Callable": f"{PYTHON_DOCS_BASE}typing.html#typing.Callable",
    "Type": f"{PYTHON_DOCS_BASE}typing.html#typing.Type",
    "TypeVar": f"{PYTHON_DOCS_BASE}typing.html#typing.TypeVar",
    "Generic": f"{PYTHON_DOCS_BASE}typing.html#typing.Generic",
    "Literal": f"{PYTHON_DOCS_BASE}typing.html#typing.Literal",
    "ClassVar": f"{PYTHON_DOCS_BASE}typing.html#typing.ClassVar",
    "Final": f"{PYTHON_DOCS_BASE}typing.html#typing.Final",
    "Protocol": f"{PYTHON_DOCS_BASE}typing.html#typing.Protocol",
    "Annotated": f"{PYTHON_DOCS_BASE}typing.html#typing.Annotated",
    "TypedDict": f"{PYTHON_DOCS_BASE}typing.html#typing.TypedDict",
    "NotRequired": f"{PYTHON_DOCS_BASE}typing.html#typing.NotRequired",
    "Required": f"{PYTHON_DOCS_BASE}typing.html#typing.Required",
    "Sequence": f"{PYTHON_DOCS_BASE}typing.html#typing.Sequence",
    "TypeAlias": f"{PYTHON_DOCS_BASE}typing.html#typing.TypeAlias",
    "Unpack": f"{PYTHON_DOCS_BASE}typing.html#typing.Unpack",
    "Enum": f"{PYTHON_DOCS_BASE}enum.html#enum.Enum",
    "ParamSpec": f"{PYTHON_DOCS_BASE}typing.html#typing.ParamSpec",
    # Dataclasses module
    "dataclass": f"{PYTHON_DOCS_BASE}dataclasses.html#dataclasses.dataclass",
    # Collections module
    "deque": f"{PYTHON_DOCS_BASE}collections.html#collections.deque",
    "defaultdict": f"{PYTHON_DOCS_BASE}collections.html#collections.defaultdict",
    "OrderedDict": f"{PYTHON_DOCS_BASE}collections.html#collections.OrderedDict",
    "Counter": f"{PYTHON_DOCS_BASE}collections.html#collections.Counter",
    "ChainMap": f"{PYTHON_DOCS_BASE}collections.html#collections.ChainMap",
    "namedtuple": f"{PYTHON_DOCS_BASE}collections.html#collections.namedtuple",
    # Common standard library types
    "Path": f"{PYTHON_DOCS_BASE}pathlib.html#pathlib.Path",
    "datetime": f"{PYTHON_DOCS_BASE}datetime.html#datetime.datetime",
    "date": f"{PYTHON_DOCS_BASE}datetime.html#datetime.date",
    "time": f"{PYTHON_DOCS_BASE}datetime.html#datetime.time",
    "timedelta": f"{PYTHON_DOCS_BASE}datetime.html#datetime.timedelta",
}


def get_doc_url_for_type(type_name: str) -> str | None:
    """Get the documentation URL for a given type name.

    Args:
        type_name: The name of the type to get the URL for

    Returns:
        The URL for the type's documentation, or None if not found

    """
    # Remove any quotes that might be in the type name
    clean_type_name = type_name.strip("'\"")

    # Look up in our builtin dictionary
    return BUILTIN_TYPE_URLS.get(clean_type_name)
