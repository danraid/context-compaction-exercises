# Chapter 9. Prompt Cache, KV Cache, Cost and Serving

## Exercise questions

**1. Prefix cache and KV cache.** Explain which one is associated with reuse of an input prefix and which contains model-internal attention state. Why does a durable repository not automatically become active context?

**2. Compaction and paid tokens.** Using the replay, show why Plan B can have fewer total input tokens in the measured window but a higher estimated charge than Plan A. State which assumptions would have to change for the ranking to change.

**3. Moving work off the critical path.** What can asynchronous summarisation change about user-visible latency? What costs and consistency problems remain even when the background work is hidden?

**4. Sensitivity exercise.** Change the cached-input price and the first post-compaction hit count. Recalculate all three plans. Identify the values at which B becomes cheaper than A, keeping the other assumptions fixed. Do not allow cached tokens to exceed input tokens.

**5. Design review.** Aster folds away an old discussion containing an authorisation requirement. Propose a retrieval trigger, a validation check and a safe fallback. Classify the risks under F1, F2 and F3, and explain what evidence you would collect before deployment.



## Solutions and reasoning

### Answer 1

Prefix cache depends on a stable prompt prefix; KV cache contains attention state during serving; source storage does not create context automatically.

### Answer 2

Include cache misses, compaction calls, outputs, retries and retrieval when comparing costs.

### Answer 3

Async summarisation can reduce critical-path latency but has consistency and storage trade-offs.

### Answer 4

Recalculate each plan when cache price and hit count change; enforce cached tokens ≤ total input tokens.

### Answer 5

Retrieve protected authorisation, verify effective version and deny actions when evidence is unavailable.

## Other chapter demonstrations

### Listing 1

```text
Durable memory                 Prompt presented on this call
(repository, event log)  --->  instructions | history | retrieved items
                                      |
                                      +--> possible prefix-cache reuse
                                      |
                                      +--> prefill --> active KV state
                                                       |
                                                       +--> decode
```

### Listing 2

```text
Time 1: [stable instructions + tools + old history] [new request]
         <------------- cached candidate ---------->

Time 2, append:
        [same instructions + tools + old history] [request] [tool result]
         <------------- reusable prefix ---------->

Time 2, rewrite:
        [new summary + altered instructions] [request] [tool result]
         ^
         early mismatch: old prefix may no longer be reusable
```

### Listing 3

```text
Estimated cost ($)                 Estimated elapsed time (seconds)
A  0.528  #####################    A  11.4  #######################
B  0.688  ########################### B  14.9  ##############################
C  0.438  ##################       C  10.3  #####################
```
