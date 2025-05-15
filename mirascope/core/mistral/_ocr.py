"""""
Module for implementing the Mistral AI OCR feature.
"""""
import functools
import inspect
import os
from typing import (Any, Callable, Coroutine, Optional, ParamSpec, TypeVar, Union, cast, overload)

from mistralai.models.sdkerror import SDKError as MistralAPIException
from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.documenturlchunk import DocumentURLChunk
from mistralai.models.ocrresponse import OCRResponse as MistralOCRResponse

from .ocr_response import OCRResponse

P = ParamSpec("P")
R = TypeVar("R") # Return type of decorated func

# Define the signature of the wrapper function (sync or async)
WrapperSig = Union[Callable[P, OCRResponse], Callable[P, Coroutine[Any, Any, OCRResponse]]]

# Define the signature of the decorator factory
# Takes a function (Callable[P, R]) and returns the wrapper (WrapperSig)
DecoratorFactorySig = Callable[[Callable[P, R]], WrapperSig]

# Overloads for the decorator factory when called with arguments like @ocr(client=...)
@overload
def ocr(*, client: MistralAsyncClient) -> DecoratorFactorySig[P, R]: ...

@overload
def ocr(*, client: MistralClient) -> DecoratorFactorySig[P, R]: ...

@overload
def ocr(*, client: None = None) -> DecoratorFactorySig[P, R]: ...

# Overload for the decorator when called directly like @ocr
@overload
def ocr(fn: Callable[P, R]) -> WrapperSig: ...

def ocr(
    fn: Optional[Callable[P, R]] = None,
    *, # Force client to be keyword-only
    client: Union[MistralClient, MistralAsyncClient, None] = None,
) -> Union[DecoratorFactorySig[P, R], WrapperSig]: # Return type depends on usage
    """A decorator for calling the Mistral OCR API endpoint via URL.

    Can be used as `@ocr` or `@ocr(client=...)`.

    Note: Only supports document processing via URL in `mistralai` v1.7.0.

    Args:
        fn: The function to decorate (automatically passed when used as `@ocr`).
        client: An optional `MistralClient` or `MistralAsyncClient` instance.
            If `None`, a client is created automatically using the `MISTRAL_API_KEY`
            environment variable.

    Returns:
        If `fn` is provided (used as `@ocr`), returns the wrapped function.
        If `fn` is `None` (used as `@ocr(client=...)`), returns a decorator factory.

    Raises:
        ValueError: If the `MISTRAL_API_KEY` environment variable is not set and no
            client is provided.
        TypeError: If the provided client type does not match the decorated function's
            sync/async nature, or if the document source is not a valid URL string.
        MistralAPIException: If the Mistral API call fails.
    """

    def decorator_logic(func_to_decorate: Callable[P, R]) -> WrapperSig:
        is_async = inspect.iscoroutinefunction(func_to_decorate)

        @functools.wraps(func_to_decorate)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> OCRResponse:
            prompt_client: MistralAsyncClient
            if client is None:
                api_key = os.environ.get("MISTRAL_API_KEY")
                if api_key is None:
                    raise ValueError(
                        "MISTRAL_API_KEY environment variable must be set for Mistral OCR."
                    )
                prompt_client = MistralAsyncClient(api_key=api_key)
            elif isinstance(client, MistralAsyncClient):
                prompt_client = client
            else:
                raise TypeError(
                    "An async function must be decorated with an async client."
                )

            try:
                document_source = await func_to_decorate(*args, **kwargs)

                if not (isinstance(document_source, str) and document_source.startswith(("http://", "https://"))):
                    raise TypeError(
                        "Unsupported document source type. Must be a URL string starting " f"with http:// or https://. Got: {type(document_source)}"
                    )

                document_chunk = DocumentURLChunk(document_url=document_source)

                mistral_response = await prompt_client.ocr.process(
                    document=document_chunk
                )
            except MistralAPIException as e:
                raise e
            except TypeError as e:
                 raise e
            except Exception as e:
                # Catch-all for unexpected errors during source handling or API call
                raise RuntimeError(f"An unexpected error occurred: {e}") from e

            return OCRResponse(response=cast(MistralOCRResponse, mistral_response))

        @functools.wraps(func_to_decorate)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> OCRResponse:
            prompt_client: MistralClient
            if client is None:
                api_key = os.environ.get("MISTRAL_API_KEY")
                if api_key is None:
                    raise ValueError(
                        "MISTRAL_API_KEY environment variable must be set for Mistral OCR."
                    )
                prompt_client = MistralClient(api_key=api_key)
            elif isinstance(client, MistralClient):
                prompt_client = client
            else:
                raise TypeError(
                    "A sync function must be decorated with a sync client."
                )

            try:
                document_source = func_to_decorate(*args, **kwargs)

                if not (isinstance(document_source, str) and document_source.startswith(("http://", "https://"))):
                    raise TypeError(
                        "Unsupported document source type. Must be a URL string starting " f"with http:// or https://. Got: {type(document_source)}"
                    )

                document_chunk = DocumentURLChunk(document_url=document_source)

                mistral_response = prompt_client.ocr.process(document=document_chunk)
            except MistralAPIException as e:
                raise e
            except TypeError as e:
                 raise e
            except Exception as e:
                # Catch-all for unexpected errors during source handling or API call
                raise RuntimeError(f"An unexpected error occurred: {e}") from e

            return OCRResponse(response=cast(MistralOCRResponse, mistral_response))

        return async_wrapper if is_async else sync_wrapper

    # Check if used as @ocr or @ocr(...)
    if fn is None:
        # Called as @ocr(...), return the decorator factory
        return decorator_logic
    else:
        # Called as @ocr, apply the decorator logic directly
        return decorator_logic(fn)
