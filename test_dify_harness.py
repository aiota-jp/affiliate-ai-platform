from dify_client import run_workflow
from harness.runner import AgentHarnessRunner


def main() -> None:
    runner = AgentHarnessRunner()

    def task() -> dict:
        return run_workflow(
            keyword="ノートパソコン",
            provider="all",
        )

    state = runner.run(
        task=task,
        run_key="article-notebook-001",
    )

    print("status:", state.status)
    print("attempts:", state.attempts)

    if state.error:
        print("error:", state.error)

    if isinstance(state.result, dict):
        data = state.result.get("data", {})
        print("workflow_run_id:", state.result.get("workflow_run_id"))
        print("task_id:", state.result.get("task_id"))
        print("workflow_status:", data.get("status"))
        print("outputs:", data.get("outputs"))
    elif state.result is not None:
        print("result:", state.result)


if __name__ == "__main__":
    main()
