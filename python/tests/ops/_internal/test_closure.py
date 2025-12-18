"""Tests for the `Closure` class"""

import os
import subprocess
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from inline_snapshot import snapshot

from mirascope.ops._internal.closure import Closure, get_qualified_name
from mirascope.ops.exceptions import ClosureComputationError

from .closure_test_functions import (
    aliased_import_fn,
    aliased_module_import_fn,
    annotated_assignment_fn,
    annotated_container_fn,
    annotated_dependency_fn,
    annotated_input_arg_fn,
    built_in_fn,
    closure_inside_decorator_fn,
    closure_inside_imported_decorator_fn,
    closure_with_long_function_name_that_wraps_around_fn,
    closure_with_properties_fn,
    datetime_fn,
    decorated_fn,
    decorated_with_model_fn,
    dotted_import_fn,
    fakepkg_import_fn,
    fn_inside_class_fn,
    global_var_fn,
    import_with_different_dist_name_fn,
    inner_class_fn,
    inner_fn,
    inner_sub_fn,
    internal_imports_fn,
    kwarg_rich_fn,
    multi_decorated_fn,
    nested_class_guard_fn,
    property_missing_getter_fn,
    registry_decorated_fn,
    self_fn_class_fn,
    single_fn,
    standard_import_fn,
    sub_fn,
    sub_fn_inside_class_fn,
    third_party_fn,
    type_alias_fn,
    user_defined_aliased_class_import_fn,
    user_defined_aliased_dotted_import_fn,
    user_defined_aliased_import_fn,
    user_defined_aliased_module_import_class_fn,
    user_defined_aliased_module_import_fn,
    user_defined_class_from_import_fn,
    user_defined_class_import_fn,
    user_defined_dotted_import_fn,
    user_defined_from_import_fn,
    user_defined_import_fn,
    user_defined_plain_import_fn,
)
from .closure_test_functions.main import (
    Chatbot,
    empty_body_fn_docstrings,
    fn_using_random_module,
    fn_using_time_module,
    handle_issue,
    multi_joined_string_fn,
    multiple_literal_fn,
    nested_base_model_definitions,
    raw_string_fn,
)


def test_single_fn() -> None:
    """Test the `Closure` class with a single function."""
    closure = Closure.from_fn(single_fn)
    assert closure.code == snapshot(
        """\
def single_fn() -> str:
    return "Hello, world!"
"""
    )
    assert closure.dependencies == snapshot({})


def test_sub_fn() -> None:
    """Test the `Closure` class with a sub function."""
    closure = Closure.from_fn(sub_fn)
    assert closure.code == snapshot(
        """\
def single_fn() -> str:
    return "Hello, world!"


def sub_fn() -> str:
    return single_fn()
"""
    )
    assert closure.dependencies == snapshot({})


def test_inner_fn() -> None:
    """Test the `Closure` class with an inner function."""
    closure = Closure.from_fn(inner_fn)
    assert closure.code == snapshot(
        """\
def inner_fn() -> str:
    def inner() -> str:
        return "Hello, world!"

    return inner()
"""
    )
    assert closure.dependencies == snapshot({})


