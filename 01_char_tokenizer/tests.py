"""
Focused tests for Phase 1.

Run:
    python 01_char_tokenizer/tests.py
"""

from __future__ import annotations

from main import CharacterTokenizer, find_invisible_characters, normalize_nfkc


def test_round_trip_known_characters() -> None:
    tokenizer = CharacterTokenizer.train_from_text("abc")

    token_ids = tokenizer.encode("cab")
    decoded = tokenizer.decode(token_ids)

    assert decoded == "cab"


def test_unknown_character_uses_unknown_token() -> None:
    tokenizer = CharacterTokenizer.train_from_text("abc")

    token_ids = tokenizer.encode("a🙂c")
    decoded = tokenizer.decode(token_ids)

    assert token_ids[1] == tokenizer.unknown_id
    assert decoded == "a<UNK>c"


def test_invalid_token_id_is_rejected() -> None:
    tokenizer = CharacterTokenizer.train_from_text("abc")

    try:
        tokenizer.decode([999])
    except ValueError as error:
        assert "outside the vocabulary" in str(error)
    else:
        raise AssertionError("decode() should reject token IDs outside the vocabulary.")


def test_nfkc_normalizes_full_width_characters() -> None:
    assert normalize_nfkc("ＡＢＣ １２３") == "ABC 123"


def test_zero_width_character_detection() -> None:
    text = "ign\u200bore"

    findings = find_invisible_characters(text)

    assert findings == [(3, "U+200B", "ZERO WIDTH SPACE")]


def run_all_tests() -> None:
    test_round_trip_known_characters()
    test_unknown_character_uses_unknown_token()
    test_invalid_token_id_is_rejected()
    test_nfkc_normalizes_full_width_characters()
    test_zero_width_character_detection()
    print("All Phase 1 tests passed.")


if __name__ == "__main__":
    run_all_tests()
