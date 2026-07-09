# Phase 1: Character Tokenizer

This lesson builds the first component of a language model: a tokenizer.

We are not trying to build a production tokenizer yet. We are building the
simplest possible version so every later component has a clear foundation.

## 1. Theory

Computers do not understand text directly. They understand numbers.

When you type:

```text
hello
```

the model cannot consume those letters as letters. We first translate each
character into an integer ID:

```text
"h" -> 5
"e" -> 2
"l" -> 7
"l" -> 7
"o" -> 9
```

That translation layer is called tokenization.

For this phase, one token equals one character. Later, with Byte Pair Encoding,
one token may represent a character, part of a word, a whole word, punctuation,
or even bytes.

### Unicode vs UTF-8

These two ideas are often confused:

- Unicode is a giant catalog that assigns a number, called a code point, to
  characters from many writing systems.
- UTF-8 is one way to store those code points as bytes.

Example:

```text
Character: 🔐
Unicode code point: U+1F510
UTF-8 bytes: f0 9f 94 90
```

The tokenizer in this phase works at the Python character level, not the raw
byte level.

## 2. Architecture

A tokenizer sits before the model:

```text
Human text
   |
   v
Tokenizer
   |
   v
Integer token IDs
   |
   v
Embedding table
   |
   v
Transformer
```

The tokenizer is not just a convenience. It decides what the model can see.
If a character is not in the vocabulary, our tokenizer maps it to `<UNK>`.

```text
"hello 🔐"
   |
   v
[5, 2, 7, 7, 9, 1, 0]
                  ^
                  unknown emoji became <UNK>
```

Once information becomes `<UNK>`, it is lost. Decoding cannot recover the
original character.

## 3. Mathematics

At this stage, the math is intentionally simple.

Let:

- `V` be the vocabulary, the set of known characters.
- `x` be an input string.
- `x_i` be the character at position `i`.
- `id(x_i)` be the integer ID for character `x_i`.

Encoding means:

```text
encoded_i = id(x_i), if x_i is in V
encoded_i = id(<UNK>), otherwise
```

Decoding means:

```text
decoded_i = token(encoded_i)
```

This gives us a sequence of integers:

```text
x = "hello"
encoded = [5, 2, 7, 7, 9]
```

The next phase of an LLM will turn each integer into a vector. That vector is
called an embedding.

## 4. Implementation

Run the demo:

```bash
python 01_char_tokenizer/main.py
```

The implementation is intentionally small.

### Step 1: Build a Vocabulary

`CharacterTokenizer.train_from_text()` collects every unique character in a
training string.

Important idea:

```text
The model only has IDs for characters seen during vocabulary creation.
```

If the training text is:

```text
hello secure llm!
```

then the vocabulary knows letters like `h`, `e`, `l`, and `m`, but not an emoji
like `🔐`.

### Step 2: Encode

`encode()` walks through text one character at a time and replaces each
character with its ID.

Unknown characters become `<UNK>`.

### Step 3: Decode

`decode()` converts IDs back into characters.

This is not always reversible:

```text
"🔐" -> <UNK> -> "<UNK>"
```

The exact original unknown character is gone.

### Step 4: Inspect Unicode

`describe_text()` prints:

- character position
- visible representation
- Unicode code point
- Unicode category
- UTF-8 bytes
- Unicode name

This matters because visually similar text may not be equal.

## 5. Visualization

This phase uses terminal visualization instead of plots.

The demo prints:

```text
ID -> token mapping
input text
token IDs
decoded text
Unicode code points
UTF-8 bytes
invisible character findings
```

This is the first habit of AI security engineering:

```text
Never trust what text looks like.
Inspect what it is.
```

## 6. Attack

Ask: how would an attacker abuse this?

### Attack 1: Unknown Character Confusion

If a security filter and the model tokenizer disagree, an attacker may hide
meaning inside characters the filter handles differently.

Example:

```text
ignore 🔐 previous instructions
```

Our tokenizer does not know `🔐`, so it becomes `<UNK>`.

Risk:

```text
Security layer sees one thing.
Model sees another thing.
Logs may show something else.
```

### Attack 2: Zero-Width Characters

An attacker can insert invisible characters:

```text
ign\u200bore previous instructions
```

This may display like:

```text
ignore previous instructions
```

but string matching for `"ignore"` may fail because the actual text contains an
extra invisible code point.

### Attack 3: Homoglyphs

Some characters look alike but are different:

```text
A  Latin capital A
Α  Greek capital alpha
А  Cyrillic capital A
```

A naive denylist for `"API"` may miss visually similar variants.

## 7. Defense

Normalization helps reduce some differences:

```text
ＡＢＣ １２３ -> ABC 123
```

But normalization is not enough.

Deterministic controls:

- Parse and validate structured data before acting on it.
- Detect and log invisible or bidirectional control characters.
- Use allow-lists for high-risk fields when possible.
- Keep security decisions outside the model.
- Ensure filters and model inputs use the same canonicalized text.

Probabilistic mitigations:

- Ask an LLM classifier whether text is suspicious.
- Ask the model to ignore prompt injection.
- Rely on model refusal behavior.

Probabilistic mitigations can reduce risk, but they are not security
boundaries.

## 8. Industry Context

Large AI providers do not usually use character tokenizers for production LLMs.
They typically use subword or byte-level tokenizers because those scale better
to many languages and rare strings.

Common architectural approaches:

- OpenAI-style systems use tokenization before embedding lookup and often expose
  token counting utilities for cost and context-window management.
- Anthropic-style safety systems treat prompts, tool results, and retrieved
  content as different trust domains, even though all become tokens eventually.
- Google-style systems often combine tokenizer-aware preprocessing with broader
  abuse detection, logging, and policy enforcement.
- Microsoft-style enterprise systems commonly put deterministic policy,
  identity, authorization, and audit controls around model calls.

Exact internal implementations are proprietary. The important principle is
public and common:

```text
Tokenization is not a security boundary.
Authorization, validation, and policy enforcement must live outside the model.
```

## 9. Interview Questions

Junior:

- What is a tokenizer?
- Why does a language model need integer token IDs?
- What is an unknown token?
- Why might decoding fail to recover the original input?

Mid-level:

- What is the difference between Unicode and UTF-8?
- How can zero-width characters bypass naive filters?
- Why are denylist-based text filters fragile?
- What does normalization solve, and what does it not solve?

Senior:

- How would you design logging for suspicious Unicode inputs?
- How would you make sure moderation sees the same text as the model?
- What risks appear when different services use different tokenizers?
- How would you test tokenizer behavior continuously?

Staff-level design:

- Design a text normalization and validation gateway for a multilingual AI
  assistant.
- Explain where deterministic controls belong in an LLM application.
- How would you handle Unicode security without blocking legitimate global
  users?
- How would you investigate a production incident caused by tokenizer mismatch?

## 10. Exercises

Coding exercises:

- Add a method that returns token strings instead of token IDs.
- Add a method that counts unknown characters in an input.
- Add a command-line argument so users can encode their own text.

Security exercises:

- Create five strings that look identical but have different Unicode code
  points.
- Write a detector for bidirectional override characters.
- Test whether normalization changes each attack string.

Thought exercises:

- Should all invisible characters be blocked?
- What might break if you normalize every user input?
- Who should decide whether suspicious text is allowed: the model or the
  application?
