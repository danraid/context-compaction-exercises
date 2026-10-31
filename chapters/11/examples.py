# Listing 1
# Exact distribution of the ordinary paired bootstrap for the toy table.
from collections import Counter

distribution = Counter({0: 1})
for _ in range(12):
    updated = Counter()
    for total, count in distribution.items():
        for difference, multiplicity in ((1, 4), (-1, 2), (0, 6)):
            updated[total + difference] += count * multiplicity
    distribution = updated

def quantile(p):
    threshold = p * 12**12
    cumulative = 0
    for total in sorted(distribution):
        cumulative += distribution[total]
        if cumulative >= threshold:
            return total / 12

print("paired damage:", 2 / 12)
print("95% percentile interval:", quantile(0.025), quantile(0.975))

# Listing 2
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

root = Path("replay_output")
(root / "fixtures").mkdir(parents=True, exist_ok=True)
(root / "traces").mkdir(parents=True, exist_ok=True)

def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def write_json(path, obj):
    path.write_text(encode(obj) + "\n", encoding="utf-8")

def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def mean(values):
    return sum(values) / len(values)

def percentile(values, p):
    ordered = sorted(values)
    # Nearest-rank percentile.
    rank = max(1, int(p * len(ordered) + 0.999999999))
    return ordered[rank - 1]

def bootstrap_interval(differences, clusters=None, seed=11, draws=3000):
    """Percentile interval for mean paired damage."""
    rng = random.Random(seed)
    estimates = []
    if clusters is None:
        for _ in range(draws):
            sample = [rng.choice(differences) for _ in differences]
            estimates.append(mean(sample))
    else:
        names = sorted(clusters)
        for _ in range(draws):
            chosen = [rng.choice(names) for _ in names]
            sample = [d for name in chosen for d in clusters[name]]
            estimates.append(mean(sample))
    return percentile(estimates, 0.025), percentile(estimates, 0.975)

rows = []
failures = Counter()

for i in range(12):
    fixture = {
        "id": i,
        "repository": f"synthetic-repository-{i % 3}",
        "history": ["request export", f"constraint-{i}: never log tokens"],
        "prompt": "implement export and explain credential handling",
    }
    fixture_path = root / "fixtures" / f"{i}.json"
    write_json(fixture_path, fixture)

    # Read the saved fork once; all conditions below use these same bytes.
    serial = fixture_path.read_bytes()
    digest = hashlib.sha256(serial).hexdigest()
    saved_fixture = json.loads(serial)

    for policy in ("full", "keep", "lossy", "index"):
        budgets = (0,) if policy == "full" else (1, 2)
        for budget in budgets:
            if policy in ("full", "keep"):
                retained, retrieved = 1, 0
            elif policy == "lossy":
                retained, retrieved = int((i + budget) % 3 != 0), 0
            else:
                retained, retrieved = 0, int(budget == 2)

            available = bool(retained or retrieved)
            # Stub: only some missing constraints cause an action failure.
            violation = int(not available and i % 2 == 0)
            success = 1 - violation
            f1 = int(not available)
            f2 = 0  # No distortion stub in this lab.
            f3 = violation

            # Synthetic accounting units; not measured tokens or latency.
            input_units = 10 if policy == "full" else 3 + budget
            output_units = 1
            tool_calls = int(policy == "index")
            cache_hits = 0
            retries = 0
            latency_units = input_units + 2 * tool_calls
            price_units = input_units + output_units + 3 * tool_calls
            trace_name = f"{i}_{policy}_{budget}.json"

            row = {
                "fixture": i,
                "repository": saved_fixture["repository"],
                "fork_sha256": digest,
                "policy": policy,
                "budget": budget,
                "success": success,
                "constraint_retained": retained,
                "constraint_available": int(available),
                "retrieval_attempt": tool_calls,
                "retrieval_success": retrieved,
                "violation": violation,
                "F1": f1, "F2": f2, "F3": f3,
                "input_units": input_units,
                "output_units": output_units,
                "cache_hits": cache_hits,
                "tool_calls": tool_calls,
                "retries": retries,
                "latency_units": latency_units,
                "price_units": price_units,
                "trace": f"traces/{trace_name}",
            }
            rows.append(row)
            write_json(root / "traces" / trace_name, {
                "fixture_path": f"fixtures/{i}.json",
                "fixture_hash": digest,
                "measurement": row,
                "evidence": {
                    "constraint": saved_fixture["history"][1],
                    "available_to_stub": available,
                    "stub_rule": "missing constraint and even id => violation",
                },
            })
            for label in ("F1", "F2", "F3"):
                if row[label]:
                    failures[(policy, budget, label)] += 1

write_csv(root / "measurements.csv", rows)

matrix = []
for policy in ("full", "keep", "lossy", "index"):
    budgets = (0,) if policy == "full" else (1, 2)
    for budget in budgets:
        for category in ("F1", "F2", "F3"):
            matrix.append({
                "policy": policy, "budget": budget,
                "category": category,
                "count": failures[(policy, budget, category)],
            })
write_csv(root / "failure_matrix.csv", matrix)

# Join each compacted continuation to its own full-history fixture.
baseline = {r["fixture"]: r for r in rows if r["policy"] == "full"}
comparisons = []

for policy in ("keep", "lossy", "index"):
    for budget in (1, 2):
        group = [
            r for r in rows
            if r["policy"] == policy and r["budget"] == budget
        ]
        differences = []
        clusters = defaultdict(list)
        outcomes = Counter()

        for r in group:
            full = baseline[r["fixture"]]
            assert r["fork_sha256"] == full["fork_sha256"]
            difference = full["success"] - r["success"]
            differences.append(difference)
            clusters[r["repository"]].append(difference)
            outcomes[(full["success"], r["success"])] += 1

        pair_lo, pair_hi = bootstrap_interval(differences)
        cluster_lo, cluster_hi = bootstrap_interval(
            differences, clusters=clusters
        )
        attempts = sum(r["retrieval_attempt"] for r in group)
        retrieved = sum(r["retrieval_success"] for r in group)

        comparisons.append({
            "policy": policy,
            "budget": budget,
            "fixtures": len(group),
            "repository_clusters": len(clusters),
            "full_success_rate": mean([
                baseline[r["fixture"]]["success"] for r in group
            ]),
            "compacted_success_rate": mean([r["success"] for r in group]),
            "paired_damage": mean(differences),
            # Positive improvement means compacted success exceeds full.
            "paired_improvement": -mean(differences),
            "damage_ci_pair_low": pair_lo,
            "damage_ci_pair_high": pair_hi,
            "damage_ci_cluster_low": cluster_lo,
            "damage_ci_cluster_high": cluster_hi,
            "both_success": outcomes[(1, 1)],
            "damage_cases": outcomes[(1, 0)],
            "rescue_cases": outcomes[(0, 1)],
            "neither_success": outcomes[(0, 0)],
            "constraint_recall": mean([
                r["constraint_retained"] for r in group
            ]),
            "constraint_availability": mean([
                r["constraint_available"] for r in group
            ]),
            "retrieval_attempts": attempts,
            "retrieval_success_rate": retrieved / attempts if attempts else "",
            "violations": sum(r["violation"] for r in group),
            "mean_input_units": mean([r["input_units"] for r in group]),
            "mean_tool_calls": mean([r["tool_calls"] for r in group]),
            "mean_latency_units": mean([r["latency_units"] for r in group]),
            "mean_price_units": mean([r["price_units"] for r in group]),
        })

write_csv(root / "paired_results.csv", comparisons)
print("Wrote", len(rows), "measurements and",
      len(comparisons), "paired comparisons to", root)