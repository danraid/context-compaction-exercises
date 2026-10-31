# Chapter 4. Semantic Compaction and Structured Checkpoints: exercise solutions

## Original exercises

**1. Fact or hypothesis?** Aster writes, “The compatibility test failed because of the migration.” The retained log shows a failure, and a developer suggested the migration as a possible cause. Which part is an observation, which part is a hypothesis, and what further evidence would be needed to establish causation?

**2. Syntax or truth?** Construct a JSON document that satisfies a test-result schema but falsely reports `passed`. Explain why parsing and type checks cannot establish the result, and identify the source and claim-matching checks that would be needed.

**3. Detecting drift.** Starting with the worked checkpoint, simulate three incremental updates that progressively weaken the rollback condition. Design a comparison against the retained approval record that detects the change. Explain what happens if the approval record is unavailable.

**4. Publication under failure.** A validator passes a draft, but the source manifest changes before activation. Specify how the system detects the change and what remains active. Then consider two concurrent publishers and describe how a version-checked pointer update prevents one from silently overwriting the other.



## Worked answer guide

### Exercise 1

Treat the observed failure as fact and the suspected migration cause as an unverified hypothesis.

### Exercise 2

A syntactically valid JSON status is not evidence; cross-check claims with the immutable test result.

### Exercise 3

Detect three successive softening edits by diffing mandatory modal terms against separately retained approved policy.

### Exercise 4

If manifest changes after validation, reject publication; only one compare-and-swap for the expected version can win.

## Non-Python listings reproduced from the chapter

### Non-Python listing 1

```text
Checkpoint
 ├─ schema_version, timestamp
 ├─ goal, branch, revision ───────────────► repository/task records
 ├─ decisions[] ──────────────────────────► approval records
 ├─ constraints[] and invariants[] ───────► requirements or policies
 ├─ observations[] and outputs[] ─────────► logs, files, tool records
 ├─ hypotheses[] and review_items[] ──────► relevant source material
 └─ pending_tests[] ──────────────────────► plans or test records

Publication envelope
 ├─ checkpoint hash and source-manifest hash
 └─ validator status, validator version and validation time
```

### Non-Python listing 2

```text
active checkpoint N
       │
       ├── create draft N+1 and source manifest
       │             │
       │             └── validate against fixed source versions
       │                         │
       │                pass ────┴──── fail
       │                 │              │
       │          persist hashes      discard or retain
       │          and validation      draft for review
       │          envelope              │
       │                 │              └── N remains active
       │          atomically activate N+1
       └───────────────────────────────────────────────
```

### Non-Python listing 3

```json
{
  "schema_version": "1.0",
  "timestamp": "2026-01-15T10:00:00Z",
  "goal": {
    "text": "Repair request parsing",
    "source": "E01"
  },
  "repository": {
    "branch": "repair/parser",
    "revision": "7c2a91f",
    "source": "E02"
  },
  "decisions": [
    {
      "text": "Defer the database migration",
      "status": "approved",
      "source": "E04"
    }
  ],
  "constraints": [
    {
      "text": "Preserve the existing request format.",
      "kind": "approved_requirement",
      "source": "E03"
    }
  ],
  "invariants": [
    {
      "text": "If either pending test fails, revert revision 7c2a91f before deploying.",
      "source": "E04"
    }
  ],
  "hypotheses": [
    {
      "text": "Whitespace handling may cause the parsing defect",
      "status": "experimental",
      "source": "E05"
    }
  ],
  "pending_tests": [
    {"name": "parser_unit", "status": "pending", "source": "E06"},
    {"name": "compatibility", "status": "pending", "source": "E06"}
  ],
  "outputs": [],
  "review_items": []
}
```
