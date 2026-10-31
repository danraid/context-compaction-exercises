# Chapter 11. Benchmarks, Paired Replay and Longitudinal Evaluation

## Exercise questions

1. What does a paired experiment control, and which sources of variation can remain after the fork?
2. Construct two continuations that both pass a feature test but differ in constraint retention. Specify a later check that distinguishes them.
3. Why is a recovery not the same as summary retention? Give one trace field needed to tell them apart.
4. A dataset contains 100 compaction checkpoints from five sessions. What should be resampled for a session-level inference, and what limitation remains?
5. Extend the laboratory with an F2 case in which a constraint is present but its meaning is reversed. Ensure that the saved trace supports the classification.
6. A policy is cheaper and has the same observed success rate as its comparator, but has more F1 cases. What further evidence is needed before adoption?



## Solutions and reasoning

### Answer 1

Hold model, tools, start state and tasks fixed across full-history and compacted paired replays; independently score success.

### Answer 2

Preserve protected invariants and provenance checks as acceptance criteria, distinct from evaluator prose.

### Answer 3

Use paired or clustered uncertainty; Wilson intervals for independent proportions do not replace paired effect estimation.

### Answer 4

Compute costs across input, output, cached tokens, retries, retrieval and compaction calls.

### Answer 5

A synthetic Pareto frontier illustrates a trade-off but cannot prove production readiness.

## Other chapter demonstrations

### Listing 1

```text
immutable pre-compaction fixture
             history + repository + tools + prompt
                              |
                         shared fork
                    __________|__________
                   |                     |
             full history          compaction policy
                   |                     |
             continuation          summary + continuation
                   |                     |
                   |__________  _________|
                              \/
              independent checks + saved replay traces
```

### Listing 2

```text
Success
 100% |                   |    |
  90% | |                 A    B
  80% | A            |    |    |
  70% | |    |       |    |    |
  60% | |    |       A         |
  50% | |    B       |         |
  40% |      |       |
  30% |      |
      +------------------------------
         1    2    3    4    5
             Cost: arbitrary units

      A = stratum A; B = stratum B; | = confidence interval
```
