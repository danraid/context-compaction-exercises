# Other demonstrations: Chapter 2. Token Budgets, Information Theory and Acceptable Loss

### Snippet 1 (text)

```text
History H ──selection──> retained subset S ──> future query Q and policy π
     │                       Loss: omitted context or missing qualification
     │
     └────generation──> compressed message C ──> future query Q and policy π
                             Loss: omission, altered meaning or invention
```

### Snippet 2 (text)

```text
Expected task loss
  4.00 | ● A: 20,000 tokens
  1.35 |              ● B: 24,500 tokens
  1.00 |                    ● C: 26,000 tokens
       +-----------------------------------------
          20,000       24,500       26,000
                      Active input budget
```
