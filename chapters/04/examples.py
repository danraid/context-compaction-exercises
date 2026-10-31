# Listing 1
import copy
import hashlib
import json
import re

def encoded(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()

# Exercise fixture: treat this separately retained manifest as trusted.
sources = {
    "E04": {
        "kind": "rollback",
        "text": "If either pending test fails, revert revision 7c2a91f before deploying."
    },
    "E06": {
        "kind": "test_plan",
        "tests": {
            "parser_unit": "pending",
            "compatibility": "pending"
        }
    }
}
manifest = {key: digest(value) for key, value in sources.items()}

def resolve(pointer):
    if not isinstance(pointer, str) or not re.fullmatch(r"E[0-9]{2}", pointer):
        raise ValueError("malformed provenance")
    if pointer not in sources or pointer not in manifest:
        raise ValueError("missing source")
    if digest(sources[pointer]) != manifest[pointer]:
        raise ValueError("source hash mismatch")
    return sources[pointer]

def validate(candidate):
    try:
        if not isinstance(candidate, dict) or len(encoded(candidate)) > 4096:
            raise ValueError("invalid document or size")
        if set(candidate) != {"schema_version", "rollback", "tests"}:
            raise ValueError("invalid top-level keys")
        if candidate["schema_version"] != "lab-1":
            raise ValueError("unsupported schema")

        rollback = candidate["rollback"]
        if not isinstance(rollback, dict) or set(rollback) != {"text", "source"}:
            raise ValueError("invalid rollback")
        record = resolve(rollback["source"])
        if (rollback["source"] != "E04" or record["kind"] != "rollback"
                or rollback["text"] != record["text"]):
            raise ValueError("rollback invariant not preserved")

        tests = candidate["tests"]
        if not isinstance(tests, list) or len(tests) != 2:
            raise ValueError("two tests required")
        names = set()
        for test in tests:
            if not isinstance(test, dict) or set(test) != {"name", "status", "source"}:
                raise ValueError("invalid test record")
            if not isinstance(test["name"], str) or test["name"] in names:
                raise ValueError("invalid or duplicate test name")
            names.add(test["name"])
            evidence = resolve(test["source"])
            if (test["source"] != "E06" or evidence["kind"] != "test_plan"
                    or evidence["tests"].get(test["name"]) != test["status"]):
                raise ValueError("test claim unsupported")
        if names != {"parser_unit", "compatibility"}:
            raise ValueError("required test missing")
        return True
    except (ValueError, TypeError, KeyError):
        return False

# Deterministic extraction of the protected text and planned statuses.
good = {
    "schema_version": "lab-1",
    "rollback": {"text": sources["E04"]["text"], "source": "E04"},
    "tests": [
        {"name": name, "status": status, "source": "E06"}
        for name, status in sources["E06"]["tests"].items()
    ]
}

invented_result = copy.deepcopy(good)
invented_result["tests"][0].update(status="passed", source="E99")

lost_rollback = copy.deepcopy(good)
lost_rollback["rollback"]["text"] = "Revert if necessary."

bad_provenance = copy.deepcopy(good)
bad_provenance["rollback"]["source"] = "../E04"

unsupported_pass = copy.deepcopy(good)
unsupported_pass["tests"][0]["status"] = "passed"

assert validate(good)
for candidate in (invented_result, lost_rollback, bad_provenance, unsupported_pass):
    assert not validate(candidate)
print("Valid fixture accepted; four invalid fixtures rejected.")