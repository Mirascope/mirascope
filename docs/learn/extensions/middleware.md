# Writing your own Custom Middleware

`middleware_factory` is a helper function to assist in helping you wrap any Mirascope call.
We will be creating an example decorator `with_saving` that saves some metadata after a Mirascope call using [SQLModel](https://sqlmodel.tiangolo.com/). We will be using this table for demonstrative purposes in our example:

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:6:7"


    --8<-- "examples/learn/middleware/with_saving.py:17:29"
    ```

This table should be adjusted and tailored to your needs depending on your SQL Dialect or requirements.

## Writing the decorator

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:9:9"


    --8<-- "examples/learn/middleware/with_saving.py:174:190"
    ```

Let's go over each of the different functions used to create the custom middleware:

### `custom_context_manager`

We start off with the `custom_context_manager` function, which will be relevant to all the handlers. You can define your own context manager where the yielded value is passed to each of the handlers.

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py::3"

    --8<-- "examples/learn/middleware/with_saving.py:7:7"


    --8<-- "examples/learn/middleware/with_saving.py:36:42"
    ```

All of the following handlers are then wrapped by this context manager.

### `handle_call_response` and `handle_call_response_async`

These functions must have the following signature (where async should be async) and will be called after making a standard Mirascope call. Here is a sample implementation of the sync version:

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:1:1"

    --8<-- "examples/learn/middleware/with_saving.py:6:6"
    --8<-- "examples/learn/middleware/with_saving.py:12:12"


    --8<-- "examples/learn/middleware/with_saving.py:45:65"
    ```

The function arguments are (with no strict naming for the arguments):

- `result`: The provider-specific `BaseCallResponse` returned by your call
- `fn`: Your Mirascope call (the same one as the custom context manager)
- `session`: The yielded object from the `custom_context_manager`, which is a `Session` in this case. If no `custom_context_manager` is used, this value will be `None`.

`handle_call_response_async` is the same as `handle_call_response` but using an `async` function. This enables awaiting other async functions  in the handler when handling async calls.

### `handle_stream` and `handle_stream_async`

These functions must have the following signature (where async should be async) and will be called after streaming a Mirascope call. Here is a sample implementation of the sync version:

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:1:1"

    --8<-- "examples/learn/middleware/with_saving.py:7:7"
    --8<-- "examples/learn/middleware/with_saving.py:12:12"


    --8<-- "examples/learn/middleware/with_saving.py:68:87"
    ```

The first argument will be a provider-specific `BaseStream` instance. All other arguments will be the same as `handle_call_response`.

!!! note "Only run on exhaustion"

    The `handle_stream` and `handle_stream_async` handlers will run only after the `Generator` or `AsyncGenerator`, respectively, have been exhausted.

### `handle_response_model` and `handle_response_model_async`

These functions must have the following signature (where async should be async) and will be called after making a Mirascope call with `response_model` set. Here is a sample implementation of the sync version:

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:1:1"

    --8<-- "examples/learn/middleware/with_saving.py:6:6"
    --8<-- "examples/learn/middleware/with_saving.py:10:10"
    --8<-- "examples/learn/middleware/with_saving.py:12:12"


    --8<-- "examples/learn/middleware/with_saving.py:90:118"
    ```

The first argument will be a Pydantic `BaseModel` or Python primitive depending on the type of `response_model`. All other arguments will be the same as `handle_call_response`.

For `BaseModel` you can grab the provider-specific `BaseCallResponse` via `response_model._response`.
However, this information is not available for primitives `BaseType`, so we use what we have access to. We recommend using a `BaseModel` for primitives when you need `BaseCallResponse` data.

### `handle_structured_stream` and `handle_structured_stream_async`

These functions must have the following signature (where async should be async) and will be called after streaming a Mirascope call with `response_model` set. Here is a sample implementation of the sync version:

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:1:1"

    --8<-- "examples/learn/middleware/with_saving.py:8:8"
    --8<-- "examples/learn/middleware/with_saving.py:12:12"


    --8<-- "examples/learn/middleware/with_saving.py:121:142"
    ```

The first argument will be a Mirascope `StructuredStream` of the provider you are using.  All other arguments will be the same as `handle_call_response`.

!!! note "Only run on exhaustion"

    The `handle_structured_stream` and `handle_structured_stream_async` handlers will run only after the `Generator` or `AsyncGenerator`, respectively, have been exhausted.

### `handle_error` and `handle_error_async`

`handle_error` and `handle_error_async` are called when an error occurs during the Mirascope call. This is useful for handling and recording common errors like validation errors or API failures:

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:145:171"
    ```

### `custom_decorator`

There may be existing libraries that already have a decorator implemented. You can pass that decorator in to `custom_decorator`, which will wrap the Mirascope call with your custom decorator. This decorator will be called before your custom middleware decorator (in our case, before `with_saving` is called).

## How to use your newly created decorator

Now that you have defined your and created your `with_saving` decorator, you can wrap any Mirascope call, like so:

!!! mira ""

    ```python
    --8<-- "examples/learn/middleware/with_saving.py:5:5"


    --8<-- "examples/learn/middleware/with_saving.py:193:199"
    ```

In this example, when `run` is finished, `handle_call_response` will be called to collect the response. Now, any Mirascope call that uses the `with_saving` decorator will write to your database.

If there is a library that you would like for us to integrate out-of-the-box, create a [GitHub Issue](https://github.com/Mirascope/mirascope/issues) or let us know in our [Slack community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).
