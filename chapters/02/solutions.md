# Chapter 2. Token Budgets, Information Theory and Acceptable Loss: worked solutions

These solutions accompany the exercises in the first edition. They explain the underlying reasoning; design exercises admit other correct implementations when invariants and validation conditions are satisfied.

## Book exercise statements

## Knowledge check and exercises

First, explain why token reduction is an incomplete objective. Your answer should distinguish a size measure from at least two measures of task performance or constraint preservation.

Secondly, compare a retained subset with a generated summary. Give one example in which generation usefully combines scattered evidence and another in which it changes the meaning of a condition.

Thirdly, explain why minimising mean error is inadequate for high-impact instructions. State how a hard constraint and a severity-weighted loss differ, and why neither alone proves safe downstream behaviour.

For a numerical exercise, suppose a 40,000-token history is reduced to 28,000 tokens. Calculate the compression ratio and reduction percentage. If seven of eight protected constraints are correctly represented, calculate constraint recall. Decide whether the result is acceptable when all eight are mandatory.

For a design exercise, extend the laboratory with a retrieval action that costs two units and restores the missing evidence, but cannot be invoked after an edit has occurred. Specify when retrieval helps and when it cannot undo a failure. Include the retrieval cost only once in your objective.


## Answer key and engineering considerations

### Answer 1

Token reduction is a size measure, not task correctness. Evaluate downstream task success, protected-invariant retention, retrieval, and recovery separately.

### Answer 2

Selection retains verbatim spans but may omit context. Generation can integrate scattered evidence but may soften prohibition into advice; test both with provenance-checked counterexamples.

### Answer 3

Hard constraints veto unsafe candidates; severity-weighted loss helps rank allowable options but cannot guarantee zero violations.

### Answer 4

40,000 → 28,000 is ratio 0.7 (retained/original), a 30% reduction, and constraint recall 7/8 = 87.5%. It fails when all eight are mandatory.

### Answer 5

A retrieval step costs two units if invoked; permit it before the irreversible action, resolve source identity/version, and reject late retrieval as incapable of undoing prior effects.

## Reproducibility and safety

Numerical examples are synthetic where specified in the book. Do not treat a test stub as proof that a production AI agent preserves authorisation, provenance, or operational safety.
