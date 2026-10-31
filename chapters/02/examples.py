# Example 1, transcribed from Chapter 2. Token Budgets, Information Theory and Acceptable Loss
from math import ceil

# Ten synthetic blocks, each costed at 100 assumed tokens.
history = [
    "intro", "old_1", "old_2", "old_3",
    "invariant",   # edit only if approval AND tests are available
    "evidence",    # diagnostic fact needed by the evidence query
    "recent_1", "recent_2", "recent_3", "tail",
]

queries = [
    # name, probability, cost of a wrong decision
    ("routine", 0.80, 10),
    ("diagnose", 0.19, 10),
    ("rare_edit", 0.01, 1000),
]

def head_tail(blocks, budget):
    left = ceil(budget / 2)
    right = budget - left
    return blocks[:left] + (blocks[-right:] if right else [])

def curated(blocks, budget):
    priority = ["invariant", "evidence"]
    remainder = [b for b in blocks if b not in priority]
    return (priority + remainder)[:budget]

def correct(query, selected):
    if query == "routine":
        return True
    if query == "diagnose":
        return "evidence" in selected
    # Synthetic replay: absent invariant produces the wrong "allow".
    return "invariant" in selected

def evaluate(selected):
    accuracy = sum(correct(q, selected) for q, _, _ in queries) / len(queries)
    loss = sum(p * cost * (not correct(q, selected))
               for q, p, cost in queries)
    return accuracy, loss

for budget in (4, 6, 8):
    for name, selector in (("head/tail", head_tail), ("curated", curated)):
        selected = selector(history, budget)
        accuracy, loss = evaluate(selected)
        print(f"{budget * 100:3} tokens  {name:9}  "
              f"accuracy={accuracy:.3f}  expected_loss={loss:.1f}  "
              f"rare_correct={correct('rare_edit', selected)}")