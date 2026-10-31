# Chapter 12. Production Harness Architecture and Observability

## Exercise questions

1. **Control and data planes.** Which component approves a policy version, and which applies it to an individual action? Why must a retrieved document change neither role?
2. **Recovery.** How does the event history distinguish a rejected candidate from an activated one? Which source records are needed to reconstruct a view?
3. **Concurrency.** Two workers read version 7 and submit valid candidates. Specify the compare-and-swap outcome and retry behaviour. Why does an idempotency key not make an external tool execute exactly once?
4. **Cost and quality.** Recalculate the worked example with only 18,000 foreground input tokens reported as cached. The revised estimate is **£0.3078**. Why can cost alone not select the safer policy?
5. **Strategy change.** A compactor repeatedly omits legally significant wording. Propose a bounded fallback and identify the checks required before Aster acts.



## Solutions and reasoning

### Answer 1

The control plane approves policy versions; the data plane enforces them for individual actions.

### Answer 2

The event log distinguishes rejected candidates from activated checkpoints, retaining immutable source references.

### Answer 3

With two CAS candidates reading version 7, only one succeeds. The loser must revalidate; idempotency alone is not exactly-once.

### Answer 4

Under stated tariff, the worked recalculation with 18,000 cached foreground tokens is £0.3078; cost alone is not a safety decision.

### Answer 5

Repeated loss of legally significant text requires protected state, independent checks and bounded fallback.

## Other chapter demonstrations

### Listing 1

```text
CONTROL PLANE
  Approved policy, configuration, versions, limits and incident controls
                                |
                                v
  User request --> Task orchestrator --> Context assembler --> Model serving
                       |      ^                |
                       |      |                +--> Compiler / compactor
                       |      |                          |
                       v      |                          v
                  Policy engine <--> Invariant validator
                       |                                  |
                       v                                  v
                  Execution gate                 Versioned context views
                       |                                  ^
                       v                                  |
                     Tools --> Source store --> Retrieval index
                                  |
                                  v
                           Events and telemetry
```

### Listing 2

```text
Tool result
    |
    v
ObservationStored --> RetrievalRequested --> ContextAssembled
    |                                           |
    +--> CompactionProposed --> CompactionValidated
                                   |
                     pass + current version + commit
                                   v
                          ContextViewActivated
                                   |
                     failure or incident --> retain or restore
                                             known-good view

Model proposes action
    |
    v
PolicyBlocked  OR  ActionAuthorised --> execution gate --> tool
```

### Listing 3

```json
{
  "tenant": "aster",
  "actor": "agent",
  "run_id": "synthetic-run-1",
  "instruction_version": "i1",
  "policy_version": "p1",
  "tool_version": "t1",
  "model_version": "offline-mock-1",
  "renderer_version": "r1",
  "index_version": "x1",
  "budget_micropounds": 10000000,
  "rates_micropounds": {
    "foreground": 2,
    "model_output": 4,
    "compaction": 3,
    "retrieval": 1,
    "tool": 10,
    "storage": 1,
    "recovery": 3
  }
}
```

### Listing 4

```sh
python3 aster.py --config config.json test

python3 aster.py --config config.json run \
  --mode deterministic --db baseline.db --out baseline.json

python3 aster.py --config config.json run \
  --mode semantic --db semantic.db --out semantic.json

python3 aster.py --config config.json evaluate \
  --dir paired-run --out paired.json
```

### Listing 5

```text
CompactionProposed    key=p10
CompactionValidated   key=p10    required_refs=true
ContextViewActivated  key=p10    new_version=1
CompactionProposed    key=p20a
CompactionValidated   key=p20a   required_refs=false
CompactionProposed    key=p20b
ContextViewActivated  key=p20b   new_version=2
CompactionProposed    key=p30
ContextViewActivated  key=p30    new_version=3
CompactionProposed    key=recovery
ContextViewActivated  key=recovery new_version=4 reason=recovery
```
