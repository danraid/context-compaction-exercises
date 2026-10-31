# Chapter 7. When to Compact: Trigger Policies and Retrieval Decisions

## Exercise questions

1. A checkpoint accurately summarises a completed test, but a permission response remains pending. Why can applying it still be a timing failure? Identify the protected relationship that must remain available.

2. Explain hysteresis using separate entry and exit thresholds. What should happen if the next operation cannot fit during a compaction cooldown?

3. Give an example in which blocking is preferable to pruning. Then identify one condition under which clarification or additional capacity would permit progress.

4. Recalculate precision, recall and statistical F1 for the worked example if the threshold is raised to 85%. State the new actions and distinguish reserve breaches from actual overflows.

5. Add a retrieval action to the laboratory policy. Define an oracle for “needless retrieval”, including provenance and access requirements. Test a case in which the relevant record is already present and another in which it must be fetched.

6. Design a replay experiment in which two trigger policies use the same compaction transformation. Explain which measurements concern F1 timing failures and which concern F2 representation defects. Why would final task success alone be insufficient to diagnose the difference?



## Solutions and reasoning

### Answer 1

A full token window does not grant permission to compact before pending authorisation or testing resolves.

### Answer 2

Gate unsafe states before choosing keep, compact or retrieve; verify source validity after each transition.

### Answer 3

Use revision checks and hysteresis to prevent repeated compaction of unchanged state.

### Answer 4

Classify decisions by headroom, protected boundary and next operation; record why occupancy-only baseline differs.

## Other chapter demonstrations

### Listing 1

```text
risk escalation / insufficient headroom
                              |
                              v
OBSERVE ---> ASSESS ---> CONSTRAINT GATE ----unsafe----> BLOCK
   ^              |             |                         |
   |              |             | admissible              | resolve,
   |              |             v                         | clarify or
   |              |       KEEP / PRUNE / RETRIEVE          | add capacity
   |              |             |                         |
   |              +------> CANDIDATE CHECKPOINT            |
   |                            |                         |
   |                       VERIFY CANDIDATE                |
   |                       /             \                 |
   |                   pass             fail               |
   |                    |                 |                |
   |                 COMMIT          KEEP OR BLOCK         |
   |                    |                 |                |
   +--------------------+-------- retry guard ------------+
```

### Listing 2

```text
permission request issued    test running       results checked    checkpoint validated
          |                       |                    |                    |
          v                       v                    v                    v
      UNSAFE boundary       UNSAFE boundary      candidate boundary     SAFE opportunity
      decision pending      result unlinked      verify dependencies    if constraints pass
```
