from collections.abc import Callable

from tenacity import AsyncRetrying, Retrying, retry, stop_after_attempt


def retry_decorator(retries: int | Retrying | AsyncRetrying) -> Callable:
    if isinstance(retries, int):
        if retries == 0:
            return lambda x: x
        return retry(stop=stop_after_attempt(retries))
    return retry(
        sleep=retries.sleep,
        stop=retries.stop,
        wait=retries.wait,
        before=retries.before,
        after=retries.after,
        before_sleep=retries.before_sleep,
        reraise=retries.reraise,
        retry_error_cls=retries.retry_error_cls,
        retry_error_callback=retries.retry_error_callback,
    )
