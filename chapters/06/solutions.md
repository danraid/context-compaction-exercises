# Chapter 6. Hierarchical Memory, Persistence and Retrieval

## Exercise questions

**1. Why is RAG not itself a compaction algorithm?**  
Explain the difference between retrieving evidence for a question and reducing a previous context. Give an example where retrieval uses an uncompressed original source.

**2. How do episodic and semantic memories differ?**  
Classify an approval event, its test output and the resulting current project constraint. State which provenance links should connect them.

**3. What happens when an index points to a revoked source?**  
Describe both the immediate fetch-time response and the subsequent treatment of the index and dependent facts.

**4. Resolve a conflict.**  
An informal message written yesterday contradicts a security policy approved last month. Specify what further metadata is needed before deciding whether either record governs the current task. Explain why timestamp ordering alone is insufficient.

**5. Test compaction.**  
Design a post-reset test that distinguishes a faithful summary from recoverable source-grounded storage. Include an expected result when the source has been deleted under a retention policy.



## Solutions and reasoning

### Answer 1

RAG selects external evidence for a query; compaction reduces prior-context representation.

### Answer 2

The approval event is episodic; a derived valid policy is semantic. Preserve version and approval provenance.

### Answer 3

Deny access to revoked source and invalidate stale index/dependent derived facts.

### Answer 4

Authority, scope and effective period govern precedence; a newer informal message does not automatically override policy.

### Answer 5

Compare post-reset answers against original source with version-checked retrieval; expired or deleted evidence is unavailable.

## Other chapter demonstrations

### Listing 1

```text
┌─────────────────────────────────────────────────────────┐
    │ 1. Working view: request, selected evidence, output     │
    ├── Latency boundary: external retrieval may be needed ──┤
    │ 2. Semantic facts and procedures: curated, versioned    │
    ├── Trust boundary: derived claims require provenance ───┤
    │ 3. Episodes: immutable event IDs and source links       │
    ├── Access / storage boundary: check permission on fetch ─┤
    │ 4. Source artefacts and policy records                  │
    │    Authority depends on source and approval, not tier   │
    └─────────────────────────────────────────────────────────┘
```

### Listing 2

```text
Retrieve(q, principal, t) -> {evidence where authorised(principal) ∧ valid_at(evidence,t) ∧ relevant(q,evidence)}.
```

### Listing 3

```text
query → permissions → search → rerank → evidence validation → active view
```
