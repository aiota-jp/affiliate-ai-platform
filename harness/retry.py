import time
from collections.abc import Callable
from typing import TypeVar

import httpx

T = TypeVar("T")

# 一時的なHTTPエラーだけを再試行する。
# 4xx（429を除く）、Validation Error、重複判定などは再試行しない。
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def is_retryable(exc: Exception) -> bool:
    """例外が再試行対象かを判定する。"""
    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError)):
        return True

    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES

    return False


def run_with_retry(
    func: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> T:
    """一時的な外部APIエラーだけを待機付きで再試行する。"""
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    if base_delay < 0:
        raise ValueError("base_delay must be >= 0")

    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as exc:
            if not is_retryable(exc) or attempt >= max_attempts:
                raise

            # 1秒 → 2秒 → ... の線形バックオフ。
            time.sleep(base_delay * attempt)

    raise RuntimeError("unreachable")
