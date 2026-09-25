from typing import Any


class ValidationError(Exception):
    pass


def validate_result(result: Any) -> Any:
    if result is None:
        raise ValidationError("result is None")

    if isinstance(result, str) and not result.strip():
        raise ValidationError("result is empty")

    if isinstance(result, dict) and not result:
        raise ValidationError("result dictionary is empty")

    return result