def test_inner_class_fn() -> None:
    """Test the `Closure` class with an inner class."""
    closure = Closure.from_fn(inner_class_fn)
    assert closure.code == snapshot(
        """\
def inner_class_fn() -> str:
    class Inner:
        def __call__(self) -> str:
            return "Hello, world!"

    return Inner()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_inner_sub_fn() -> None:
    """Test the `Closure` class with an inner method."""
    closure = Closure.from_fn(inner_sub_fn)
    assert closure.code == snapshot(
        """\
def single_fn() -> str:
    return "Hello, world!"


def sub_fn() -> str:
    return single_fn()


def inner_sub_fn() -> str:
    def inner() -> str:
        return sub_fn()

    return inner()
"""
    )
    assert closure.dependencies == snapshot({})


def test_built_in_fn() -> None:
    """Test the `Closure` class with a built-in function."""
    closure = Closure.from_fn(built_in_fn)
    assert closure.code == snapshot(
        """\
from typing import Literal


def built_in_fn() -> Literal["Hello, world!"]:
    return "Hello, world!"
"""
    )
    assert closure.dependencies == snapshot({})


def test_third_party_fn() -> None:
    """Test the `Closure` class with a third-party function."""
    closure = Closure.from_fn(third_party_fn)
    assert closure.code == snapshot(
        """\
from pydantic import BaseModel


class BaseMessageParam(BaseModel):
    role: str
    content: str


def third_party_fn() -> BaseMessageParam:
    return BaseMessageParam(role="user", content="Hello, world!")
"""
    )
    assert closure.dependencies == snapshot(
        {"pydantic": {"version": "2.11.5", "extras": None}}
    )


def test_decorated_fn() -> None:
    """Test the `Closure` class with a decorated function."""
    closure = Closure.from_fn(decorated_fn)
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from typing import Any, TypeVar

_T = TypeVar("_T", bound=Callable[..., Any])


def test_decorator(param: str | None = None) -> Callable[[_T], _T]:
    def decorator(func: _T) -> _T:
        func._test_param = param  # type: ignore[attr-defined]
        return func

    return decorator


@test_decorator("test_param")
def decorated_fn() -> str:
    return "Hello, world!"
"""
    )
    assert closure.dependencies == snapshot({})


def test_multi_decorated_fn() -> None:
    """Test the `Closure` class with a multi-decorated function."""
    closure = Closure.from_fn(multi_decorated_fn)
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from typing import Any


def log_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    from functools import wraps

    func._call_count = 0  # type: ignore[attr-defined]

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func._call_count += 1  # type: ignore[attr-defined]
        return func(*args, **kwargs)

    return wrapper


def cache_result(func: Callable[..., Any]) -> Callable[..., Any]:
    from functools import wraps

    cache: dict[str, Any] = {}

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


