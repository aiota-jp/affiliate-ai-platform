from collections.abc import Callable
from typing import Any

from harness.idempotency import DuplicateRunError, InMemoryRunStore
from harness.logger import create_logger
from harness.retry import run_with_retry
from harness.state import RunState
from harness.validator import validate_result


class AgentHarnessRunner:
    def __init__(
        self,
        run_store: InMemoryRunStore | None = None,
    ) -> None:
        self.logger = create_logger()
        self.run_store = run_store or InMemoryRunStore()

    def run(
        self,
        task: Callable[[], Any],
        *,
        run_key: str,
        retryable: tuple[type[Exception], ...] | None = None,
        max_attempts: int = 3,
        base_delay: float = 1.0,
    ) -> RunState:
        state = RunState(run_key=run_key)

        self.logger.info("run started run_key=%s", run_key)

        try:
            state.move_to("idempotency")

            if self.run_store.exists(run_key):
                raise DuplicateRunError(f"duplicate run: {run_key}")

            state.status = "running"
            state.move_to("execute")

            def on_attempt(attempt: int) -> None:
                state.attempts = attempt
                self.logger.info(
                    "task attempt=%s run_key=%s",
                    attempt,
                    run_key,
                )

            result = run_with_retry(
                task,
                max_attempts=max_attempts,
                base_delay=base_delay,
                retryable=retryable,
                on_attempt=on_attempt,
            )

            state.move_to("validate")
            validated = validate_result(result)

            # Only successful runs are recorded as completed idempotent runs.
            self.run_store.add(run_key)
            state.succeed(validated)

            self.logger.info("run completed run_key=%s", run_key)

        except Exception as exc:
            state.fail(exc)
            self.logger.error(
                "run failed run_key=%s step=%s error=%s",
                run_key,
                state.current_step,
                exc,
            )

        return state
