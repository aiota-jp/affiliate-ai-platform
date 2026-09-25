from dataclasses import dataclass
from typing import Any


@dataclass
class RunState:
    run_key: str
    status: str = "created"
    current_step: str = "created"
    attempts: int = 0
    result: Any = None
    error: str | None = None

    def move_to(self, step: str) -> None:
        self.current_step = step

    def succeed(self, result: Any) -> None:
        self.status = "completed"
        self.current_step = "completed"
        self.result = result
        self.error = None

    def fail(self, error: Exception) -> None:
        self.status = "failed"
        self.error = str(error)
