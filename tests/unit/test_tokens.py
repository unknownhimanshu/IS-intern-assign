from agentctl.tokens.budget import BudgetPolicy
from agentctl.tokens.counter import TokenCounter, TokenLedger


def test_counter_counts_text():
    assert TokenCounter().count("hello world") > 0


def test_ledger_breakdown():
    ledger = TokenLedger(TokenCounter())
    ledger.add("system", "stable instructions")
    ledger.add("evidence", "important evidence")
    assert ledger.total == sum(ledger.breakdown().values())


def test_budget_reserves_evidence():
    allocation = BudgetPolicy().allocate()
    assert allocation.evidence > allocation.recent_turns
