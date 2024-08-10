# Writing your own Custom Middleware

## How to write your own custom middleware for Mirascope

`middleware_decorator` is a helper function to assist in helping you wrap any Mirascope call.
We will be creating an example decorator `with_saving` that saves some metadata after a Mirascope call using [SQLModel](https://sqlmodel.tiangolo.com/). We will be using this table for demonstrative purposes in our example:

```python
from decimal import Decimal

from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column

class CallResponseTable(SQLModel, table=True):
    """CallResponse model"""

    __tablename__ = "call_response"
    id: int | None = Field(default=None, primary_key=True)
    function_name: str = Field(default="")
    prompt_template: str | None = Field(default=None)
    content: str | None = Field(default=None)
    response_model: dict | None = Field(sa_column=Column(JSON), default=None)
    cost: Decimal | None = Field(default=None)
```

This table should be adjusted and tailored to your needs depending on your SQL Dialect or requirements.

### Writing the decorator

```python
from mirascope.integrations import middleware_decorator

def with_saving(fn):
    """Saves some data after a Mirascope call."""

    return middleware_decorator(
        fn,
        custom_context_manager=custom_context_manager,
        custom_decorator=custom_decorator,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_response_model=handle_response_model,
        handle_response_model_async=handle_response_model_async,
        handle_structured_stream=handle_structured_stream,
        handle_structured_stream_async=handle_structured_stream_async,
    )
```

We will go over each of the different functions.

### `custom_context_manager`

We start off with the `custom_context_manager` function which will be relevant to all the handlers. You can define your own context manager where the yielded value is passed to each of the handlers.

```python
from contextlib import contextmanager
from typing import Any, Callable, Generator

from sqlmodel import Session

@contextmanager
def custom_context_manager(
    fn: Callable,
) -> Generator[Session, Any, None]:
    engine = ...
    print(f"Saving call: {fn.__name__}")
    with Session(engine) as session:
        yield session
```

All the handlers will be wrapped by this context manager. The `fn` argument will be your Mirascope call function.

### `handle_call_response` and `handle_call_response_async`

These functions must have the following signature (where async should be async) and will be called after making a standard Mirascope call. Here is a sample implementation of the sync version:

```python
from typing import Callable

from mirascope.core.base import BaseCallResponse


def handle_call_response(
    result: BaseCallResponse, fn: Callable, session: Session | None
):
    if not session:
        raise ValueError('Session is not set.')

    call_response_row = CallResponseTable(
        function_name=fn.__name__,
        content=result.content,
        prompt_template=result.prompt_template,
        cost=result.cost,
    )
    session.add(call_response_row)
    session.commit()
```

The first argument will be a Mirascope `CallResponse` of the provider you are using.

The second argument is the same `fn` argument as the one used in `custom_context_manager`.

The third argument is the yielded object of your `custom_context_manager`, in this case a SQLModel Session object. If no `custom_context_manager` is used, this value is `None`.

`handle_call_response_async` is the same as `handle_call_response` but using an `async` function.

### `handle_stream` and `handle_stream_async`

These functions must have the following signature (where async should be async) and will be called after streaming a Mirascope call. Here is a sample implementation of the sync version:

```python
from typing import Callable

from mirascope.core.base._stream import BaseStream


def handle_stream(
    stream: BaseStream, fn: Callable, session: Session | None
):
    if not session:
        raise ValueError('Session is not set.')

    result = stream.construct_call_response()
    call_response_row = CallResponseTable(
        function_name=fn.__name__,
        content=result.content,
        prompt_template=result.prompt_template,
        cost=result.cost,
    )
    session.add(call_response_row)
    session.commit()
```

The first argument will be a Mirascope `Stream` of the provider you are using.

The `Stream` object has a method `construct_call_response` which will construct a Mirascope `BaseCallResponse` object. You can also use the properties set on the Stream object.
See `handle_call_response` section for information regarding the other arguments.

One thing to note for `handle_stream` is that it will not be called until after the `Generator` has been exhausted.

### `handle_response_model` and `handle_response_model_async`

These functions must have the following signature (where async should be async) and will be called after making a Mirascope call with `response_model` set. Here is a sample implementation of the sync version:

```python
from typing import Callable
from pydantic import BaseModel

from mirascope.core.base import BaseType

def handle_response_model(
    response_model: BaseModel | BaseType, fn: Callable, session: Session | None
):
    if not session:
        raise ValueError('Session is not set.')

    if isinstance(response_model, BaseModel):
        result = response_model._response  # pyright: ignore[reportAttributeAccessIssue]
        call_response_row = CallResponseTable(
            function_name=fn.__name__,
            response_model=response_model,
            prompt_template=result.prompt_template,
            cost=result.cost,
        )
    else:
        call_response_row = CallResponseTable(
            function_name=fn.__name__,
            response_model=response_model,
            prompt_template=fn._prompt_template,  # pyright: ignore[reportFunctionMemberAccess]
        )
    session.add(call_response_row)
    session.commit()
```

The first argument will be a Pydantic `BaseModel` or Python primative depending on the type of `response_model`.

See `handle_call_response` section for information regarding the other arguments.

For `BaseModel` you can grab the `CallResponse` via `response_model._response`.
However for primatives `BaseType`, this information is not available so we use what we have access to. We recommend using a `BaseModel` for primitives when you need `CallResponse` data.

### `handle_structured_stream` and `handle_structured_stream_async`

These functions must have the following signature (where async should be async) and will be called after streaming a Mirascope call with `response_model` set. Here is a sample implementation of the sync version:

```python
from typing import Callable

from mirascope.core.base._structured_stream import BaseStructuredStream

def handle_structured_stream(
    structured_stream: BaseStructuredStream, fn: Callable, session: Session | None
):
    if not session:
        raise ValueError('Session is not set.')

    result = structured_stream.stream.construct_call_response()
    call_response_row = CallResponseTable(
        function_name=fn.__name__,
        content=result.content,
        prompt_template=result.prompt_template,
        cost=result.cost,
    )
    session.add(call_response_row)
    session.commit()
```

The first argument will be a Mirascope `StructuredStream` of the provider you are using.

Like with `handle_stream`, `handle_structured_stream` will not be called until the `Generator` has been exhausted.

### `custom_decorator`

There may be existing libraries that have a decorator implemented already. You can pass that decorator in to `custom_decorator` which will wrap the Mirascope call with your custom decorator and will be called before `middleware_decorator`.

## How to use your newly created decorator

Now that you have defined your and created your `with_saving` decorator, you can wrap any Mirascope call, like so:

```python
from your_file import with_saving

from mirascope.core import anthropic, prompt_template

@with_saving
@anthropic.call(model="claude-3-5-sonnet-20240620")
@prompt_template("What is your purpose?")
def run(): ...

print(run())
```

In this example, when `run` is finished, `handle_call_response` will be called to collect the response.

Now, any Mirascope call that uses the `with_saving` decorator will write to your database.

If there is a library that you would like for us to integrate out-of-the-box, create a [GitHub Issue](https://github.com/Mirascope/mirascope/issues) or let us know in our [Slack](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) community.
