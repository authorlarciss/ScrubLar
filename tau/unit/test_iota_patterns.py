"""Tests for structured PII regex patterns."""

from nu.iota.public.patterns import (
    EMAIL_PATTERN,
    INITIALS_PATTERN,
    INN10_PATTERN,
    INN12_PATTERN,
    PASSPORT_PATTERN,
    PHONE_PATTERN,
    SNILS_FORMATTED_PATTERN,
    SNILS_RAW_PATTERN,
)


def test_phone_matches_plus7() -> None:
    assert PHONE_PATTERN.fullmatch("+79991234567")


def test_phone_matches_8() -> None:
    assert PHONE_PATTERN.fullmatch("89991234567")


def test_phone_matches_formatted() -> None:
    assert PHONE_PATTERN.fullmatch("+7 (999) 123-45-67")
    assert PHONE_PATTERN.fullmatch("8-999-123-45-67")


def test_phone_rejects_bare_10_digits() -> None:
    assert PHONE_PATTERN.fullmatch("9991234567") is None


def test_email_matches_standard() -> None:
    assert EMAIL_PATTERN.fullmatch("test@example.com")
    assert EMAIL_PATTERN.fullmatch("a.b+c@sub.domain.co.uk")


def test_email_rejects_no_local_part() -> None:
    assert EMAIL_PATTERN.fullmatch("@example.com") is None


def test_snils_formatted_matches() -> None:
    assert SNILS_FORMATTED_PATTERN.fullmatch("123-456-789 00")
    assert SNILS_FORMATTED_PATTERN.fullmatch("123-456-789-00")


def test_snils_raw_matches_11_digits() -> None:
    assert SNILS_RAW_PATTERN.fullmatch("12345678900")


def test_inn10_matches_10_digits() -> None:
    assert INN10_PATTERN.fullmatch("7707083893")


def test_inn12_matches_12_digits() -> None:
    assert INN12_PATTERN.fullmatch("500100732259")


def test_passport_matches_canonical() -> None:
    assert PASSPORT_PATTERN.fullmatch("45 06 123456")
    assert PASSPORT_PATTERN.fullmatch("4506 123456")


def test_passport_rejects_no_space() -> None:
    assert PASSPORT_PATTERN.fullmatch("4506123456") is None


def test_initials_matches_canonical() -> None:
    assert INITIALS_PATTERN.fullmatch("Сидоров А.П.")


def test_initials_matches_with_spaces_between() -> None:
    assert INITIALS_PATTERN.fullmatch("Сидоров А. П.")
    assert INITIALS_PATTERN.fullmatch("Иванова А. И.")


def test_initials_matches_short_surname() -> None:
    assert INITIALS_PATTERN.fullmatch("Ильин В.С.")


def test_initials_rejects_full_name() -> None:
    assert INITIALS_PATTERN.fullmatch("Иванов Иван Иванович") is None


def test_initials_rejects_single_initial() -> None:
    assert INITIALS_PATTERN.fullmatch("Сидоров А.") is None


def test_initials_rejects_missing_second_dot() -> None:
    assert INITIALS_PATTERN.fullmatch("Сидоров А.П") is None


def test_initials_rejects_lowercase() -> None:
    assert INITIALS_PATTERN.fullmatch("сидоров а.п.") is None


def test_initials_rejects_short_word_before_initials() -> None:
    # "А.П." alone — no surname, must not match.
    assert INITIALS_PATTERN.fullmatch("А.П.") is None
