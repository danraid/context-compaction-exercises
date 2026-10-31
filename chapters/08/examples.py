# Listing 1
import math

# Rows: successes, protected passes, cases, mean tokens (thousands),
#       mean extra calls, mean latency (seconds).
training = {
    "heuristic": (18, 20, 20, 4.0, 1.0, 2.0),
    "guideline": (19, 20, 20, 2.5, 0.5, 1.5),
    "distilled": (19, 19, 20, 1.0, 0.4, 1.0),
}

# Synthetic replay held out from training, but used for selection.
validation = {
    "heuristic": (18, 20, 20, 4.0, 1.0, 2.0),
    "guideline": (19, 20, 20, 2.5, 0.5, 1.5),
    "distilled": (19, 19, 20, 1.0, 0.4, 1.0),
}

# Final audit data: kept separate until after selection.
held_out = {
    "heuristic": (90, 100, 100, 4.0, 1.0, 2.0),
    "guideline": (96, 100, 100, 2.5, 0.5, 1.5),
    "distilled": (94, 99, 100, 1.0, 0.4, 1.0),
}

def passes_gate(row):
    _, protected, cases, _, _, _ = row
    return cases > 0 and protected == cases

def score(row):
    successes, _, cases, tokens, calls, latency = row
    return (successes / cases
            - 0.02 * tokens
            - 0.10 * calls
            - 0.05 * latency)

# Counterexample: this intentionally ignores task quality and safety.
token_only = min(validation, key=lambda name: validation[name][3])
print("Token-only choice:", token_only)
print("Token-only passes validation gate:",
      passes_gate(validation[token_only]))

eligible = {
    name: score(row)
    for name, row in validation.items()
    if passes_gate(row)
}
if not eligible:
    raise SystemExit("No eligible policy: retain the safe baseline.")

# Stable softmax; temperature 0.1 is an illustrative tuning choice.
temperature = 0.1
maximum = max(eligible.values())
raw = {
    name: math.exp((value - maximum) / temperature)
    for name, value in eligible.items()
}
total = sum(raw.values())
weights = {name: value / total for name, value in raw.items()}

# Deterministic selection; ties broken by name.
chosen = sorted(weights, key=lambda name: (-weights[name], name))[0]
print("Eligible validation scores:",
      {k: round(v, 3) for k, v in eligible.items()})
print("Relative weights:", {k: round(v, 3) for k, v in weights.items()})
print("Frozen choice:", chosen)

audit = held_out[chosen]
if not passes_gate(audit):
    print("Held-out gate FAILED: reject; return to development.")
else:
    print("Held-out gate passed on", audit[2], "audited cases.")
    print("Held-out score:", round(score(audit), 3))
    print("Next step: limited canary, not unrestricted deployment.")