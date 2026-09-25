from harness.runner import AgentHarnessRunner


def test_normal() -> None:
    runner = AgentHarnessRunner()
    state = runner.run(
        task=lambda: {"message": "article generated"},
        run_key="normal-001",
        base_delay=0,
    )
    assert state.status == "completed"
    assert state.attempts == 1


def test_validation_error() -> None:
    runner = AgentHarnessRunner()
    state = runner.run(
        task=lambda: "",
        run_key="validation-001",
        base_delay=0,
    )
    assert state.status == "failed"
    assert state.current_step == "validate"
    assert state.error == "result is empty"


def test_retry() -> None:
    runner = AgentHarnessRunner()
    counter = {"value": 0}

    def unstable_task():
        counter["value"] += 1
        if counter["value"] < 3:
            raise TimeoutError("temporary timeout")
        return {"message": "success"}

    state = runner.run(
        task=unstable_task,
        run_key="retry-001",
        retryable=(TimeoutError,),
        base_delay=0,
    )
    assert state.status == "completed"
    assert state.attempts == 3


def test_idempotency() -> None:
    runner = AgentHarnessRunner()

    first = runner.run(
        task=lambda: {"message": "success"},
        run_key="duplicate-001",
        base_delay=0,
    )
    second = runner.run(
        task=lambda: {"message": "success"},
        run_key="duplicate-001",
        base_delay=0,
    )

    assert first.status == "completed"
    assert second.status == "failed"
    assert second.error == "duplicate run: duplicate-001"


if __name__ == "__main__":
    test_normal()
    test_validation_error()
    test_retry()
    test_idempotency()
    print("All Agent Harness tests passed.")
