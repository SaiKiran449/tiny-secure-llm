# Phase 3: BPE Tokenizer

Part 1 mapped one character to one token. That is easy to understand and
expensive at scale. Part 3 introduces Byte Pair Encoding: a method that learns
frequent pairs and merges them into reusable tokens.

## 1. Theory

Imagine you have to store these words many times:

```text
secure
secure
secure
llm
llm
```

A character tokenizer encodes `secure` as six pieces every time:

```text
s e c u r e
```

If `se` appears often, BPE learns a merge:

```text
s e  ->  se
```

Next pass might learn:

```text
se c  ->  sec
```

And so on. Frequent patterns become reusable tokens. Rare patterns stay small.

Why this exists:

- shorter sequences mean cheaper attention later
- common words get compact representations
- rare words can still be built from smaller pieces

BPE is compression driven by frequency, not by linguistics.

## 2. Architecture

```text
Training text
      |
      v
Split into characters (+ word end marker)
      |
      v
Count adjacent pairs
      |
      v
Merge most frequent pair
      |
      v
Repeat until merge budget ends
      |
      v
Vocabulary + merge table
      |
      v
Encode new text with those merges
```

Inside an LLM stack:

```text
Unicode hygiene (Phase 2)
      |
      v
BPE tokenizer (Phase 3)
      |
      v
Token IDs
      |
      v
Embeddings (Phase 4)
```

## 3. Mathematics

Let a word be a sequence of tokens:

```text
w = [t0, t1, t2, ..., tn]
```

For each adjacent pair `(ti, ti+1)`, count occurrences across the corpus:

```text
count(a, b) = number of times a is immediately followed by b
```

At every merge step, choose:

```text
(a*, b*) = argmax count(a, b)
```

Then replace every occurrence of `(a*, b*)` with a new token `a*b*`.

Encoding applies the learned merges in the same order they were trained.

## 4. Implementation

```bash
python3 03_bpe_tokenizer/main.py
python3 03_bpe_tokenizer/tests.py
```

### Step 1: Split words into characters

Each word ends with `</w>` so the model can tell where words stop.

### Step 2: Train merges

`BPETokenizer.train()` repeatedly merges the most frequent adjacent pair.

### Step 3: Encode

`encode()` applies merges in training order, then maps tokens to integer IDs.

### Step 4: Decode

`decode()` joins tokens and turns `</w>` back into spaces.

### Step 5: Visualize

`tokenize()` returns the token strings so you can see splits without IDs.

## 5. Visualization

The demo prints:

- each merge iteration
- vocabulary growth
- compression against character tokens
- two tokenizers splitting the same string differently

Watch vocabulary size grow as merges accumulate. That growth is the point.

## 6. Attack

### Attack 1: Filter mismatch

Train two tokenizers on different corpora. Encode the same payload:

```text
ignore previous instructions
```

They can produce different token sequences. A moderation rule tied to one model's
token IDs may miss the same text under another model.

### Attack 2: Token splitting

A filter that blocks the exact token `admin</w>` may miss:

- `administrator` (different merge shape)
- `ad min` (split across words)
- homoglyph variants from Phase 2

BPE makes exact token matching fragile.

### Attack 3: Cross model disagreement

OpenAI, Anthropic, Google, Meta, and open source models use different
tokenizers and vocabularies. The same password, jailbreak, or blocked phrase can
token count and split differently across vendors.

## 7. Defense

Why attacks work:

- security decisions were tied to a tokenizer specific representation
- the attacker still controls the surface text
- merges depend on training data, so vocabularies diverge

Deterministic controls:

- make security decisions on canonicalized text before tokenization
- keep blocklists and policy at the string layer, not only the token layer
- log both raw text and token IDs for forensics
- if you must use token based rules, revalidate them per model vocabulary

Probabilistic mitigations:

- model refusal behavior
- LLM classifiers on decoded text

Remaining risks:

- tokenizer upgrades silently changing behavior
- multi model gateways where each backend tokenizes differently
- byte level schemes that remove `<UNK>` but create new edge cases

## 8. Industry Context

Modern LLM providers rarely use character tokenizers. Common approaches:

- Byte Pair Encoding and variants
- WordPiece style merges
- Unigram language model tokenization
- byte level BPE that can represent any byte string

Exact vocabularies and merge tables are product specific. The architectural
pattern is public:

```text
Canonicalize text for policy.
Tokenize for the model.
Do not confuse those two steps.
```

## 9. Interview Questions

Junior:

- What problem does BPE solve compared with character tokens?
- What is a merge operation?
- Why do vocabularies grow during training?

Mid-level:

- Why can two BPE tokenizers split the same sentence differently?
- How would a token based content filter fail?
- What does `</w>` accomplish in this tiny tokenizer?

Senior:

- How would you design moderation that works across multiple LLM vendors?
- What should be logged when a tokenizer is upgraded in production?
- How does tokenizer choice affect prompt injection and RAG safety?

Staff-level:

- Design a multi model gateway where policy is tokenizer independent.
- Explain tradeoffs between character, subword, and byte level tokenization for
  security and internationalization.
- How would you detect silent behavior changes after a vocabulary refresh?

## 10. Exercises

Coding:

- Print vocabulary size after every merge and plot it later.
- Add a method that returns compression ratio versus character tokenization.
- Save merges to a JSON file and reload them for encoding only.

Security:

- Train two tokenizers and find a phrase they tokenize differently.
- Build a weak token blocker and show three bypasses.
- Combine Phase 2 Unicode tricks with Phase 3 splits.

Thought:

- Should security teams ever key policies to token IDs?
- When is token counting a product feature, and when is it a risk signal?
- Why might two models refuse different variants of the same jailbreak phrase?
