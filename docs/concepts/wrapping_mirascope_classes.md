# Wrapping Mirascope Classes

Often times you will want to do some action before or after a call to the LLM such as logging. Mirascope offers a utility function that you can use to build your own decorator that wraps Mirascope Classes.

## Wrapping Mirascope Class Functions

Let us start off by writing a custom decorator for your use case:

```python
from mirascope.base.ops_utils import wrap_mirascope_class_functions

def with_saving(cls):
    """Test decorator for saving."""
    def handle_before_call(
        self: BaseModel,
        fn: Callable[..., Any],
        **kwargs: dict[str, Any],
    ):
        # do some work before the call
        ...
    def handle_after_call(
        self: BaseModel,
        fn: Callable[..., Any],
        result: Any,
        before_result: Any,
        **kwargs: dict[str, Any],
    ):
        # do some work after the call

    wrap_mirascope_class_functions(
        cls,
        handle_before_call=handle_before_call,
        handle_after_call=handle_after_call,
        decorator=decorator,
        custom_kwarg="anything"
    )
    return cls

```

Now let’s look at how to implement the before and after callback functions.

### Deeper dive on callback functions

There are four optional callback functions that we provide: `handle_before_call`, `handle_before_call_async`, `handle_after_call`, and `handle_after_call_async`. One of the most important parts of a production LLM-based application is to have all your calls logged. Check out our existing [integrations](https://docs.mirascope.io/latest/integrations/logfire/) for out-of-the-box solutions.

For more specific cases, you should fill out all the handle before/after methods as you see fit.

!!! note

    The `handle_before_call_async` and `handle_after_call_async` methods should generally only be used if you are calling e.g. `call_async` or `stream_async` and need to await an async method in your handler as a result. If not, you can simply define and provide the `handle_before_call` and `handle_after_call` methods. Note that the async and sync methods are functionally equivalent and should have the same signatures beyond the async difference.

### `handle_before_call`

For manual approaches to logging, it starts at `handle_before_call` . We pass a few arguments to the user, namely the Pydantic model itself, the function that is about to be called, and the kwargs of the Mirascope class function, in addition to any custom kwargs you pass in to `wrap_mirascope_class_functions` . The below example showcases how one would use the arguments in addition to using `handle_before_call` as a `contextmanager` :

```python
from typing import Any
from mirascope.base.ops_utils import get_class_vars

@contextmanager
def handle_before_call(
    self: BaseModel,
    fn: Callable[..., Any],
    **kwargs: dict[str, Any],
) -> Any:
    """Do stuff before the LLM call
    
    Args:
	    self: The instance of the Call or Embedder, contains things such as dump, properties, call_params, etc. Check what the type is then handle appropriately
	    fn: The function that was called. Typically used to grab function name for ops logging. It is not recommended to call this function, unless you know what you are doing
	    kwargs: Any custom kwargs that was passed to `wrap_mirascope_class_functions`
    """
    
    class_vars = get_class_vars(self)
    inputs = self.model_dump()
    # In this example, tracer is an opentelemetry trace.get_tracer(...)
    tracer: Tracer = kwargs["tracer"]
    with tracer.start_as_current_span(
        f"{self.__class__.__name__}.{fn.__name__}"
    ) as span:
        for k, v in {**kwargs, **class_vars, **inputs}.items():
            span.set_attribute(k, v)
        yield span
```

### `handle_after_call`

After the call to the LLM, you have access to a Mirascope `CallResponse` Pydantic Model that you can use to log your results and any additional information you might have sent over from `handle_before_call`. This callback has the same arguments as `handle_before_call` with a few extras, such as result which is the result of the Mirascope class function and also the return of `handle_before_call` . Here’s how it looks like in action:

```python
from mirascope.base.ops_utils import get_class_vars

def handle_after_call(
    self: BaseModel,
    fn: Callable[..., Any],
    result: Any,
    before_result: Any,
    **kwargs: dict[str, Any],
) -> None:
    """Do stuff after the LLM call
    
    Args:
	    self: The instance of the Call or Embedder, contains things such as dump, properties, call_params, etc. Check what the type is then handle appropriately
	    fn: The function that was called. Typically used to grab function name for ops logging. It is not recommended to call this function, unless you know what you are doing
	    result: The result of the function, which will be an instance of BaseCallResponse
	    before_result: The return of handle_before_call
	    kwargs: Any custom kwargs that was passed to `wrap_mirascope_class_functions`
    """
    
    # In this example `handle_before_result` yields a span so we can set attributes on that span
    before_result.set_attribute("response", result)
```

and...that's it! Now you're ready to use your decorator.

### Using your decorator

Add the decorator to your Mirascope classes and make your call:

```python
from mirascope.anthropic import AnthropicCall


@with_saving  # function defined in previous block above
class BookRecommender(AnthropicCall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


response = BookRecommender(genre="fantasy").call()
print(response.content)
```

## Wrapping the LLM call

There are times where accessing just the Mirascope functions might not be sufficient. We at Mirascope value the user having full control of their application, so let’s take a look at that.

### Mirascope `llm_ops`

Mirascope `llm_ops` is a property that we use in all our calls across all our providers. What it does is wrap the LLM call directly to get the arguments that the call uses directly in addition to the raw response.

Using the same example as above, here is how you can use it (note that we have left comments for where you would write or re-use your handle before/after methods):

```python
import inspect
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    contextmanager,
)
from functools import wraps
from typing import Any, Generator, Optional

from mirascope.anthropic import AnthropicCall
from mirascope.base import BaseConfig
from mirascope.base.tools import BaseTool
from mirascope.base.types import BaseCallResponse, BaseCallResponseChunk, ChunkT

@contextmanager
def record_streaming() -> Generator:
    content: list[str] = []

    def record_chunk(
        chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
    ) -> Any:
        """Handles all provider chunk_types"""
        chunk_content = response_chunk_type(chunk=chunk).content
        if chunk_content is not None:
            content.append(chunk_content)

    try:
        yield record_chunk
    finally:
        # handle after stream/stream_async

def wrap_llm(): # add any args as necessary
    def decorator(
        fn,
        suffix, # the provider, used to handle provider to provider differences
        *,
        is_async: bool = False,
        response_type: Optional[type[BaseCallResponse]] = None,
        response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
        tool_types: Optional[list[type[BaseTool]]] = None,
        model_name: Optional[str] = None, # this is specific to Gemini
    ):
        @wraps(fn)
        def wrapper(*args, **kwargs): # for call
            # handle before call
            result = fn(*args, **kwargs)
            # handle after call
            return result

        @wraps(fn)
        def wrapper_generator(*args, **kwargs): # for stream
            # handle before stream
            with record_streaming() as record_chunk:
                generator = fn(*args, **kwargs)
                if isinstance(generator, AbstractContextManager): # this is specific to Anthropic
                    with generator as s:
                        for chunk in s:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk
                else:
                    for chunk in generator:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk

        @wraps(fn)
        async def wrapper_async(*args, **kwargs): # for call_async
            # handle before call async
            result = await fn(*args, **kwargs)
            # handle after call async
            return result

        @wraps(fn)
        async def wrapper_generator_async(*args, **kwargs): # for stream_async
            # handle before stream_async
            with record_streaming() as record_chunk:
                stream = fn(*args, **kwargs)
                if inspect.iscoroutine(stream): # this is specific to OpenAI and Groq
                    stream = await stream
                if isinstance(stream, AbstractAsyncContextManager): # this is specific to Anthropic
                    async with stream as s:
                        async for chunk in s:
                            record_chunk(chunk, response_chunk_type)
                            yield chunk
                else:
                    async for chunk in stream:
                        record_chunk(chunk, response_chunk_type)
                        yield chunk

        if response_chunk_type and is_async:
            return wrapper_generator_async
        elif response_type and is_async:
            return wrapper_async
        elif response_chunk_type:
            return wrapper_generator
        elif response_type:
            return wrapper
        else:
            raise ValueError("No response type or chunk type provided")

    return decorator


class BookRecommender(AnthropicCall):
    prompt_template = "Please recommend a {genre} book."

    genre: str

    configuration = BaseConfig(llm_ops=[wrap_llm()])


response = BookRecommender(genre="fantasy").call()
print(response.content)
```

### Combine with Wrapping Mirascope Class Functions

If you happen to be using the `@with_saving` decorator, you can combine the two like so:

```python
@with_saving
class BookRecommender(AnthropicCall):
    prompt_template = "Please recommend a {genre} book."

    genre: str

    configuration = BaseConfig(llm_ops=[wrap_llm()])


response = BookRecommender(genre="fantasy").call()
print(response.content)
```

or alternatively:

```python
def with_saving(cls):
    # same code as above
    ...

    cls.configuration = cls.configuration.model_copy(
        update={
            "llm_ops": [
                *cls.configuration.llm_ops,
                wrap_llm(),
            ]
        }
    )
    return cls


@with_saving
class BookRecommender(AnthropicCall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


response = BookRecommender(genre="fantasy").call()
print(response.content)
```

This is how our integrations are written and we'd rather implement the above ourselves so you don't have to so if there are any other tools you would like us to integrate with, create a [Feature Request](https://github.com/Mirascope/mirascope/issues).
