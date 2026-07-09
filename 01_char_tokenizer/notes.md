# Phase 1 Notes

## Mental Model

A character tokenizer is a dictionary:

```text
character <-> integer ID
```

The model never receives raw text. It receives token IDs.

## Key Lessons

- Tokenization is the first lossy or lossless transformation in an LLM pipeline.
- Unknown tokens are lossy because many possible inputs collapse into `<UNK>`.
- Text that looks identical to a human may be different at the Unicode level.
- UTF-8 bytes are storage details; Unicode code points are character identities.
- Normalization is useful, but it is not authorization, validation, or policy.

## Security Lessons

Text is attacker-controlled input.

Important questions:

- What exact string did the user submit?
- What exact string did we normalize?
- What exact token IDs did the model receive?
- What exact text did our security checks inspect?
- Are logs preserving enough detail to investigate Unicode abuse?

## Trust Boundary

The tokenizer is not the security boundary.

```text
untrusted user text
   |
   v
normalization and inspection
   |
   v
tokenization
   |
   v
model
```

The real security boundary must be enforced by deterministic application logic:

- schema validation
- authorization
- tool allow-lists
- policy checks
- approval workflows
- audit logging

## Probabilistic vs Deterministic

Probabilistic:

- model refuses suspicious text
- LLM classifier flags prompt injection
- model follows system instructions

Deterministic:

- parser rejects malformed JSON
- authorization denies a tool call
- policy engine blocks an unsafe action
- audit log records raw and normalized inputs

For AI security engineering, this distinction matters more than almost anything
else.

## Things To Revisit Later

- Byte-level tokenizers can avoid `<UNK>`, but introduce other complexity.
- BPE tokenizers make filtering harder because words split differently across
  models.
- Prompt injection becomes more dangerous once the model can call tools.
- RAG introduces indirect prompt injection from retrieved documents.
