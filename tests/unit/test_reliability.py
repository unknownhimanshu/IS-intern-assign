from pydantic import BaseModel

from agentctl.reliability.json_guard import parse_or_repair
from agentctl.reliability.timeouts import deadline, remaining


class Payload(BaseModel):
    answer: str


def test_json_guard_strips_fences():
    result = parse_or_repair('```json\n{"answer":"ok"}\n```', Payload)
    assert result.answer == "ok"


def test_deadline_propagates():
    with deadline(1):
        assert 0 < remaining() <= 1
