from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class ConversationFacts(BaseModel):
    decisions: list[str] = Field(default_factory=list, max_length=12)
    constraints: list[str] = Field(default_factory=list, max_length=12)
    entities: list[str] = Field(default_factory=list, max_length=20)
    open_questions: list[str] = Field(default_factory=list, max_length=8)

    def render(self) -> str:
        sections = []
        labels = (
            ("CONSTRAINTS", self.constraints),
            ("DECISIONS", self.decisions),
            ("ENTITIES", self.entities),
            ("OPEN", self.open_questions),
        )
        for name, values in labels:
            if values:
                sections.append(
                    name + ":\n" + "\n".join(f"- {value}" for value in values)
                )
        return "\n\n".join(sections)


@dataclass(frozen=True, slots=True)
class Turn:
    role: str
    content: str


@dataclass(slots=True)
class RollingSummary:
    keep_verbatim: int = 4
    facts: ConversationFacts = field(default_factory=ConversationFacts)

    def build(self, history: list[Turn]) -> tuple[ConversationFacts, list[Turn]]:
        if len(history) <= self.keep_verbatim:
            return self.facts, history
        older = history[:-self.keep_verbatim]
        tail = history[-self.keep_verbatim:]
        self.facts = self._merge(older)
        return self.facts, tail

    def _merge(self, turns: list[Turn]) -> ConversationFacts:
        constraints = list(self.facts.constraints)
        decisions = list(self.facts.decisions)
        entities = list(self.facts.entities)
        open_questions = list(self.facts.open_questions)
        for turn in turns:
            text = turn.content.strip()
            if text.lower().startswith("constraint:"):
                constraints.append(text.split(":", 1)[1].strip())
            elif text.lower().startswith("decision:"):
                decisions.append(text.split(":", 1)[1].strip())
            elif text.lower().startswith("question:"):
                open_questions.append(text.split(":", 1)[1].strip())
        return ConversationFacts(
            constraints=list(dict.fromkeys(constraints))[-12:],
            decisions=list(dict.fromkeys(decisions))[-12:],
            entities=list(dict.fromkeys(entities))[-20:],
            open_questions=list(dict.fromkeys(open_questions))[-8:],
        )
