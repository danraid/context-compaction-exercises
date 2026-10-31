# Chapter 1. The Agent Harness and the Context Lifecycle: worked solutions

These solutions accompany the exercises in the first edition. They explain the underlying reasoning; design exercises admit other correct implementations when invariants and validation conditions are satisfied.

## Book exercise statements

## 1.10 Exercises

1. Why might an accurate-looking summary be unfit as the sole state representation for an agent that edits production code?
2. Where must the authority of a security condition be established, and what role does its source provenance play?
3. Design separate tests for an F1 trigger error and an F3 retrieval error.
4. In the budget example, suppose 3,000 tokens of tool output must remain verbatim. What is the smallest possible selected input if all other listed components remain unchanged?
5. What differs between model-visible context and an immutable execution log? Explain how you would test the integrity of a pointer from one to the other.
6. Why might truncating the oldest messages appear efficient in a short benchmark yet fail during a longer task?


## Answer key and engineering considerations

### Answer 1

A tool-result instruction is lower-trust content; it cannot override system/developer authority. AUTH-17 becomes operative only when retrieved from an approved policy and validated against the applicable version.

### Answer 2

The active context budget is 32,000 − 4,000 − 2,000 = 26,000 tokens. Candidate input 35,000 exceeds this by 9,000. Reducing observations by 10,500 gives 24,500. Preserving an additional 18-token mandatory constraint yields 24,518, still feasible.

### Answer 3

A valid selector must treat protected requirements as hard constraints, return source identifiers and enforce budget feasibility before an action. A content-length improvement alone does not demonstrate safety.

## Reproducibility and safety

Numerical examples are synthetic where specified in the book. Do not treat a test stub as proof that a production AI agent preserves authorisation, provenance, or operational safety.
