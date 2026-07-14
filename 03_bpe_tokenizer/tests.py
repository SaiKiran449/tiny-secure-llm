"""
Tests for Phase 3: BPE Tokenizer.

Run:
    python3 03_bpe_tokenizer/tests.py
"""

from __future__ import annotations

from main import BPETokenizer, _apply_merge_to_word, _count_adjacent_pairs


def test_train_learns_merges() -> None:
    tokenizer = BPETokenizer.train("secure secure secure llm llm", max_merges=5)

    assert len(tokenizer.merges) > 0
    assert tokenizer.vocabulary_size > 1


def test_encode_decode_round_trip() -> None:
    tokenizer = BPETokenizer.train(
        "secure llm secure llm hello world language model",
        max_merges=12,
    )
    text = "secure llm"
    decoded = tokenizer.decode(tokenizer.encode(text))

    assert decoded == text


def test_tokenize_is_shorter_than_characters_for_frequent_words() -> None:
    corpus = "secure " * 20 + "llm " * 20
    tokenizer = BPETokenizer.train(corpus, max_merges=10)
    tokens = tokenizer.tokenize("secure")

    # After merges, "secure</w>" should not remain as six separate letters plus </w>.
    assert len(tokens) < 7


def test_apply_merge_left_to_right() -> None:
    tokens = ["a", "b", "a", "b"]
    merged = _apply_merge_to_word(tokens, "a", "b", "ab")

    assert merged == ["ab", "ab"]


def test_pair_counts() -> None:
    words = [["a", "b", "c"], ["a", "b"]]
    counts = _count_adjacent_pairs(words)

    assert counts[("a", "b")] == 2
    assert counts[("b", "c")] == 1


def test_unknown_character_maps_to_unk() -> None:
    tokenizer = BPETokenizer.train("abc abc abc", max_merges=3)
    ids = tokenizer.encode("ab🔐")

    assert tokenizer.unknown_id in ids


def test_different_corpora_tokenize_differently() -> None:
    tokenizer_a = BPETokenizer.train("ignore ignore ignore previous", max_merges=6)
    tokenizer_b = BPETokenizer.train("please please please ignore", max_merges=6)

    tokens_a = tokenizer_a.tokenize("ignore")
    tokens_b = tokenizer_b.tokenize("ignore")

    # Both should encode successfully, but merge history may differ.
    assert tokens_a
    assert tokens_b
    assert tokenizer_a.merges != tokenizer_b.merges or tokens_a != tokens_b


def test_invalid_token_id_raises() -> None:
    tokenizer = BPETokenizer.train("hi hi hi", max_merges=2)

    try:
        tokenizer.decode([9999])
    except ValueError as error:
        assert "outside the vocabulary" in str(error)
    else:
        raise AssertionError("decode() should reject invalid token IDs")


def run_all_tests() -> None:
    test_train_learns_merges()
    test_encode_decode_round_trip()
    test_tokenize_is_shorter_than_characters_for_frequent_words()
    test_apply_merge_left_to_right()
    test_pair_counts()
    test_unknown_character_maps_to_unk()
    test_different_corpora_tokenize_differently()
    test_invalid_token_id_raises()
    print("All Phase 3 tests passed.")


if __name__ == "__main__":
    run_all_tests()
