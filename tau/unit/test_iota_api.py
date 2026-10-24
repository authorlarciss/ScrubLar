"""Tests for structured PII detection API."""

from nu.iota.public.api import (
    find_emails,
    find_initials,
    find_inns,
    find_passports,
    find_phones,
    find_snils,
    find_structured_pii,
)


def test_find_emails_extracts() -> None:
    entities = find_emails("Пишите на test@example.com или a.b+c@sub.domain.co.uk")
    assert len(entities) == 2
    assert {e.value for e in entities} == {
        "test@example.com",
        "a.b+c@sub.domain.co.uk",
    }
    assert all(e.kind.name == "EMAIL" for e in entities)


def test_find_phones_extracts() -> None:
    entities = find_phones("Звоните: +79991234567 или 8 (999) 123-45-67")
    assert len(entities) == 2
    assert all(e.kind.name == "PHONE" for e in entities)


def test_find_phones_ignores_bare_10_digits() -> None:
    assert find_phones("9991234567") == ()


def test_find_snils_valid_only() -> None:
    # "112-233-445 95" passes checksum; "123-456-789 00" does not.
    text = "СНИЛС: 112-233-445 95, другой: 123-456-789 00"
    entities = find_snils(text)
    assert len(entities) == 1
    assert entities[0].value == "112-233-445 95"


def test_find_snils_skips_phone_with_plus() -> None:
    # +79991234567 must not be picked up as raw 11-digit SNILS.
    entities = find_snils("+79991234567")
    assert entities == ()


def test_find_inns_valid_only() -> None:
    # 7707083893 is valid INN10, 7707083894 is not.
    text = "ИНН: 7707083893, ошибочный: 7707083894"
    entities = find_inns(text)
    assert len(entities) == 1
    assert entities[0].value == "7707083893"


def test_find_inns_12_digit() -> None:
    entities = find_inns("ИНН физлица: 500100732259")
    assert len(entities) == 1
    assert entities[0].value == "500100732259"


def test_find_passports_canonical() -> None:
    entities = find_passports("Паспорт: 45 06 123456")
    assert len(entities) == 1
    assert entities[0].value == "45 06 123456"


def test_find_passports_no_false_positive_on_inn() -> None:
    # INN 7707083893 must not match passport pattern.
    entities = find_passports("7707083893")
    assert entities == ()


def test_find_structured_pii_mixed() -> None:
    text = (
        "Телефон +79991234567, email test@example.com, "
        "СНИЛС 112-233-445 95, ИНН 7707083893, паспорт 45 06 123456."
    )
    entities = find_structured_pii(text)
    kinds = [e.kind.name for e in entities]
    assert "PHONE" in kinds
    assert "EMAIL" in kinds
    assert "SNILS" in kinds
    assert "INN" in kinds
    assert "PASSPORT" in kinds
    # Sorted by start, non-overlapping (guaranteed by API).
    for prev, curr in zip(entities, entities[1:], strict=False):
        assert prev.end <= curr.start


def test_find_structured_pii_empty() -> None:
    assert find_structured_pii("Ничего персонального.") == ()


def test_find_structured_pii_resolves_overlap() -> None:
    # Phone +79991234567 must not produce both PHONE and SNILS entities.
    entities = find_structured_pii("+79991234567")
    assert len(entities) == 1
    assert entities[0].kind.name == "PHONE"


def test_find_structured_pii_overlap_snils_wins_over_phone() -> None:
    """11-digit number matching both PHONE (8...) and SNILS raw.

    89991234594:
    - PHONE: 8 999 123 45 94 — matches.
    - SNILS: first 9 digits "899912345", sum with weights = 296,
      296 % 101 = 94, last two = "94" — checksum matches.
    Priority: SNILS (5) > PHONE (2) → PHONE rejected in overlap.
    """
    entities = find_structured_pii("89991234594")
    assert len(entities) == 1
    assert entities[0].kind.name == "SNILS"
    assert entities[0].value == "89991234594"


def test_find_snils_skips_invalid_raw() -> None:
    """11-digit number, matches SNILS_RAW, fails checksum — loop-back branch."""
    # 89991234567: first 9 digits → 296; 296 % 101 = 94; last two "67" ≠ 94.
    assert find_snils("89991234567") == ()


def test_find_inns_skips_invalid_12_digit() -> None:
    """12-digit number, matches INN12, fails checksum — loop-back branch."""
    # 500100732257: second check fails; INN10 doesn't match inside 12 digits.
    assert find_inns("500100732257") == ()


def test_find_initials_extracts() -> None:
    entities = find_initials("Подписал Сидоров А.П. и Иванова А. И.")
    assert len(entities) == 2
    assert {e.value for e in entities} == {"Сидоров А.П.", "Иванова А. И."}
    assert all(e.kind.name == "NAME" for e in entities)


def test_find_initials_rejects_full_name() -> None:
    assert find_initials("Иванов Иван Иванович") == ()


def test_find_initials_known_false_positive_geography() -> None:
    """Known limitation: 'Москва А.С.' matches (city + initials).

    Rare in business documents; mitigation in v0.2 (surname suffix
    check or NER cross-validation).
    """
    entities = find_initials("Москва А.С.")
    assert len(entities) == 1  # documented false positive


def test_find_structured_pii_includes_initials() -> None:
    text = "Клиент: Сидоров А.П., телефон +79991234567, email test@example.com."
    entities = find_structured_pii(text)
    kinds = [e.kind.name for e in entities]
    assert "NAME" in kinds
    assert "PHONE" in kinds
    assert "EMAIL" in kinds
    # Non-overlapping, sorted
    for prev, curr in zip(entities, entities[1:], strict=False):
        assert prev.end <= curr.start
