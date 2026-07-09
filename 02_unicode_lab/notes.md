# Phase 2 Notes

## Mental Model

Unicode security is about **agreement**.

Different components must agree on:

- which normalization form they use
- whether invisible characters are stripped or preserved
- whether matching is raw, normalized, or canonicalized
- what gets logged for forensics

When they disagree, attackers slip through the gap.

## What Normalization Buys You

NFKC helps with:

- full width ASCII lookalikes
- some compatibility characters
- certain composed vs decomposed forms when you standardize on NFC or NFKC

## What Normalization Does Not Buy You

NFKC does not reliably stop:

- homoglyphs across scripts (Latin vs Cyrillic vs Greek)
- attacks that depend on visual rendering vs logical order (bidi controls)
- every invisible character policy you might need
- semantic attacks (the text is valid but malicious)

## Deterministic vs Probabilistic

Deterministic in this phase:

- invisible character detection
- stripping formatting controls
- NFKC normalization
- blocklist on canonicalized text
- structured inspection reports

Probabilistic (not enough alone):

- asking a model to ignore malicious Unicode
- hoping users will not paste weird text
- assuming visual inspection catches attacks

## Logging Guidance

For production, log at minimum:

- raw input bytes or escaped Unicode
- normalization form used
- normalized output
- findings from inspection
- filter decision and reason code

Never rely only on decoded or normalized text for incident response.

## Bridge to Phase 3

BPE tokenizers split text differently across models and vocabularies.
That means two systems can both "normalize correctly" and still disagree after
tokenization. Phase 3 is where filter mismatch gets worse.
