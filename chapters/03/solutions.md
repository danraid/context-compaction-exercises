# Chapter 3. Truncation, Pruning and Observation Compression: worked solutions

These solutions accompany the exercises in the first edition. They explain the underlying reasoning; design exercises admit other correct implementations when invariants and validation conditions are satisfied.

## Book exercise statements

## Knowledge check and exercises

1. **Pruning versus generation.** A selector returns three verbatim log lines; a summariser writes one new sentence about them. Which operation can introduce a new wording, and which can still mislead by omitting surrounding evidence? Design one test for each.

2. **Tool-call integrity.** A function call contains a JSON argument with a file path and a Boolean flag. Give an example of token removal that makes the call invalid, and another that leaves valid JSON but changes its meaning. State where schema validation helps and where it does not.

3. **Source pointers.** Explain why a line number without a source version is insufficient after a log changes. Implement hash-checked retrieval for the laboratory and test an incorrect hash.

4. **Adversarial future question.** The structural selector retains the failure and rollback requirement but discards repeated warnings. Formulate a legitimate question it cannot answer from the selected view alone. Modify the representation to answer it without retaining every warning line.

5. **Fair comparison.** A colleague compares a compressed prompt on one model with an uncompressed prompt on a stronger model. Identify the confound and propose a controlled comparison. Include token counts for message wrappers and source pointers, not just the extracted prose.


## Answer key and engineering considerations

### Answer 1

A verbatim selector can mislead by excluding context, while a generated summary can introduce novel wording. Test omitted qualifiers and semantic entailment separately.

### Answer 2

Removing bytes inside JSON can break parseability. Changing a boolean value can preserve schema validity but invert meaning; schemas do not prove authorisation.

### Answer 3

A line number is not a stable identifier: persist source hash, version and offsets, reject mismatched hashes.

### Answer 4

A future question about frequency of repeated warnings requires aggregate count or pointer to archived log; do not retain every line if a validated index suffices.

### Answer 5

Compare on the same model, tasks, source snapshot, prompt wrappers, tokenizer, tools and temperatures, with paired continuation and task success checks.

## Reproducibility and safety

Numerical examples are synthetic where specified in the book. Do not treat a test stub as proof that a production AI agent preserves authorisation, provenance, or operational safety.
