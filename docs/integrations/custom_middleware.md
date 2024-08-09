# Writing your own Custom Middleware

## How to write your own custom middleware for Mirascope

`middleware_decorator` is a helper function to assist in helping you wrap any Mirascope call.
We will be creating an example decorator `with_saving` that saves some metadata after a Mirascope call:

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

### `handle_call_response` and `handle_call_response_async`

These functions will be called after making a mirascope call with the following signature:

```python
from typing import Callable

from mirascope.core.base import BaseCallResponse


def handle_call_response(
    result: BaseCallResponse, fn: Callable, context_manager: ContextManagerType | None
):
    # handle after call here
```

The first argument will be a Mirascope `CallResponse` of the provider you are using.
The second argument will be your Mirascope call function.
The third argument is the yielded object of your `custom_context_manager`

`handle_call_response_async` is the same as `handle_call_response` but using an `async` function.

### `handle_stream` and `handle_stream_async`

These functions will be called after streaming a Mirascope call with the following signature:

```python
from typing import Callable

from mirascope.core.base._stream import BaseStream


def handle_stream(
    stream: BaseStream, fn: Callable, context_manager: ContextManagerType | None
):
    # handle after stream here
```

The first argument will be a Mirascope `Stream` of the provider you are using.
See `handle_call_response` section for information regarding the other arguments.

One thing to note for `handle_stream` is that it will not be called until after the `Generator` has been exhausted.

### `handle_response_model` and `handle_response_model_async`

These functions will be called after making a mirascope call with `response_model` set with the following signature:

```python
from typing import Callable
from pydantic import BaseModel

from mirascope.core.base._utils._base_type import BaseType

def handle_response_model(
    response_model: BaseModel | BaseType, fn: Callable, context_manager: ContextManagerType | None
):
    # handle after call with response_model here
```

The first argument will be a Pydantic `BaseModel` or Python primative depending on what type `response_model` is.
See `handle_call_response` section for information regarding the other arguments.

For `BaseModel` you can grab the `CallResponse` via `response_model._response`.
However for primatives `BaseType`, this information is not available.

### `handle_structured_stream` and `handle_structured_stream_async`

These functions will be called after streaming a mirascope call with `response_model` set with the following signature:

```python
from typing import Callable

from mirascope.core.base._structured_stream import BaseStructuredStream

def handle_structured_stream(
    result: BaseStructuredStream,
    fn: Callable,
    context_manager: ContextManagerType | None,
):
```

The first argument will be a Mirascope `StructuredStream` of the provider you are using.
Like with `handle_stream`, `handle_structured_stream` will not be called until the `Generator` has been exhausted.

### `custom_context_manager`

You can define your own context manager where the yielded object is passed to each of the handlers.

Here is an example using [SQLModel](https://sqlmodel.tiangolo.com/):

```python
from contextlib import contextmanager
from typing import Any, Callable, Generator

from sqlmodel import Session

from mirascope.core.base import BaseCallResponse


@contextmanager
def custom_context_manager(
    fn: Callable,
) -> Generator[Session, Any, None]:
    engine = ...
    with Session(engine) as session:
        yield session

def handle_call_response(
    result: BaseCallResponse, fn: Callable, session: Session | None
):
    # write to db 
```

In this example, the 3rd argument of your handler will be typed with the yielded `Session` and metadata can be written to your database of choice.

### `custom_decorator`

There may be existing libraries that have a decorator implemented already. You can pass that decorator in to `custom_decorator` which will wrap the Mirascope call with that decorator.

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

```python
from typing import Callable
from sqlmodel import Session

from mirascope.core.base import BaseCallResponse


def handle_call_response(
    result: BaseCallResponse, fn: Callable, session: Session | None
):
    # Assume you have a SQLModel CallResponseTable
    if not session:
        return

    session.add(result)
    session.commit()
```

Now, any Mirascope call that uses the `with_saving` decorator will write to your database.

If there is a library that you would like for us to integrate out-of-the-box, let us know in our [Slack](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) community.
