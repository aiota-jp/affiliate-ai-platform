import time
from collections.abc import Callable
from typing import TypeVar

import httpx


T = TypeVar("T")

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def is_retryable_http_error(exc: Exception) -> bool:
    if isinstance(exc, (TimeoutError, httpx.TimeoutException, httpx.NetworkError)):
        return True

    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES

    return False


def run_with_retry(
    func: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    retryable: tuple[type[Exception], ...] | None = None,
    on_attempt: Callable[[int], None] | None = None,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    if base_delay < 0:
        raise ValueError("base_delay must be >= 0")

    for attempt in range(1, max_attempts + 1):
        if on_attempt is not None:
            on_attempt(attempt)

        try:
            return func()

        except Exception as exc:
            should_retry = (
                isinstance(exc, retryable)
                if retryable is not None
                else is_retryable_http_error(exc)
            )

            if not should_retry or attempt >= max_attempts:
                raise

            time.sleep(base_delay * attempt)

    raise RuntimeError("unreachable")
