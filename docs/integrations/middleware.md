# Writing your own Custom Middleware

`middleware_factory` is a helper function to assist in helping you wrap any Mirascope call.
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

## Writing the decorator

```python
from mirascope.integrations import middleware_factory

def with_saving():
    """Saves some data after a Mirascope call."""

    return middleware_factory(
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

Let's go over each of the different functions used to create the custom middleware:

### `custom_context_manager`

We start off with the `custom_context_manager` function, which will be relevant to all the handlers. You can define your own context manager where the yielded value is passed to each of the handlers.

```python
from contextlib import contextmanager
from typing import Any, Callable, Generator

from sqlmodel import Session

@contextmanager
def custom_context_manager(
    fn: Callable,  # your Mirascope call
) -> Generator[Session, Any, None]:
    engine = ...
    print(f"Saving call: {fn.__name__}")
    with Session(engine) as session:
        yield session
```

All of the following handlers are then wrapped by this context manager.

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

The function arguments are (with no strict naming for the arguments):

- `result`: The provider-specific `BaseCallResponse` returned by your call
- `fn`: Your Mirascope call (the same one as the custom context manager)
- `session`: The yielded object from the `custom_context_manager`, which is a `Session` in this case. If no `custom_context_manager` is used, this value will be `None`.

`handle_call_response_async` is the same as `handle_call_response` but using an `async` function.

### `handle_stream` and `handle_stream_async`

These functions must have the following signature (where async should be async) and will be called after streaming a Mirascope call. Here is a sample implementation of the sync version:

```python
from typing import Callable

from mirascope.core.base.stream import BaseStream


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

The first argument will be a provider-specific `BaseStream` instance. All other arguments will be the same as `handle_call_response`.

!!! note "Only Run On Exhaustion"

    The `handle_stream` and `handle_stream_async` handlers will only be run after the `Generator` or `AsyncGenerator`, respectively, have been exhausted.

### `handle_response_model` and `handle_response_model_async`

These functions must have the following signature (where async should be async) and will be called after making a Mirascope call with `response_model` set. Here is a sample implementation of the sync version:

```python
from typing import Callable, cast
from pydantic import BaseModel

from mirascope.core.base import BaseType, BaseCallResponse

def handle_response_model(
    response_model: BaseModel | BaseType, fn: Callable, session: Session | None
):
    if not session:
        raise ValueError('Session is not set.')

    if isinstance(response_model, BaseModel):
        result = cast(BaseCallResponse, response_model._response)  # pyright: ignore[reportAttributeAccessIssue]
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

The first argument will be a Pydantic `BaseModel` or Python primitive depending on the type of `response_model`. All other arguments will be the same as `handle_call_response`.

For `BaseModel` you can grab the provider-specific `BaseCallResponse` via `response_model._response`.
However, this information is not available for primitives `BaseType`, so we use what we have access to. We recommend using a `BaseModel` for primitives when you need `BaseCallResponse` data.

### `handle_structured_stream` and `handle_structured_stream_async`

These functions must have the following signature (where async should be async) and will be called after streaming a Mirascope call with `response_model` set. Here is a sample implementation of the sync version:

```python
from typing import Callable

from mirascope.core.base.structured_stream import BaseStructuredStream

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

The first argument will be a Mirascope `StructuredStream` of the provider you are using.  All other arguments will be the same as `handle_call_response`.

!!! note "Only Run On Exhaustion"

    The `handle_structured_stream` and `handle_structured_stream_async` handlers will only be run after the `Generator` or `AsyncGenerator`, respectively, have been exhausted.

### `custom_decorator`

There may be existing libraries that have a decorator implemented already. You can pass that decorator in to `custom_decorator`, which will wrap the Mirascope call with your custom decorator. This decorator will be called before your custom middleware decorator (in our case, before `with_saving` is called).

## How to use your newly created decorator

Now that you have defined your and created your `with_saving` decorator, you can wrap any Mirascope call, like so:

```python
from your_file import with_saving

from mirascope.core import anthropic, prompt_template

@with_saving()
@anthropic.call(model="claude-3-5-sonnet-20240620")
@prompt_template("What is your purpose?")
def run(): ...

print(run())
```

In this example, when `run` is finished, `handle_call_response` will be called to collect the response. Now, any Mirascope call that uses the `with_saving` decorator will write to your database.

If there is a library that you would like for us to integrate out-of-the-box, create a [GitHub Issue](https://github.com/Mirascope/mirascope/issues) or let us know in our [Slack](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) community.
