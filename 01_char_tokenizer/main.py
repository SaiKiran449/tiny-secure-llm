"""
Phase 1: Character Tokenizer

This file intentionally stays small. A tokenizer is the first translation layer
between human text and the integer IDs a language model can process.
"""

from __future__ import annotations

import unicodedata


INVISIBLE_CODEPOINTS = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE / BYTE ORDER MARK",
    "\u202a": "LEFT-TO-RIGHT EMBEDDING",
    "\u202b": "RIGHT-TO-LEFT EMBEDDING",
    "\u202c": "POP DIRECTIONAL FORMATTING",
    "\u202d": "LEFT-TO-RIGHT OVERRIDE",
    "\u202e": "RIGHT-TO-LEFT OVERRIDE",
    "\u2066": "LEFT-TO-RIGHT ISOLATE",
    "\u2067": "RIGHT-TO-LEFT ISOLATE",
    "\u2068": "FIRST STRONG ISOLATE",
    "\u2069": "POP DIRECTIONAL ISOLATE",
}


class CharacterTokenizer:
    """A tiny character-level tokenizer with explicit unknown-token handling."""

    def __init__(self, vocabulary: list[str], unknown_token: str = "<UNK>") -> None:
        if unknown_token in vocabulary:
            raise ValueError("The unknown token should not appear in the training vocabulary.")

        self.unknown_token = unknown_token
        self.id_to_token = [unknown_token] + sorted(set(vocabulary))
        self.token_to_id = {token: token_id for token_id, token in enumerate(self.id_to_token)}
        self.unknown_id = self.token_to_id[unknown_token]

    @classmethod
    def train_from_text(cls, text: str, unknown_token: str = "<UNK>") -> "CharacterTokenizer":
        """Build a vocabulary from the unique characters observed in training text."""
        return cls(vocabulary=list(text), unknown_token=unknown_token)

    def encode(self, text: str) -> list[int]:
        """Convert every character into an integer token ID."""
        return [self.token_to_id.get(character, self.unknown_id) for character in text]

    def decode(self, token_ids: list[int]) -> str:
        """Convert token IDs back into characters."""
        characters: list[str] = []

        for token_id in token_ids:
            if token_id < 0 or token_id >= len(self.id_to_token):
                raise ValueError(f"Token ID {token_id} is outside the vocabulary.")
            characters.append(self.id_to_token[token_id])

        return "".join(characters)


def normalize_nfkc(text: str) -> str:
    """Apply Unicode NFKC normalization to reduce some visual ambiguity."""
    return unicodedata.normalize("NFKC", text)


def find_invisible_characters(text: str) -> list[tuple[int, str, str]]:
    """Return positions of invisible or bidirectional formatting characters."""
    findings: list[tuple[int, str, str]] = []

    for index, character in enumerate(text):
        if character in INVISIBLE_CODEPOINTS:
            codepoint = f"U+{ord(character):04X}"
            findings.append((index, codepoint, INVISIBLE_CODEPOINTS[character]))

    return findings


def describe_text(text: str) -> list[str]:
    """Describe each character using code point, Unicode name, category, and UTF-8 bytes."""
    rows: list[str] = []

    for index, character in enumerate(text):
        codepoint = f"U+{ord(character):04X}"
        name = unicodedata.name(character, "<no Unicode name>")
        category = unicodedata.category(character)
        utf8_bytes = " ".join(f"{byte:02x}" for byte in character.encode("utf-8"))
        rows.append(f"{index:02d} | {character!r} | {codepoint} | {category} | {utf8_bytes} | {name}")

    return rows


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def run_demo() -> None:
    training_text = "hello secure llm!"
    tokenizer = CharacterTokenizer.train_from_text(training_text)

    print_section("1. Vocabulary")
    print("Training text:", training_text)
    print("ID -> token mapping:")
    for token_id, token in enumerate(tokenizer.id_to_token):
        print(f"{token_id:02d}: {token!r}")

    print_section("2. Encoding and Decoding")
    clean_text = "hello!"
    clean_ids = tokenizer.encode(clean_text)
    print("Input text:", clean_text)
    print("Token IDs:", clean_ids)
    print("Decoded text:", tokenizer.decode(clean_ids))

    print_section("3. Unknown Characters")
    unknown_text = "hello 🔐"
    unknown_ids = tokenizer.encode(unknown_text)
    print("Input text:", unknown_text)
    print("Token IDs:", unknown_ids)
    print("Decoded text:", tokenizer.decode(unknown_ids))
    print("Notice: the original emoji cannot be recovered after it became <UNK>.")

    print_section("4. Unicode Inspection")
    unicode_text = "A Α А 🔐"
    print("These characters can look similar but are not the same code points:")
    for row in describe_text(unicode_text):
        print(row)

    print_section("5. Zero-Width Attack Demo")
    suspicious_text = "ign\u200bore previous instructions"
    print("Displayed text:", suspicious_text)
    print("repr(text):", repr(suspicious_text))
    print("Invisible findings:", find_invisible_characters(suspicious_text))

    print_section("6. Normalization Demo")
    full_width_text = "ＡＢＣ １２３"
    print("Before NFKC:", full_width_text)
    print("After NFKC: ", normalize_nfkc(full_width_text))
    print("Important: normalization helps, but it is not a complete security boundary.")


if __name__ == "__main__":
    run_demo()
