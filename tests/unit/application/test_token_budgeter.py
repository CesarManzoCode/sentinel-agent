from sentinel.application.llm.token_budgeter import TokenBudgeter


def test_token_budgeter_allocates_all_sections() -> None:
    budgeter = TokenBudgeter(max_context_tokens=1000)
    allocation = budgeter.allocate()

    assert set(allocation) == {"system", "history", "memory", "tools", "observations"}
    assert sum(allocation.values()) <= 1000


def test_token_budgeter_trims_predictably() -> None:
    budgeter = TokenBudgeter(max_context_tokens=1000)
    text = "x" * 5000
    trimmed = budgeter.trim(text, 100)
    assert len(trimmed) <= 400
    assert trimmed.endswith("…")
