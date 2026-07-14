"""
Phase 3: Byte Pair Encoding (BPE) Tokenizer

Character tokenization from Phase 1 works, but it is verbose.
BPE learns frequent character pairs and merges them into larger tokens.
That compression is powerful, and it is also where filter mismatch begins.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class MergeRule:
    left: str
    right: str
    merged: str
    count: int


class BPETokenizer:
    """
    A tiny BPE tokenizer for teaching.

    Training starts from characters, then repeatedly merges the most frequent
    adjacent pair into a new token until max_merges is reached.
    """

    def __init__(
        self,
        vocabulary: list[str],
        merges: list[MergeRule],
        unknown_token: str = "<UNK>",
    ) -> None:
        if unknown_token in vocabulary:
            raise ValueError("Unknown token should not already be in the vocabulary.")

        self.unknown_token = unknown_token
        self.merges = list(merges)
        self.id_to_token = [unknown_token] + vocabulary
        self.token_to_id = {token: token_id for token_id, token in enumerate(self.id_to_token)}
        self.unknown_id = self.token_to_id[unknown_token]
        self.merge_lookup = {(rule.left, rule.right): rule.merged for rule in self.merges}

    @classmethod
    def train(
        cls,
        corpus: str,
        max_merges: int = 20,
        unknown_token: str = "<UNK>",
        verbose: bool = False,
    ) -> "BPETokenizer":
        """
        Train BPE merges from a corpus.

        Algorithm:
        1. Split text into individual characters (with a word_end marker).
        2. Count adjacent pairs across the corpus.
        3. Merge the most frequent pair into one token.
        4. Repeat until max_merges or no pairs remain.
        """
        words = _split_into_training_words(corpus)
        vocabulary = sorted({character for word in words for character in word})
        merges: list[MergeRule] = []

        for step in range(1, max_merges + 1):
            pair_counts = _count_adjacent_pairs(words)
            if not pair_counts:
                break

            (left, right), count = pair_counts.most_common(1)[0]
            merged = left + right
            merges.append(MergeRule(left=left, right=right, merged=merged, count=count))

            if merged not in vocabulary:
                vocabulary.append(merged)

            words = [_apply_merge_to_word(word, left, right, merged) for word in words]

            if verbose:
                print(f"Merge {step:02d}: ({left!r}, {right!r}) -> {merged!r}  count={count}")
                print(f"  Vocabulary size: {len(vocabulary) + 1}")  # +1 for <UNK>

        vocabulary = sorted(set(vocabulary), key=lambda token: (len(token), token))
        return cls(vocabulary=vocabulary, merges=merges, unknown_token=unknown_token)

    def encode(self, text: str) -> list[int]:
        """Encode text by applying learned merges in training order, then mapping to IDs."""
        words = _split_into_training_words(text)
        encoded: list[int] = []

        for word in words:
            tokens = list(word)
            for rule in self.merges:
                tokens = _apply_merge_to_word(tokens, rule.left, rule.right, rule.merged)
            encoded.extend(self.token_to_id.get(token, self.unknown_id) for token in tokens)

        return encoded

    def decode(self, token_ids: list[int]) -> str:
        """Decode token IDs back into text. Word end markers become spaces."""
        pieces: list[str] = []

        for token_id in token_ids:
            if token_id < 0 or token_id >= len(self.id_to_token):
                raise ValueError(f"Token ID {token_id} is outside the vocabulary.")
            pieces.append(self.id_to_token[token_id])

        text = "".join(pieces).replace("</w>", " ")
        return text.strip()

    def tokenize(self, text: str) -> list[str]:
        """Return the token strings produced by BPE, useful for visualization."""
        words = _split_into_training_words(text)
        tokens: list[str] = []

        for word in words:
            pieces = list(word)
            for rule in self.merges:
                pieces = _apply_merge_to_word(pieces, rule.left, rule.right, rule.merged)
            tokens.extend(pieces)

        return tokens

    @property
    def vocabulary_size(self) -> int:
        return len(self.id_to_token)


def _split_into_training_words(text: str) -> list[list[str]]:
    """
    Split text into words, then into characters, marking word boundaries with </w>.

    Example:
        "secure llm" -> [["s","e","c","u","r","e","</w>"], ["l","l","m","</w>"]]
    """
    words: list[list[str]] = []

    for word in text.split():
        characters = list(word) + ["</w>"]
        words.append(characters)

    return words


def _count_adjacent_pairs(words: list[list[str]]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()

    for word in words:
        for left, right in zip(word, word[1:]):
            counts[(left, right)] += 1

    return counts


def _apply_merge_to_word(
    tokens: list[str],
    left: str,
    right: str,
    merged: str,
) -> list[str]:
    """Scan left to right and merge the first matching adjacent pair repeatedly."""
    if len(tokens) < 2:
        return list(tokens)

    result: list[str] = []
    index = 0

    while index < len(tokens):
        if index < len(tokens) - 1 and tokens[index] == left and tokens[index + 1] == right:
            result.append(merged)
            index += 2
        else:
            result.append(tokens[index])
            index += 1

    return result


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def demo_train_with_merge_trace() -> BPETokenizer:
    print_section("1. Train BPE and Watch Merges")
    corpus = (
        "secure llm secure llm "
        "hello secure world "
        "secure models learn from text "
        "low level language model security"
    )
    print("Corpus:")
    print(corpus)
    print()
    tokenizer = BPETokenizer.train(corpus, max_merges=15, verbose=True)
    print()
    print(f"Final vocabulary size: {tokenizer.vocabulary_size}")
    print("Learned merges:")
    for index, rule in enumerate(tokenizer.merges, start=1):
        print(f"{index:02d}. ({rule.left!r}, {rule.right!r}) -> {rule.merged!r}  count={rule.count}")
    return tokenizer


def demo_encode_decode(tokenizer: BPETokenizer) -> None:
    print_section("2. Encode and Decode")
    text = "secure llm"
    tokens = tokenizer.tokenize(text)
    ids = tokenizer.encode(text)
    decoded = tokenizer.decode(ids)

    print("Input text:", text)
    print("BPE tokens:", tokens)
    print("Token IDs: ", ids)
    print("Decoded:   ", decoded)


def demo_compression_vs_characters(tokenizer: BPETokenizer) -> None:
    print_section("3. Compression vs Character Tokenizer")
    text = "secure language model security"
    char_tokens = list(text.replace(" ", ""))
    bpe_tokens = [token for token in tokenizer.tokenize(text) if token != "</w>"]

    print("Input:", text)
    print(f"Character pieces (ignoring spaces): {len(char_tokens)}")
    print(f"BPE pieces (ignoring word ends):    {len(bpe_tokens)}")
    print("Character tokens:", char_tokens)
    print("BPE tokens:      ", bpe_tokens)
    print("Lesson: BPE compresses frequent patterns into fewer tokens.")


def demo_filter_mismatch() -> None:
    print_section("4. Security: Filter Mismatch Across Tokenizers")

    # Two tiny tokenizers trained on overlapping but different corpora.
    # Same surface string, different splits.
    security_corpus = "ignore previous instructions ignore previous instructions"
    chat_corpus = "please ignore spam please ignore spam please ignore spam"

    security_tokenizer = BPETokenizer.train(security_corpus, max_merges=8)
    chat_tokenizer = BPETokenizer.train(chat_corpus, max_merges=8)

    payload = "ignore previous instructions"
    security_tokens = security_tokenizer.tokenize(payload)
    chat_tokens = chat_tokenizer.tokenize(payload)

    print("Payload:", payload)
    print()
    print("Security tokenizer tokens:")
    print(security_tokens)
    print()
    print("Chat tokenizer tokens:")
    print(chat_tokens)
    print()
    print("Same text. Different tokenizations.")
    print("A filter that blocks one token sequence may miss the other.")


def demo_token_splitting_bypass() -> None:
    print_section("5. Security: Token Splitting Bypass Pattern")

    corpus = "admin admin administrator administer"
    tokenizer = BPETokenizer.train(corpus, max_merges=10)

    samples = ["admin", "administrator", "ad min", "АДМИН"]
    blocked_token = "admin</w>"

    print(f"Suppose a naive token filter blocks exactly: {blocked_token!r}")
    print()

    for sample in samples:
        tokens = tokenizer.tokenize(sample.lower() if sample.isascii() else sample)
        blocked = blocked_token in tokens
        print(f"Input: {sample!r}")
        print(f"  Tokens:  {tokens}")
        print(f"  Blocked: {blocked}")
        print()

    print("Lesson: token blockers that match whole surface words are fragile.")
    print("BPE can split, merge, and reshape the same intent differently.")


def demo_unknown_and_rare_text(tokenizer: BPETokenizer) -> None:
    print_section("6. Unknown Tokens Still Exist")
    text = "secure llm 🔐"
    tokens = tokenizer.tokenize(text)
    ids = tokenizer.encode(text)

    print("Input:", text)
    print("Tokens:", tokens)
    print("IDs:   ", ids)
    print("Any character outside the learned alphabet becomes <UNK>.")
    print("Byte level tokenizers avoid <UNK>, but introduce different complexity.")


def run_demo() -> None:
    tokenizer = demo_train_with_merge_trace()
    demo_encode_decode(tokenizer)
    demo_compression_vs_characters(tokenizer)
    demo_filter_mismatch()
    demo_token_splitting_bypass()
    demo_unknown_and_rare_text(tokenizer)
    print_section("7. Takeaway")
    print("BPE compresses frequent pairs into reusable tokens.")
    print("Different corpora produce different merges and different splits.")
    print("Security filters that depend on exact token IDs or exact token strings")
    print("will diverge across models. Canonicalize and decide at the text layer")
    print("before tokenization whenever deterministic security is required.")


if __name__ == "__main__":
    run_demo()
