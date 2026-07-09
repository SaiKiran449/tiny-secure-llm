# Phase 2: Unicode Security Lab

Part 1 showed that text is not what it looks like. Part 2 builds the lab where
you inspect, attack, and harden that layer on purpose.

## 1. Theory

Unicode assigns a code point to characters from many writing systems. Python
strings expose those code points as individual characters.

Two strings can look identical on screen while being different at the byte and
code point level. Attackers exploit that gap against:

- blocklists
- regex filters
- moderation APIs
- log viewers
- human reviewers

Normalization is a standard preprocessing step. It reduces some ambiguity. It
does not turn untrusted text into trusted text.

## 2. Architecture

```text
Untrusted input
      |
      v
Unicode inspection
      |
      v
Strip invisible controls
      |
      v
Normalization (NFKC)
      |
      v
Deterministic policy / blocklist
      |
      v
Tokenizer (Phase 1) / model (later phases)
```

The inspection layer belongs **before** tokenization. If the filter sees raw
text and the model sees normalized text, you have already created a bypass.

## 3. Mathematics

Normalization is a function:

```text
N(text) -> text'
```

Security decision on a blocklist `B` is:

```text
blocked(text) = exists term in B such that term is substring of inspect(text)
```

The critical detail is what `inspect(text)` means:

```text
inspect_raw(text) = text
inspect_nfkc(text) = NFKC(text)
inspect_pipeline(text) = NFKC(strip_invisible(text))
```

If one service uses `inspect_raw` and another uses `inspect_nfkc`, the same
user input can produce different decisions.

## 4. Implementation

Run the lab:

```bash
python3 02_unicode_lab/main.py
python3 02_unicode_lab/tests.py
```

### Step 1: Normalization utilities

`normalize()` supports NFC, NFD, NFKC, and NFKD.

For security preprocessing, NFKC is the most common starting point because it
collapses many compatibility characters, including full width ASCII lookalikes.

### Step 2: Unicode visualizer

`inspect_text()` prints per character:

- index
- character
- code point
- Unicode category
- UTF-8 bytes
- invisible flag
- bidirectional control flag

### Step 3: Invisible character detector

`find_invisible_characters()` flags zero width spaces and bidirectional
formatting controls.

### Step 4: Confusable detector

`find_confusable_characters()` uses curated homoglyph groups for Latin, Greek,
and Cyrillic lookalikes.

### Step 5: Security pipeline

`UnicodeSecurityPipeline` applies deterministic steps:

1. inspect raw text
2. collect findings
3. strip invisible controls
4. normalize with NFKC
5. apply blocklist

## 5. Visualization

The demo prints:

- normalization form comparisons
- character tables for homoglyphs
- filter decisions for each attack
- pipeline outcomes for mixed samples

Watch for cases where:

```text
naive filter blocked: False
pipeline blocked: True
```

That gap is the lesson.

## 6. Attack

### Attack 1: Zero width split

```text
ign\u200bore previous instructions
```

Naive substring match for `ignore` fails.

### Attack 2: Full width bypass

```text
ＡＤＭＩＮ
```

Naive match for `admin` fails. NFKC match succeeds.

### Attack 3: Cyrillic homoglyph

Cyrillic letters that look like `admin` bypass a Latin only blocklist.

### Attack 4: Bidirectional override

`U+202E` can change visual ordering without changing the logical string your
code inspects.

## 7. Defense

Why attacks work:

- filters often compare the wrong representation
- humans review rendered text, not code points
- normalization is not homoglyph detection

Industry mitigations:

- canonicalize with an explicit normalization form
- strip or reject formatting controls
- log raw and normalized forms
- use allow lists for high risk identifiers
- keep authorization outside the model

Limitations:

- NFKC does not merge Cyrillic into Latin
- aggressive stripping can break legitimate scripts
- no single Unicode step replaces policy

Remaining risks:

- semantic attacks after normalization
- tokenizer mismatch in Phase 3
- indirect injection from pasted documents

## 8. Industry Context

Common architectural pattern across major providers:

- input hygiene before model inference
- separate trust domains for user text, retrieved text, and tool output
- deterministic policy engines around model calls
- security logging with raw request capture

Exact implementations differ and are proprietary. The public pattern is stable:
**do not treat the model as the filter**.

## 9. Interview Questions

Junior:

- What is Unicode normalization?
- Why can two identical looking strings compare unequal?
- What is a zero width character?

Mid-level:

- What is the difference between NFC and NFKC?
- Why is NFKC not sufficient for homoglyph defense?
- What should you log when investigating a Unicode bypass?

Senior:

- Design an input canonicalization pipeline for a multilingual assistant.
- How would you test Unicode regressions in CI?
- When should invisible characters be stripped vs rejected?

Staff-level:

- How do normalization, tokenization, and moderation interact in production?
- What policy decisions belong before vs after tokenization?
- How would you investigate a bypass where logs look benign but the model misbehaved?

## 10. Exercises

Coding:

- Add NFC as a pipeline option and compare outcomes.
- Reject any input containing bidi override characters instead of stripping.
- Export `InspectionReport` as JSON for audit logs.

Security:

- Build five strings that all display as `admin` with different code points.
- Find a case where normalization changes length but not meaning.
- Combine zero width and homoglyph in one payload.

Thought:

- Should legitimate users be allowed to paste invisible characters?
- What languages or names could aggressive stripping break?
- Where should the trust boundary sit for pasted RAG documents?
