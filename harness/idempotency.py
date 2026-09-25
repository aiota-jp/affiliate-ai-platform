import hashlib


def create_run_key(*values: str) -> str:
    if not values:
        raise ValueError("at least one value is required")

    normalized = [str(value).strip() for value in values]

    if any(not value for value in normalized):
        raise ValueError("run key values must not be empty")

    raw = ":".join(normalized)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class DuplicateRunError(Exception):
    pass


class InMemoryRunStore:
    def __init__(self) -> None:
        self._keys: set[str] = set()

    def exists(self, run_key: str) -> bool:
        return run_key in self._keys

    def add(self, run_key: str) -> None:
        self._keys.add(run_key)
