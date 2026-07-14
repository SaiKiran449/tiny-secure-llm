# Phase 3 Notes

## Mental Model

BPE is frequency driven compression:

```text
common adjacent pieces get glued together
rare pieces stay small
```

The model never sees the original characters alone once merges are applied.
It sees the token inventory that BPE invented from its training text.

## Key Lessons

- Character tokenizers are easy to reason about and expensive at scale.
- BPE shortens frequent words by learning merges.
- Merge order is part of the tokenizer identity.
- Different corpora => different merges => different splits.
- Decode is only as faithful as the vocabulary allows.

## Security Lessons

Tokenization is still not a security boundary.

New failure mode in this phase:

```text
Filter uses tokenizer A
Model uses tokenizer B
Same text becomes different token sequences
```

That is filter mismatch.

Another failure mode:

```text
Policy blocks token "admin</w>"
Attacker sends administrator / ad min / homoglyph admin
```

Exact token matching is brittle.

## Deterministic vs Probabilistic

Deterministic:

- canonicalize Unicode before tokenization
- apply policy to text, then tokenize for the model
- pin tokenizer versions in production
- regression tests for known payloads across tokenizer upgrades

Probabilistic:

- hoping the model interprets a split phrase the same way the filter did
- relying on refusal after tokenization has already reshaped the input

## Bridge to Phase 4

Token IDs are still just integers. Embeddings turn those IDs into vectors with
geometry. That is where similarity attacks and RAG retrieval foundations begin.
