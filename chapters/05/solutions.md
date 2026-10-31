# Chapter 5. Context Folding, Reversibility and Subtasks

## Exercise questions

1. **Why is a folded subtask not the same as a deleted subtask?** Explain how the distinction depends on retention policy and access control.

2. **How do learned Context Folding and reversible rendering differ?** Describe branching and return [ref003], then identify the additional version, integrity and authorisation guarantees required by this chapter’s rendering contract.

3. **What should be recorded when results are disputed?** Construct a compact record containing both positions, evidence handles, the unresolved decision and its owner. State what must remain visible to the parent.

4. **Boundary exercise.** A branch has passed its local test but modified a file another branch is using. Decide whether to fold it now. Specify the state version, dependency and validation evidence needed before the parent can treat the outcome as stable.

5. **Evaluation exercise.** Design a comparison between an unfolded baseline and a fold manager. Specify downstream tasks, correctness criteria, input-size measures and how often restoration is needed. Include manifest and evidence-storage costs as well as active-view size.



## Solutions and reasoning

### Answer 1

A fold is reversible only if source evidence remains retrievable through authorised handles; deletion is different.

### Answer 2

Learned folding concerns branching; reliable restoration also requires hashes, source versions and access checks.

### Answer 3

Preserve conflicting accounts, each evidence handle, owner, disputed decision and unresolved flag.

### Answer 4

A local passing test does not resolve shared-file conflicts; validate dependency and version before fold activation.

### Answer 5

Evaluate against an unfolded baseline on paired tasks, correctness, constraint retention, evidence recovery and total cost.

## Other chapter demonstrations

### Listing 1

```text
Parent: repair dependency-related test failures
│
├── B1: incompatible library version
│   ├── local commands, test output and artefacts
│   └── folded outcome: choose version constraint; validation passed
│
├── B2: changed configuration default
│   ├── local commands, test output and rejected alternatives
│   └── folded outcome: not sufficient to explain failure; retain handle
│
└── B3: missing initialisation
    ├── local commands and test output
    └── folded outcome: not observed under tested conditions; retain handle
```

### Listing 2

```text
ActiveView = Render(History, FoldManifest, ContextBudget)
```

### Listing 3

```text
Unfold(fold_id) must resolve to the same canonical evidence version.
```

### Listing 4

```text
Append-only event history ────────────────┐
  parent events, branch events, outputs  │
                                         ▼
Fold manifests ───────────────────────► Renderer ──► Active view
  outcome, checks, risks, handles        ▲
                                         │
Context budget and mandatory constraints ┘

Authorised unfold: manifest → verify version and checksum → evidence
```
