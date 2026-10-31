# Chapter 8. Adaptive Compressors and Reinforcement Learning

## Exercise questions

1. **Objective and success.** Explain why maximising the proposed \(J(\pi)\) is not equivalent to completing Aster’s task correctly. Identify two measurements that the numerical example does not fully capture.

2. **Rare failure.** Construct a set of cases in which a compressor has a higher average reward than a baseline but fails one protected security requirement. Explain why changing the penalty alone may not provide the same decision rule as a hard gate.

3. **Distillation.** When does training a smaller compressor change the benchmark question? Describe what must remain fixed to compare compressor quality, and what additional question arises when the downstream agent is trained end to end.

4. **Leakage and replay.** Design repository, task-family and temporal partitions for a coding-agent evaluation. Identify a future event that could leak into a training summary and explain how paired replay would detect—or fail to detect—its effect.

5. **Rollback.** Specify a canary limit, an observable stop condition and the artefacts required to restore the baseline. Explain what action follows if the frozen policy fails the final held-out safety gate.



## Solutions and reasoning

### Answer 1

A reward proxy omits relevant task semantics; direct success and constraint checks remain mandatory.

### Answer 2

A mean reward advantage cannot override a hard protected-rule violation; reject at an independent gate.

### Answer 3

Distillation changes compressor architecture; hold downstream model and evaluation tasks fixed for fair comparison.

### Answer 4

Split by repository, task family and time; freeze final holdout before selection.

### Answer 5

Deploy a bounded canary with objective stop conditions, baseline checkpoint and rehearsed rollback.

## Other chapter demonstrations

### Listing 1

```text
Permitted trajectory data
        |
        +--> Training partition --> candidate instructions / model training
        |
        +--> Validation partition --> paired replay and policy selection
             held out from training             |
                                                v
                                        Freeze selected policy
                                                |
        +--> Final held-out partition -----> final offline audit
             separated by repository,           |
             task family and time               v
                                   Limited canary --> operational audit
                                                |              |
                                                +--> broader enablement
                                                     if gates pass

                        Safe baseline available for rollback
```

### Listing 2

```text
Correct continuation + reconstruction  ---> quality signal
Tokens, extra calls and latency        ---> cost deductions
Security violations                    ---> optional penalty signal
Protected-constraint checks            ---> mandatory gate
                                              |
                         pass audited cases --+--> eligible for staged rollout
                         observed violation --+--> reject and investigate
```
