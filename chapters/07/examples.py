# Listing 1
import json

WINDOW = 10_000
RESERVE = 1_000
SAVING = 1_000
VERSION = "boundary-risk-v1"

# Independent checkpoints: id, used, next cost, permission pending,
# test pending, validated boundary, expected risk-policy action.
cases = [
    ("A", 8200,  400, True,  False, False, "keep"),
    ("B", 8600,  600, True,  False, False, "block"),
    ("C", 8700,  600, False, False, True,  "compact"),
    ("D", 7600, 1600, False, False, True,  "compact"),
    ("E", 8100,  200, False, False, False, "keep"),
    ("F", 7900, 1400, False, False, False, "block"),
]

# Sequential observations. T1–T3 model delayed responses; T4 is
# validated. T5 has no new information after compaction. T6 has
# new information and permits another compaction.
trace = [
    ("T1", 8600,  600, True,  True,  False, 1, "block"),
    ("T2", 8600,  600, True,  True,  False, 1, "block"),
    ("T3", 8600,  600, False, True,  False, 2, "block"),
    ("T4", 8600,  600, False, False, True,  3, "compact"),
    ("T5", 7600, 1500, False, False, True,  3, "block"),
    ("T6", 7600, 1500, False, False, True,  4, "compact"),
]

def threshold(obs, last_compacted_revision):
    # Deliberately unsafe baseline, used only for comparison.
    return ("compact" if obs["used"] >= 8000 else "keep",
            "occupancy threshold")

def boundary_risk(obs, last_compacted_revision):
    headroom = WINDOW - obs["used"] - RESERVE
    if obs["next"] <= headroom:
        return "keep", "next operation fits within reserve"

    if obs["permission_pending"] or not obs["safe_boundary"]:
        return "block", "unsafe boundary under pressure"

    if obs["revision"] == last_compacted_revision:
        return "block", "no new information since compaction"

    return "compact", "validated boundary under pressure"

def observation(row, revision=1):
    ident, used, next_cost, permission, test, safe, *_ = row
    return {
        "id": ident,
        "used": used,
        "next": next_cost,
        "permission_pending": permission,
        "test_pending": test,
        "safe_boundary": safe,
        "revision": revision,
    }

def run_risk(obs, last_compacted_revision):
    action, reason = boundary_risk(obs, last_compacted_revision)
    post_size = obs["used"] - SAVING if action == "compact" else None

    # The fixture declares validation successful at a safe boundary.
    # A real harness must verify the candidate's content and provenance.
    verified = True if action == "compact" else None
    record = {
        "trace_id": "synthetic",
        "checkpoint_id": obs["id"],
        "policy_version": VERSION,
        "window": WINDOW,
        "used": obs["used"],
        "reserve": RESERVE,
        "projected_next_cost": obs["next"],
        "permission_pending": obs["permission_pending"],
        "test_pending": obs["test_pending"],
        "safe_boundary": obs["safe_boundary"],
        "revision": obs["revision"],
        "action": action,
        "reason": reason,
        "source_segment": obs["id"] if action == "compact" else None,
        "verification": verified,
        "post_compaction_size": post_size,
    }
    assert not (action == "compact" and obs["permission_pending"])
    assert not (action == "compact"
                and obs["revision"] == last_compacted_revision)
    return action, record

# Each worked-example checkpoint starts with a fresh policy state.
for row in cases:
    obs = observation(row)
    expected = row[-1]
    baseline, _ = threshold(obs, None)
    action, record = run_risk(obs, None)
    assert action == expected
    record["threshold_action"] = baseline
    print(json.dumps(record, sort_keys=True))

# The trace carries the last committed revision between observations.
last_compacted_revision = None
for row in trace:
    revision, expected = row[-2:]
    obs = observation(row, revision)
    action, record = run_risk(obs, last_compacted_revision)
    assert action == expected
    if action == "compact":
        last_compacted_revision = revision
        # Confirm that this fixture's compaction creates enough headroom.
        assert record["post_compaction_size"] + obs["next"] <= WINDOW - RESERVE
    print(json.dumps(record, sort_keys=True))