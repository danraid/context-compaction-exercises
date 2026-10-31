# Listing 1
import hashlib
import json
from datetime import date

def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()

def digest_record(record):
    encoded = json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return digest_bytes(encoded)

# Synthetic approved evidence, obtained through a trusted resolver.
policy_text = b"POL-17 v1: Do not log access tokens."
evidence = {
    "id": "POL-17",
    "version": "1",
    "content": policy_text,
}

sidecar = {
    "rule": "NO_ACCESS_TOKEN_LOGGING",
    "source_id": "POL-17",
    "source_version": "1",
    "source_sha256": digest_bytes(policy_text),
    "valid_until": "2030-12-31",
    "permissions": ["write_safe_event_log"],
}

# In a real system these baselines must be protected independently
# from the summary and from any mutable copy of the sidecar.
approved_sidecar_digest = digest_record(sidecar)
approved_permissions = frozenset({"write_safe_event_log"})

def safety_gate(candidate, evidence, action, today):
    if candidate is None:
        return False, "missing protected state"

    if digest_record(candidate) != approved_sidecar_digest:
        return False, "unapproved or altered sidecar"

    if candidate.get("rule") != "NO_ACCESS_TOKEN_LOGGING":
        return False, "required constraint absent"

    if today > date.fromisoformat(candidate["valid_until"]):
        return False, "policy expired"

    if (
        evidence.get("id") != candidate["source_id"]
        or evidence.get("version") != candidate["source_version"]
        or digest_bytes(evidence["content"]) != candidate["source_sha256"]
    ):
        return False, "evidence cannot be verified"

    if frozenset(candidate["permissions"]) != approved_permissions:
        return False, "permissions changed"

    # This example accepts exactly one action shape and one safe value.
    # Summary or tool text cannot add a new action type or permission.
    if action != {
        "type": "write_log",
        "fields": {"event": "feature_ready"},
    }:
        return False, "action outside approved logging schema"

    return True, "allowed"

today = date(2026, 10, 31)
safe = {"type": "write_log", "fields": {"event": "feature_ready"}}
unsafe = {"type": "write_log", "fields": {"access_token": "SYNTHETIC"}}

for state, action in [(None, safe), (sidecar, unsafe), (sidecar, safe)]:
    print(safety_gate(state, evidence, action, today))