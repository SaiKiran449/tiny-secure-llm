# TinySecureLM

Building a language model from scratch — and attacking every layer along the way.

This repo documents a hands-on journey from tokenization to a secure AI application:
character tokenizers, Unicode abuse, BPE, embeddings, attention, transformers,
prompt injection, RAG, tool calling, and production-style security controls.

## Phases

| Phase | Topic | Status |
|-------|-------|--------|
| 01 | Character Tokenizer | Done |
| 02 | Unicode Security Lab | Planned |
| 03 | BPE Tokenizer | Planned |
| 04 | Embeddings | Planned |
| 05 | Bigram Language Model | Planned |
| 06 | Self-Attention | Planned |
| 07 | Transformer | Planned |
| 08 | Instruction Tuning | Planned |
| 09 | Prompt Injection Lab | Planned |
| 10 | Output Validation | Planned |
| 11 | RAG | Planned |
| 12 | Tool Calling | Planned |
| 13 | Security Gateway | Planned |
| 14 | Security Evaluations | Planned |
| 15 | Capstone | Planned |

## Quick start

```bash
python3 01_char_tokenizer/main.py
python3 01_char_tokenizer/tests.py
```

## Philosophy

Every phase follows the same loop:

1. Build it
2. Understand why it exists
3. Attack it
4. Harden it
5. Test it
6. Document lessons learned
