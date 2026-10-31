# Listing 1
import hashlib
import json


def encode(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


class FoldManager:
    def __init__(self):
        self._events = ()       # canonical JSON bytes, append-only by API
        self._folds = {}        # keyed by (branch, source revision)

    def append(self, event):
        old = self._snapshot()
        if any(e["id"] == event["id"] for e in old):
            raise ValueError("duplicate event ID")
        self._events += (encode(event),)

    def _snapshot(self):
        return [json.loads(e) for e in self._events]

    @staticmethod
    def _validate_span(events, parent, span, child_ids):
        if set(span) != {"start_id", "end_id"}:
            raise ValueError("invalid parent span")

        positions = {e["id"]: i for i, e in enumerate(events)}
        if span["start_id"] not in positions or span["end_id"] not in positions:
            raise ValueError("parent span endpoint missing")

        start = positions[span["start_id"]]
        end = positions[span["end_id"]]
        if start >= end:
            raise ValueError("parent span is not ordered")

        first, last = events[start], events[end]
        if (first.get("kind") != "parent_start"
                or last.get("kind") != "parent_end"
                or first.get("parent") != parent
                or last.get("parent") != parent):
            raise ValueError("parent span does not match parent")

        if not child_ids or any(
            event_id not in positions
            or not start < positions[event_id] < end
            for event_id in child_ids
        ):
            raise ValueError("child lies outside parent span")

    def fold(self, branch):
        events = self._snapshot()
        revision = len(events)
        key = (branch, revision)
        if key in self._folds:
            return json.loads(self._folds[key])

        child = [e for e in events if e.get("branch") == branch]
        if not child or child[-1]["kind"] != "result":
            raise ValueError("branch has no terminal result")

        result = child[-1]
        if (result["check"] != "pass" or result["constraints"]
                or not result["approved"]):
            raise ValueError("branch is not safe to fold")

        child_ids = [e["id"] for e in child]
        self._validate_span(
            events, result["parent"], result["parent_span"], child_ids
        )

        manifest = {
            "fold_id": f"{branch}@{revision}",
            "parent": result["parent"],
            "parent_span": result["parent_span"],
            "child_ids": child_ids,
            "outcome": result["outcome"],
            "check": result["check"],
            "unresolved_risks": result["risks"],
            "source_revision": revision,
            "source_checksum": digest(events),
            "evidence_checksum": digest(child),
            "restore_action": "authorised_unfold",
        }
        self._folds[key] = encode(manifest)
        return json.loads(self._folds[key])

    def unfold(self, manifest):
        events = self._snapshot()
        if len(events) != manifest["source_revision"]:
            raise ValueError("stale revision handle")
        if digest(events) != manifest["source_checksum"]:
            raise ValueError("source checksum mismatch")

        self._validate_span(
            events, manifest["parent"], manifest["parent_span"],
            manifest["child_ids"]
        )
        ids = set(manifest["child_ids"])
        child = [e for e in events if e["id"] in ids]
        if ([e["id"] for e in child] != manifest["child_ids"]
                or digest(child) != manifest["evidence_checksum"]):
            raise ValueError("evidence mismatch")
        return child

    def render(self, manifests, byte_budget):
        events = self._snapshot()
        folded_ids = set()
        outcomes = []

        for manifest in manifests:
            # Check revision, span and evidence before using the overlay.
            self.unfold(manifest)
            if folded_ids.intersection(manifest["child_ids"]):
                raise ValueError("overlapping folds")
            folded_ids.update(manifest["child_ids"])
            outcomes.append({
                "outcome": manifest["outcome"],
                "handle": manifest["fold_id"],
                "risks": manifest["unresolved_risks"],
            })

        # Derive mandatory constraints from history, not from summaries.
        mandatory = [
            {"event_id": e["id"], "constraint": constraint}
            for e in events
            for constraint in e.get("constraints", [])
        ]
        view = {
            "folded_outcomes": outcomes,
            "unfolded_events": [
                e for e in events if e["id"] not in folded_ids
            ],
            "mandatory_constraints": mandatory,
        }
        if len(encode(view)) > byte_budget:
            raise ValueError("budget cannot hold the required active view")
        return view

# Listing 2
import gc
import tracemalloc


SPAN = {"start_id": "parent-start", "end_id": "parent-end"}


def result(event_id, branch, outcome, *, constraints=None, span=None):
    return {
        "id": event_id, "branch": branch, "kind": "result",
        "parent": "repair-1", "parent_span": span or SPAN,
        "outcome": outcome, "check": "pass", "approved": True,
        "constraints": constraints or [],
        "risks": ["Only the synthetic test environment was checked"],
    }


def build_history(observation_size=40, observations_per_branch=1):
    m = FoldManager()
    m.append({"id": "parent-start", "kind": "parent_start",
              "parent": "repair-1"})
    for branch, outcome in [
        ("B1", "select version constraint"),
        ("B2", "configuration not sole cause"),
        ("B3", "initialisation present on inspected path"),
    ]:
        for i in range(observations_per_branch):
            m.append({
                "id": f"{branch}-observation-{i}",
                "branch": branch, "kind": "observation",
                "text": branch + ":" + ("x" * observation_size),
            })
        m.append(result(branch + "-result", branch, outcome))
    m.append({"id": "parent-end", "kind": "parent_end",
              "parent": "repair-1"})
    return m


def expect_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def allocation_measurement(folded):
    """Trace one fresh manager, its history, manifests and active view."""
    gc.collect()
    tracemalloc.start()
    try:
        m = build_history(observation_size=2000, observations_per_branch=25)
        if folded:
            manifests = [m.fold(b) for b in ("B1", "B2", "B3")]
            view = m.render(manifests, byte_budget=10_000_000)
        else:
            view = m._snapshot()

        # Keep both manager and view live when measuring retained allocations.
        retained, peak = tracemalloc.get_traced_memory()
        assert m is not None and view is not None
        return retained, peak
    finally:
        tracemalloc.stop()


if __name__ == "__main__":
    m = build_history()
    before = m._events
    source = m._snapshot()
    manifests = [m.fold(b) for b in ("B1", "B2", "B3")]

    assert m.fold("B2") == manifests[1]
    assert manifests[1]["parent_span"] == SPAN

    expected = [e for e in source if e.get("branch") == "B2"]
    assert m.unfold(manifests[1]) == expected
    assert m.unfold(manifests[1]) == expected
    assert m._events == before

    bad_span = dict(manifests[1])
    bad_span["parent_span"] = {
        "start_id": "parent-end", "end_id": "parent-start"
    }
    expect_error(lambda: m.unfold(bad_span))

    bad_checksum = dict(manifests[1])
    bad_checksum["evidence_checksum"] = "0" * 64
    expect_error(lambda: m.unfold(bad_checksum))

    active = m.render(manifests, byte_budget=1_000_000)
    print("Source JSON bytes:", len(encode(source)))
    print("Active-view JSON bytes:", len(encode(active)))
    print("Manifest-store JSON bytes:", len(encode(manifests)))

    # A later append makes the old handles stale. Its constraint is blocking.
    m.append(result(
        "B4-result", "B4", "not ready",
        constraints=["approval pending"]
    ))
    expect_error(lambda: m.unfold(manifests[1]))
    expect_error(lambda: m.fold("B4"))

    current = [m.fold(b) for b in ("B1", "B2", "B3")]
    full_view = m.render(current, byte_budget=1_000_000)
    assert {
        "event_id": "B4-result", "constraint": "approval pending"
    } in full_view["mandatory_constraints"]

    # Simulate a renderer trying to fit by hiding the mandatory list.
    hidden = dict(full_view)
    hidden["mandatory_constraints"] = []
    hiding_budget = len(encode(hidden))
    assert hiding_budget < len(encode(full_view))
    expect_error(lambda: m.render(current, hiding_budget))

    # Neither folding nor unfolding changed the existing source history.
    after_append = m._events
    m.unfold(current[1])
    m.fold("B2")
    assert m._events == after_append
    assert m._events[:len(before)] == before

    for label, folded in [("unfolded", False), ("folded", True)]:
        retained, peak = allocation_measurement(folded)
        print(f"{label} traced bytes: retained={retained}, peak={peak}")

    print("All checks passed.")