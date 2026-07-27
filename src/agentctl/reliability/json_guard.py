from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

M = TypeVar("M", bound=BaseModel)
FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.MULTILINE)


class SchemaRepairFailed(RuntimeError):
    pass


def strip_wrapping(raw: str) -> str:
    text = FENCE.sub("", raw).strip()
    starts = [index for index in (text.find("{"), text.find("[")) if index >= 0]
    return text[min(starts):] if starts else text


def balance_brackets(raw: str) -> str:
    text, stack, quoted, escaped = strip_wrapping(raw), [], False, False
    for char in text:
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and char in "{[":
            stack.append(char)
        elif not quoted and char in "}]" and stack:
            stack.pop()
    if quoted:
        text += '"'
    return text + "".join("}" if char == "{" else "]" for char in reversed(stack))


def parse_or_repair(raw: str, schema: type[M]) -> M:
    for candidate in (strip_wrapping(raw), balance_brackets(raw)):
        try:
            return schema.model_validate(json.loads(candidate))
        except (json.JSONDecodeError, ValidationError):
            pass
    raise SchemaRepairFailed("response failed JSON parsing and schema validation")
