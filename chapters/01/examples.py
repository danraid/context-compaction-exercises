# Example 1, transcribed from Chapter 1. The Agent Harness and the Context Lifecycle
from dataclasses import dataclass

@dataclass(frozen=True)
class ContextItem:
    key: str
    kind: str
    text: str
    token_estimate: int
    source_id: str
    content_hash: str
    required: bool = False
    importance: int = 0

def select_context(items: list[ContextItem], budget: int) -> list[ContextItem]:
    if budget < 0 or any(item.token_estimate < 0 for item in items):
        raise ValueError("budgets and token estimates must be non-negative")
    if len({item.key for item in items}) != len(items):
        raise ValueError("item keys must be unique")

    required = [item for item in items if item.required]
    required_tokens = sum(item.token_estimate for item in required)

    # Fail closed: never silently remove a mandatory item.
    if required_tokens > budget:
        raise ValueError("mandatory context exceeds the budget")

    selected = list(required)
    remaining = budget - required_tokens
    optional = sorted(
        (item for item in items if not item.required),
        key=lambda x: (-x.importance, x.token_estimate, x.key),
    )
    for item in optional:
        if item.token_estimate <= remaining:
            selected.append(item)
            remaining -= item.token_estimate
    return selected

======================================================================

# Example 2, transcribed from Chapter 1. The Agent Harness and the Context Lifecycle
from hashlib import sha256

def digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()

log = (
    "Authentication test failed.\n"
    "AUTH-17: Refresh tokens must not be persisted in application logs.\n"
)
sources = {"terminal-log-1": log}

items = [
    ContextItem(
        "goal", "state", "Repair the authentication test.",
        5, "goal-1", digest("Repair the authentication test."),
        required=True,
    ),
    ContextItem(
        "auth-17", "constraint",
        "Refresh tokens must not be persisted in application logs.",
        18, "terminal-log-1", digest(log),
        required=True,
    ),
    ContextItem(
        "status", "ephemeral", "Still investigating.",
        4, "status-1", digest("Still investigating."),
        importance=1,
    ),
]

# Feasible budget: retain the compulsory condition and locate its source.
selected = select_context(items, 27)
rule = next(item for item in selected if item.key == "auth-17")
original = sources[rule.source_id]
assert digest(original) == rule.content_hash
assert "AUTH-17" in original
assert selected == select_context(items, 27)

# Infeasible budget: selection fails before any tool action can occur.
tool_calls = []
try:
    select_context(items, 22)  # Mandatory estimates total 23.
    raise AssertionError("selection should have failed")
except ValueError:
    pass
assert tool_calls == []