"""The main methods for testing the `Closure class."""

import importlib.metadata
import inspect
import os
import random
import time
from collections.abc import Callable
from datetime import datetime
from functools import cached_property, wraps
from typing import Annotated, Any, Literal, TypeAlias, TypeVar

import httpx
import openai as oai
from openai import OpenAI as OAI
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel

import tests.ops._internal.closure_test_functions as closure_test_functions_pkg
from mirascope.ops._internal.closure import Closure

from . import other, other as oth
from .other import (
    FnInsideClass,
    ImportedClass,
    ImportedClass as IC,
    SelfFnClass,
    SubFnInsideClass,
    customer_support_bot,
    imported_fn,
    imported_fn as ifn,
)


class BaseMessageParam(BaseModel):
    """A test class for third-party imports."""

    role: str
    content: str


_T = TypeVar("_T", bound=Callable[..., Any])


def test_decorator(param: str | None = None) -> Callable[[_T], _T]:
    """A decorator that adds a test parameter to the function."""

    def decorator(func: _T) -> _T:
        func._test_param = param  # type: ignore[attr-defined]
        return func

    return decorator


def cache_result(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator that caches the result of the function."""
    from functools import wraps

    cache: dict[str, Any] = {}

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


def log_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    from functools import wraps

    func._call_count = 0  # type: ignore[attr-defined]

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func._call_count += 1  # type: ignore[attr-defined]
        return func(*args, **kwargs)

    return wrapper


GLOBAL_STATE = "skip"


class ModuleLessDependency:
    __module__ = ""

    def __init__(self, value: str) -> None:
        self.value = value


AnnotatedDependency = Annotated[ModuleLessDependency, "meta"]


# Object that raises when Python inspects its class.
class _IntrospectionGuard:
    def __init__(self) -> None:
        object.__setattr__(self, "value", "guarded")

    def __getattribute__(self, name: str):
        if name == "__class__":
            raise RuntimeError("introspection is not permitted")
        return object.__getattribute__(self, name)


INTROSPECTION_GUARD = _IntrospectionGuard()

DECORATOR_REGISTRY = [test_decorator("registry")]


class AnnotatedContainer:
    dependency: Annotated[ModuleLessDependency, "meta"]
    collection: list[ModuleLessDependency]

    def __init__(self, dependency: ModuleLessDependency) -> None:
        self.dependency = dependency
        self.collection = [dependency]


def single_fn() -> str:
    return "Hello, world!"


def sub_fn() -> str:
    return single_fn()


def inner_fn() -> str:
    def inner() -> str:
        return "Hello, world!"

    return inner()


def inner_class_fn() -> str:
    class Inner:
        def __call__(self) -> str:
            return "Hello, world!"

    return Inner()()


def inner_sub_fn() -> str:
    def inner() -> str:
        return sub_fn()

    return inner()


def built_in_fn() -> Literal["Hello, world!"]:
    return "Hello, world!"


def third_party_fn() -> BaseMessageParam:
    return BaseMessageParam(role="user", content="Hello, world!")


@test_decorator("test_param")
def decorated_fn() -> str:
    return "Hello, world!"


@cache_result
@log_calls
def multi_decorated_fn() -> None: ...


def user_defined_import_fn() -> str:
    return other.imported_fn()


def user_defined_from_import_fn() -> str:
    return imported_fn()


def user_defined_class_import_fn() -> str:
    return other.ImportedClass()()


def user_defined_class_from_import_fn() -> str:
    return ImportedClass()()


def fn_inside_class_fn() -> str:
    return FnInsideClass()()


def sub_fn_inside_class_fn() -> str:
    return SubFnInsideClass()()


def self_fn_class_fn() -> str:
    return SelfFnClass()()


def standard_import_fn() -> str:
    return os.getenv("HELLO_WORLD", "Hello, world!")


def dotted_import_fn() -> str:
    return importlib.metadata.version("mirascope")


def aliased_module_import_fn(query: str) -> str:
    client = oai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": query}]
    )
    return str(completion.choices[0].message.content)


def aliased_import_fn(query: str) -> str:
    client = OAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": query}]
    )
    return str(completion.choices[0].message.content)


def user_defined_aliased_module_import_fn() -> str:
    return oth.imported_fn()


def user_defined_aliased_module_import_class_fn() -> str:
    return oth.ImportedClass()()


def user_defined_aliased_import_fn() -> str:
    return ifn()


def user_defined_aliased_class_import_fn() -> str:
    return IC()()


def user_defined_dotted_import_fn() -> str:
    return other.imported_fn()


def user_defined_aliased_dotted_import_fn() -> str:
    return oth.imported_fn()


def annotated_input_arg_fn(var: Any) -> str:
    return str(var)


def annotated_assignment_fn() -> str:
    message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": "Hello, world!",
    }
    return str(message)


def internal_imports_fn() -> str:
    from openai import OpenAI

    from .other import imported_fn

    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": imported_fn()}]
    )
    return str(completion.choices[0].message.content)


MyType: TypeAlias = Literal["Hello, world!"]


def type_alias_fn() -> MyType:
    var: MyType = "Hello, world!"
    return var


test_config = {"api_key": "dummy", "model": "test"}


@test_decorator(param=test_config["model"])
def global_var_fn() -> str:
    return "Hello, world!"


def _decorator(fn: Callable[..., Any]) -> Callable[[], Closure]:
    @wraps(fn)
    def inner() -> Closure:
        return Closure.from_fn(fn)

    return inner


def import_with_different_dist_name_fn() -> type[httpx.Client]:
    return httpx.Client


@_decorator
def closure_inside_decorator_fn() -> str:
    return "Hello, world!"


@other.imported_decorator
def closure_inside_imported_decorator_fn() -> str:
    return "Hello, world!"


class MockClient:
    @cached_property
    def foo(self) -> str:
        return "Hello, "

    @property
    def bar(self) -> str:
        return "world!"


def closure_with_properties_fn() -> str:
    model = MockClient()
    assert isinstance(model, MockClient)
    return model.foo + model.bar


def kwarg_rich_fn(*values: int, keyword: int, **extras: int) -> int:
    global GLOBAL_STATE
    total = sum(values) + keyword + sum(extras.values())
    GLOBAL_STATE = "updated"
    return total


def registry_decorated_fn() -> str:
    @DECORATOR_REGISTRY[0]
    def inner() -> str:
        return "Hello, registry!"

    return inner()


def annotated_container_fn() -> AnnotatedContainer:
    container = AnnotatedContainer(ModuleLessDependency("value"))
    return container


def annotated_dependency_fn(payload: AnnotatedDependency) -> ModuleLessDependency:
    return payload


class MissingGetterContainer:
    value = property()


def property_missing_getter_fn() -> MissingGetterContainer:
    return MissingGetterContainer()


def fakepkg_import_fn() -> str:
    import fakepkg

    return fakepkg.__name__


def closure_with_long_function_name_that_wraps_around_fn(
    arg1: str,
    arg2: str,
) -> ChatCompletionUserMessageParam:
    return {"role": "user", "content": "Hello, world!"}


def user_defined_plain_import_fn() -> str:
    return closure_test_functions_pkg.other.SELF_REF


def nested_class_guard_fn() -> str:
    class Guarded:
        def method(self) -> str:
            return INTROSPECTION_GUARD.value

    return Guarded().method()


def datetime_fn() -> str:
    return datetime.now().strftime("%B %d, %Y")


class Response(BaseModel):
    response: str


@test_decorator(param="with_model")
def decorated_with_model_fn() -> str:
    return "Hello, world!"


def multiple_literal_fn() -> str:
    return """Hello
            World"""


def raw_string_fn() -> str:
    return r"""Hello
            World"""


def multi_joined_string_fn() -> str:
    return (
        "Hello, -----------------------------------------------------------------world!"
    )


def empty_body_fn_docstrings() -> None:
    """..."""  # noqa: D200


def nested_base_model_definitions(issue: str) -> str:
    from enum import Enum

    from pydantic import BaseModel, Field

    class TicketPriority(str, Enum):
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"
        URGENT = "Urgent"

    class TicketCategory(str, Enum):
        BUG_REPORT = "Bug Report"
        FEATURE_REQUEST = "Feature Request"

    class Ticket(BaseModel):
        issue: str
        category: TicketCategory
        priority: TicketPriority
        summary: str = Field(
            ...,
            description="A highlight summary of the most important details of the ticket.",
        )

    ticket = Ticket(
        issue=issue,
        category=TicketCategory.FEATURE_REQUEST,
        priority=TicketPriority.MEDIUM,
        summary="Test ticket",
    )
    return f"Created ticket: {ticket.summary}"


issue = inspect.cleandoc("")


def handle_issue(issue: str) -> str:
    history = []
    response = customer_support_bot(issue, history)
    return str(response)


class Chatbot:
    def __init__(self, name: str) -> None:
        self.name = name

    @test_decorator("instance_method")
    def instance_method(self) -> str:
        return f"Hello, {self.name}!"


def fn_using_time_module():
    return time.time()


def fn_using_random_module():
    return random.random()