@cache_result
@log_calls
def multi_decorated_fn() -> None: ...
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_import_fn() -> None:
    """Test the `Closure` class with a user-defined import."""
    closure = Closure.from_fn(user_defined_import_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def user_defined_import_fn() -> str:
    return imported_fn()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_from_import_fn() -> None:
    """Test the `Closure` class with a user-defined from import."""
    closure = Closure.from_fn(user_defined_from_import_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def user_defined_from_import_fn() -> str:
    return imported_fn()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_class_import_fn() -> None:
    """Test the `Closure` class with a user-defined class import."""
    closure = Closure.from_fn(user_defined_class_import_fn)
    assert closure.code == snapshot(
        """\
class ImportedClass:
    def __call__(self) -> str:
        return "Hello, world!"


def user_defined_class_import_fn() -> str:
    return ImportedClass()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_class_from_import_fn() -> None:
    """Test the `Closure` class with a user-defined class from import."""
    closure = Closure.from_fn(user_defined_class_from_import_fn)
    assert closure.code == snapshot(
        """\
class ImportedClass:
    def __call__(self) -> str:
        return "Hello, world!"


def user_defined_class_from_import_fn() -> str:
    return ImportedClass()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_plain_import_fn() -> None:
    """Test user-defined plain import handling."""
    closure = Closure.from_fn(user_defined_plain_import_fn)
    assert closure.code == snapshot(
        """\
import tests.ops._internal.closure_test_functions as closure_test_functions_pkg


def user_defined_plain_import_fn() -> str:
    return closure_test_functions_pkg.other.SELF_REF
"""
    )
    assert closure.dependencies == snapshot({})


def test_fn_inside_class_fn() -> None:
    """Test the `Closure` class with a function inside a class."""
    closure = Closure.from_fn(fn_inside_class_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


class FnInsideClass:
    def __call__(self) -> str:
        return imported_fn()


def fn_inside_class_fn() -> str:
    return FnInsideClass()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_sub_fn_inside_class_fn() -> None:
    """Test the `Closure` class with a sub function inside a class."""
    closure = Closure.from_fn(sub_fn_inside_class_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def imported_sub_fn() -> str:
    return imported_fn()


class SubFnInsideClass:
    def __call__(self) -> str:
        return imported_sub_fn()


def sub_fn_inside_class_fn() -> str:
    return SubFnInsideClass()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_self_fn_class_fn() -> None:
    """Test the `Closure` class with a method inside a class."""
    closure = Closure.from_fn(self_fn_class_fn)
    assert closure.code == snapshot(
        """\
class SelfFnClass:
    def fn(self) -> str:
        return "Hello, world!"

    def __call__(self) -> str:
        return self.fn()


def self_fn_class_fn() -> str:
    return SelfFnClass()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_nested_class_guard_fn() -> None:
    """Ensure nested class methods remain intact when GC inspection fails."""
    closure = Closure.from_fn(nested_class_guard_fn)
    assert closure.code == snapshot(
        """\
INTROSPECTION_GUARD = _IntrospectionGuard()


def nested_class_guard_fn() -> str:
    class Guarded:
        def method(self) -> str:
            return INTROSPECTION_GUARD.value

    return Guarded().method()
"""
    )
    assert closure.dependencies == snapshot({})


def test_standard_import_fn() -> None:
    """Test the `Closure` class with a standard import."""
    closure = Closure.from_fn(standard_import_fn)
    assert closure.code == snapshot(
        """\
import os


def standard_import_fn() -> str:
    return os.getenv("HELLO_WORLD", "Hello, world!")
"""
    )
    assert closure.dependencies == snapshot({})


def test_dot_import_fn() -> None:
    """Test the `Closure` class with a dotted import."""
    closure = Closure.from_fn(dotted_import_fn)
    assert closure.code == snapshot(
        """\
import importlib.metadata


def dotted_import_fn() -> str:
    return importlib.metadata.version("mirascope")
"""
    )
    assert closure.dependencies == snapshot({})


def test_aliased_module_import_fn() -> None:
    """Test the `Closure` class with an aliased module import."""
    closure = Closure.from_fn(aliased_module_import_fn)
    assert closure.code == snapshot(
        """\
import openai as oai


def aliased_module_import_fn(query: str) -> str:
    client = oai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": query}]
    )
    return str(completion.choices[0].message.content)
"""
    )
    assert closure.dependencies == snapshot(
        {"openai": {"version": "2.7.1", "extras": None}}
    )


def test_aliased_import_fn() -> None:
    """Test the `Closure` class with an aliased import."""
    closure = Closure.from_fn(aliased_import_fn)
    assert closure.code == snapshot(
        """\
from openai import OpenAI as OAI


def aliased_import_fn(query: str) -> str:
    client = OAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": query}]
    )
    return str(completion.choices[0].message.content)
"""
    )
    assert closure.dependencies == snapshot(
        {"openai": {"version": "2.7.1", "extras": None}}
    )


def test_user_defined_aliased_module_import_fn() -> None:
    """Test the `Closure` class with a user-defined aliased module import."""
    closure = Closure.from_fn(user_defined_aliased_module_import_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def user_defined_aliased_module_import_fn() -> str:
    return imported_fn()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_aliased_module_import_class_fn() -> None:
    """Test the `Closure` class with a user-defined aliased module import."""
    closure = Closure.from_fn(user_defined_aliased_module_import_class_fn)
    assert closure.code == snapshot(
        """\
class ImportedClass:
    def __call__(self) -> str:
        return "Hello, world!"


def user_defined_aliased_module_import_class_fn() -> str:
    return ImportedClass()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_aliased_import_fn() -> None:
    """Test the `Closure` class with a user-defined aliased import."""
    closure = Closure.from_fn(user_defined_aliased_import_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def user_defined_aliased_import_fn() -> str:
    return imported_fn()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_aliased_class_import_fn() -> None:
    """Test the `Closure` class with a user-defined aliased class import."""
    closure = Closure.from_fn(user_defined_aliased_class_import_fn)
    assert closure.code == snapshot(
        """\
class ImportedClass:
    def __call__(self) -> str:
        return "Hello, world!"


def user_defined_aliased_class_import_fn() -> str:
    return ImportedClass()()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_dotted_import_fn() -> None:
    """Test the `Closure` class with a user-defined dotted import."""
    closure = Closure.from_fn(user_defined_dotted_import_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def user_defined_dotted_import_fn() -> str:
    return imported_fn()
"""
    )
    assert closure.dependencies == snapshot({})


def test_user_defined_aliased_dotted_import_fn() -> None:
    """Test the `Closure` class with a user-defined aliased dotted import."""
    closure = Closure.from_fn(user_defined_aliased_dotted_import_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def user_defined_aliased_dotted_import_fn() -> str:
    return imported_fn()
"""
    )
    assert closure.dependencies == snapshot({})


def test_annotated_input_arg_fn() -> None:
    """Test the `Closure` class with an annotated input argument."""
    closure = Closure.from_fn(annotated_input_arg_fn)
    assert closure.code == snapshot(
        """\
from typing import Any


def annotated_input_arg_fn(var: Any) -> str:
    return str(var)
"""
    )
    assert closure.dependencies == snapshot({})


def test_annotated_assignment_fn() -> None:
    """Test the `Closure` class with an annotated assignment."""
    closure = Closure.from_fn(annotated_assignment_fn)
    assert closure.code == snapshot(
        """\
from openai.types.chat import ChatCompletionUserMessageParam


def annotated_assignment_fn() -> str:
    message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": "Hello, world!",
    }
    return str(message)
"""
    )
    assert closure.dependencies == snapshot(
        {"openai": {"version": "2.7.1", "extras": None}}
    )


def test_internal_imports_fn() -> None:
    """Test the `Closure` class with internal imports."""
    closure = Closure.from_fn(internal_imports_fn)
    assert closure.code == snapshot(
        """\
def imported_fn() -> str:
    return "Hello, world!"


def internal_imports_fn() -> str:
    from openai import OpenAI

    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": imported_fn()}]
    )
    return str(completion.choices[0].message.content)
"""
    )
    assert closure.dependencies == snapshot(
        {"openai": {"version": "2.7.1", "extras": None}}
    )


def test_type_alias_fn() -> None:
    """Test the `Closure` class with a type alias."""
    closure = Closure.from_fn(type_alias_fn)
    assert closure.code == snapshot(
        """\
from typing import Literal, TypeAlias

MyType: TypeAlias = Literal["Hello, world!"]


def type_alias_fn() -> MyType:
    var: MyType = "Hello, world!"
    return var
"""
    )
    assert closure.dependencies == snapshot({})


def test_global_var_fn() -> None:
    """Test the `Closure` class with a global variable."""
    closure = Closure.from_fn(global_var_fn)
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from typing import Any, TypeVar

test_config = {"api_key": "dummy", "model": "test"}
_T = TypeVar("_T", bound=Callable[..., Any])


def test_decorator(param: str | None = None) -> Callable[[_T], _T]:
    def decorator(func: _T) -> _T:
        func._test_param = param  # type: ignore[attr-defined]
        return func

    return decorator


@test_decorator(param=test_config["model"])
def global_var_fn() -> str:
    return "Hello, world!"
"""
    )
    assert closure.dependencies == snapshot({})


def test_import_with_different_dist_name_fn() -> None:
    """Test the `Closure` class with third-party package imports."""
    closure = Closure.from_fn(import_with_different_dist_name_fn)
    assert closure.code == snapshot(
        """\
import httpx


def import_with_different_dist_name_fn() -> type[httpx.Client]:
    return httpx.Client
"""
    )
    assert closure.dependencies == snapshot(
        {"httpx": {"version": "0.28.1", "extras": None}}
    )


def test_closure_inside_decorator_fn() -> None:
    """Test the `Closure` class inside a decorator."""
    closure = closure_inside_decorator_fn()
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from functools import wraps
from typing import Any

from mirascope.ops._internal.closure import Closure


def _decorator(fn: Callable[..., Any]) -> Callable[[], Closure]:
    @wraps(fn)
    def inner() -> Closure:
        return Closure.from_fn(fn)

    return inner


@_decorator
def closure_inside_decorator_fn() -> str:
    return "Hello, world!"
"""
    )
    assert closure.dependencies == snapshot(
        {
            "mirascope": {
                "version": "2.0.0a4",
                "extras": ["all"],
            }
        }
    )


def test_closure_inside_imported_decorator_fn() -> None:
    """Test the `Closure` class inside an imported decorator."""
    closure = closure_inside_imported_decorator_fn()
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from functools import wraps

from mirascope.ops._internal.closure import Closure


def imported_decorator(fn: Callable[..., str]) -> Callable[[], Closure]:
    @wraps(fn)
    def inner() -> Closure:
        return Closure.from_fn(fn)

    return inner


@imported_decorator
def closure_inside_imported_decorator_fn() -> str:
    return "Hello, world!"
"""
    )
    assert closure.dependencies == snapshot(
        {
            "mirascope": {
                "version": "2.0.0a4",
                "extras": ["all"],
            }
        }
    )


def test_closure_with_properties_fn() -> None:
    """Test the fn with properties."""
    closure = Closure.from_fn(closure_with_properties_fn)
    assert closure.code == snapshot(
        """\
from functools import cached_property


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
"""
    )
    assert closure.dependencies == snapshot({})


def test_kwarg_rich_fn_handles_variadic_parameters() -> None:
    """Test the closure preserves globals when variadic args are used."""
    closure = Closure.from_fn(kwarg_rich_fn)
    assert closure.code == snapshot(
        """\
def kwarg_rich_fn(*values: int, keyword: int, **extras: int) -> int:
    global GLOBAL_STATE
    total = sum(values) + keyword + sum(extras.values())
    GLOBAL_STATE = "updated"
    return total
"""
    )
    assert closure.dependencies == snapshot({})


def test_registry_decorated_fn_handles_subscript_decorator() -> None:
    """Ensure decorators accessed via subscription are handled."""
    Closure.from_fn.cache_clear()
    closure = Closure.from_fn(registry_decorated_fn)
    assert closure.code == snapshot(
        """\
DECORATOR_REGISTRY = [test_decorator("registry")]


def registry_decorated_fn() -> str:
    @DECORATOR_REGISTRY[0]
    def inner() -> str:
        return "Hello, registry!"

    return inner()
"""
    )
    assert closure.dependencies == snapshot({})


def test_annotated_container_fn_collects_types() -> None:
    """Ensure class annotations using Annotated are preserved."""
    Closure.from_fn.cache_clear()
    closure = Closure.from_fn(annotated_container_fn)
    assert closure.code == snapshot(
        """\
from typing import Annotated


class AnnotatedContainer:
    dependency: Annotated[ModuleLessDependency, "meta"]
    collection: list[ModuleLessDependency]

    def __init__(self, dependency: ModuleLessDependency) -> None:
        self.dependency = dependency
        self.collection = [dependency]


def annotated_container_fn() -> AnnotatedContainer:
    container = AnnotatedContainer(ModuleLessDependency("value"))
    return container
"""
    )
    assert closure.dependencies == snapshot({})


def test_annotated_dependency_fn_uses_custom_type() -> None:
    """Test the closure retains annotated dependency types."""
    closure = Closure.from_fn(annotated_dependency_fn)
    assert closure.code == snapshot(
        """\
from typing import Annotated

AnnotatedDependency = Annotated[ModuleLessDependency, "meta"]


def annotated_dependency_fn(payload: AnnotatedDependency) -> ModuleLessDependency:
    return payload
"""
    )
    assert closure.dependencies == snapshot({})


def test_property_missing_getter_fn_skips_definition() -> None:
    """Test the closure skips properties without getters."""
    closure = Closure.from_fn(property_missing_getter_fn)
    assert closure.code == snapshot(
        """\
class MissingGetterContainer:
    value = property()


def property_missing_getter_fn() -> MissingGetterContainer:
    return MissingGetterContainer()
"""
    )
    assert closure.dependencies == snapshot({})


def test_fakepkg_import_fn_skips_missing_distribution() -> None:
    """Ensure dependency collection skips modules without distributions."""
    Closure.from_fn.cache_clear()
    closure = Closure.from_fn(fakepkg_import_fn)
    Closure.from_fn.cache_clear()
    assert closure.dependencies == snapshot({})


def test_closure_with_long_function_name_that_wraps_around_fn() -> None:
    """Test the `Closure` class with a long function name that wraps around."""
    closure = Closure.from_fn(closure_with_long_function_name_that_wraps_around_fn)
    assert closure.code == snapshot(
        """\
from openai.types.chat import ChatCompletionUserMessageParam


def closure_with_long_function_name_that_wraps_around_fn(
    arg1: str,
    arg2: str,
) -> ChatCompletionUserMessageParam:
    return {"role": "user", "content": "Hello, world!"}
"""
    )
    assert closure.signature == snapshot(
        """\
def closure_with_long_function_name_that_wraps_around_fn(
    arg1: str,
    arg2: str,
) -> ChatCompletionUserMessageParam: ...\
"""
    )


def test_datetime() -> None:
    """Test the `Closure` class with a datetime function."""
    closure = Closure.from_fn(datetime_fn)
    assert closure.code == snapshot(
        """\
from datetime import datetime


def datetime_fn() -> str:
    return datetime.now().strftime("%B %d, %Y")
"""
    )
    assert closure.dependencies == snapshot({})


def test_decorated_with_model_fn() -> None:
    """Test the `Closure` class with a decorator that has a model parameter."""
    closure = Closure.from_fn(decorated_with_model_fn)
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from typing import Any, TypeVar

_T = TypeVar("_T", bound=Callable[..., Any])


def test_decorator(param: str | None = None) -> Callable[[_T], _T]:
    def decorator(func: _T) -> _T:
        func._test_param = param  # type: ignore[attr-defined]
        return func

    return decorator


@test_decorator(param="with_model")
def decorated_with_model_fn() -> str:
    return "Hello, world!"
"""
    )
    assert closure.dependencies == snapshot({})


def test_multiple_literal_fn() -> None:
    """Test the `Closure` class with multiple literal functions."""
    closure = Closure.from_fn(multiple_literal_fn)
    assert closure.code == snapshot(
        """\
def multiple_literal_fn() -> str:
    return \"\"\"Hello
            World\"\"\"
"""
    )
    assert closure.dependencies == snapshot({})


def test_raw_string_fn() -> None:
    """Test the `Closure` class with a raw string."""
    closure = Closure.from_fn(raw_string_fn)
    assert closure.code == snapshot(
        """\
def raw_string_fn() -> str:
    return r\"\"\"Hello
            World\"\"\"
"""
    )
    assert closure.dependencies == snapshot({})


@pytest.mark.skip("Skip this test for now. the pattern is broken")
def test_multi_joined_string_fn() -> None:
    """Test the `Closure` class with multiple joined strings."""
    closure = Closure.from_fn(multi_joined_string_fn)
    assert closure.code == snapshot(
        """\
def multi_joined_string_fn() -> str:
    return (
        "Hello, -----------------------------------------------------------------"
        "world!"
    )
"""
    )
    assert closure.dependencies == snapshot({})


def test_empty_body_fn() -> None:
    """Test the `Closure` class with an empty function body."""

    def empty_body_fn() -> None: ...

    closure = Closure.from_fn(empty_body_fn)
    assert closure.code == snapshot("def empty_body_fn() -> None: ...\n")
    assert closure.dependencies == snapshot({})


def test_empty_body_fn_docstrings() -> None:
    """Test the `Closure` class with an empty function body and docstrings."""
    closure = Closure.from_fn(empty_body_fn_docstrings)
    assert closure.code == snapshot("def empty_body_fn_docstrings() -> None: ...\n")
    assert closure.dependencies == snapshot({})

    os.environ["MIRASCOPE_VERSIONING_INCLUDE_DOCSTRINGS"] = "true"
    Closure.from_fn.cache_clear()
    closure = Closure.from_fn(empty_body_fn_docstrings)
    assert closure.code == snapshot('''\
def empty_body_fn_docstrings() -> None:
    """..."""  # noqa: D200
''')
    os.environ["MIRASCOPE_VERSIONING_INCLUDE_DOCSTRINGS"] = "false"


def test_nested_base_model_definitions() -> None:
    """Test the `Closure` class with nested Pydantic model definitions inside a function."""
    closure = Closure.from_fn(nested_base_model_definitions)
    assert closure.code == snapshot(
        """\
from pydantic import Field


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
"""
    )
    assert closure.dependencies == snapshot(
        {"pydantic": {"version": "2.11.5", "extras": None}}
    )


def test_nested_handle_issue_method() -> None:
    """Test the `Closure` class with nested handle issue method."""
    closure = Closure.from_fn(handle_issue)
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

from pydantic import BaseModel, Field

_F = TypeVar("_F", bound=Callable[..., Any])


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


def mock_decorator_fn(
    model: str, response_model: type[BaseModel]
) -> Callable[[_F], _F]:
    def inner(fn: _F) -> _F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return inner


@mock_decorator_fn(
    "gpt-4o-mini",
    response_model=Ticket,
)
def triage_issue(issue: str) -> str:
    return "How can I help you today?"


def customer_support_bot(issue: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    ticket = triage_issue(issue)
    return {"computed_fields": {"ticket": ticket}}


def handle_issue(issue: str) -> str:
    history = []
    response = customer_support_bot(issue, history)
    return str(response)
"""
    )
    assert closure.dependencies == snapshot(
        {"pydantic": {"version": "2.11.5", "extras": None}}
    )


def test_instance_method() -> None:
    """Test the `Closure` class with instance method."""
    closure = Closure.from_fn(Chatbot.instance_method)
    assert closure.code == snapshot(
        """\
from collections.abc import Callable
from typing import Any, TypeVar

_T = TypeVar("_T", bound=Callable[..., Any])


def test_decorator(param: str | None = None) -> Callable[[_T], _T]:
    def decorator(func: _T) -> _T:
        func._test_param = param  # type: ignore[attr-defined]
        return func

    return decorator


class Chatbot:
    def __init__(self, name: str) -> None:
        self.name = name

    @test_decorator("instance_method")
    def instance_method(self) -> str:
        return f"Hello, {self.name}!"
"""
    )
    assert closure.dependencies == snapshot({})


def test_instance_method_on_local() -> None:
    """Test the `Closure` class with instance method."""
    from collections.abc import Callable
    from typing import Any

    def test_decorator(
        param: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            func._test_param = param  # type: ignore[attr-defined]
            return func

        return decorator

    class LocalChatbot:
        """A chatbot class."""

        def __init__(self, name: str) -> None:
            self.name = name

        @test_decorator("instance_method")
        def instance_method(self) -> str:
            """class LocalChatbot:
            def __init__(self, name: str) -> None:
                self.name = name

            @test_decorator("instance_method")
            def instance_method(self) -> str:
                return f"Hello, {self.name}!"
            """  # noqa: D403
            return f"Hello, {self.name}!"

    closure = Closure.from_fn(LocalChatbot.instance_method)
    assert closure.code == snapshot(
        """\
class LocalChatbot:
    def __init__(self, name: str) -> None:
        self.name = name

    @test_decorator("instance_method")
    def instance_method(self) -> str:
        return f"Hello, {self.name}!"
"""
    )
    assert closure.dependencies == snapshot({})


def test_from_fn_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Closure.from_fn propagates exceptions from _run_ruff."""

    def fake_run_ruff(code: str) -> str:
        raise RuntimeError("Ruff failed")

    monkeypatch.setattr("mirascope.ops._internal.closure._run_ruff", fake_run_ruff)

    def dummy_func(x: int) -> int:
        return x

    with pytest.raises(RuntimeError, match="Ruff failed"):
        Closure.from_fn(dummy_func)


def test_closure_raises_when_ruff_nonzero_return() -> None:
    """Test the closure surfaces formatter failures as ClosureComputationError."""
    result = Mock()
    result.returncode = 2
    result.args = ["ruff", "check"]
    result.stdout = ""
    result.stderr = "error"

    with patch("mirascope.ops._internal.closure.subprocess.run", return_value=result):

        def transient() -> str:
            return "ok"

        Closure.from_fn.cache_clear()
        with pytest.raises(ClosureComputationError):
            Closure.from_fn(transient)


def sample_function(x: int) -> int:
    """A sample function that multiplies input by 2."""
    return x * 2


@pytest.fixture()
def fixed_uuid(monkeypatch: pytest.MonkeyPatch) -> UUID:
    """Fixture that replaces uuid.uuid4 with a fixed UUID."""
    fixed = UUID("12345678123456781234567812345678")
    monkeypatch.setattr("uuid.uuid4", lambda: fixed)
    return fixed


def test_get_qualified_name_handles_locals() -> None:
    """Test that get_qualified_name returns a simplified name for a function defined in a local scope."""

    def outer():
        def inner() -> None:
            pass

        return inner

    inner_fn = outer()
    simple_name = get_qualified_name(inner_fn)
    assert simple_name == "inner"


def test_run_ruff_exit_code_1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that _run_ruff handles exit code 1 correctly."""

    mock_run = Mock(
        side_effect=[
            subprocess.CompletedProcess(
                args=["ruff"], returncode=1, stdout="", stderr=""
            ),
            subprocess.CompletedProcess(
                args=["ruff"], returncode=0, stdout="", stderr=""
            ),
            subprocess.CompletedProcess(
                args=["ruff"], returncode=1, stdout="", stderr=""
            ),
            subprocess.CompletedProcess(
                args=["ruff"], returncode=0, stdout="", stderr=""
            ),
        ]
    )
    monkeypatch.setattr("subprocess.run", mock_run)

    def dummy() -> None: ...

    closure = Closure.from_fn(dummy)
    assert closure.code.endswith("def dummy() -> None: ...")


def test_module_without_qualname_time() -> None:
    """Test the `Closure` class with a module that doesn't have __qualname__ attribute (time)."""

    closure = Closure.from_fn(fn_using_time_module)
    assert closure.code == snapshot(
        """\
import time


def fn_using_time_module():
    return time.time()
"""
    )
    assert "time" in closure.code
    assert closure.dependencies == snapshot({})


def test_module_without_qualname_random() -> None:
    """Test the `Closure` class with a module that doesn't have __qualname__ attribute (random)."""

    closure = Closure.from_fn(fn_using_random_module)
    assert closure.code == snapshot(
        """\
import random


def fn_using_random_module():
    return random.random()
"""
    )
    assert "random" in closure.code
    assert closure.dependencies == snapshot({})


def test_signature_hash() -> None:
    """Test that signature_hash is computed correctly."""
    closure = Closure.from_fn(single_fn)
    assert closure.signature_hash == snapshot(
        "cee81f38b242e7d58dd61512d4b387197d67087aebf592403d53b9df76790db2"
    )
