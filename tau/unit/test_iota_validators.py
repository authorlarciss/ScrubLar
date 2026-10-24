"""Tests for SNILS and INN checksum validators."""

import pytest

from nu.iota.public.validators import inn10_valid, inn12_valid, snils_valid


@pytest.mark.parametrize(
    "snils", ["11223344595", "112-233-445 95".replace("-", "").replace(" ", "")]
)
def test_snils_valid_known_good(snils: str) -> None:
    assert snils_valid(snils)


def test_snils_invalid_checksum() -> None:
    assert not snils_valid("11223344500")


def test_snils_rejects_wrong_length() -> None:
    assert not snils_valid("123")
    assert not snils_valid("")


def test_snils_rejects_non_digits() -> None:
    assert not snils_valid("1122334459X")


def test_inn10_valid() -> None:
    assert inn10_valid("7707083893")


def test_inn10_invalid_checksum() -> None:
    assert not inn10_valid("7707083894")


def test_inn10_rejects_wrong_length() -> None:
    assert not inn10_valid("770708389")


def test_inn12_valid() -> None:
    assert inn12_valid("500100732259")


def test_inn12_invalid_checksum() -> None:
    assert not inn12_valid("500100732257")


def test_inn12_rejects_wrong_length() -> None:
    assert not inn12_valid("50010073225")


def test_snils_control_returns_zero_when_total_100() -> None:
    """Base sum == 100 → check = 0 (SNILS 322222223 00)."""
    # 3*9 + 2*8 + 2*7 + 2*6 + 2*5 + 2*4 + 2*3 + 2*2 + 3*1 = 100
    assert snils_valid("32222222300")


def test_snils_control_returns_zero_when_mod_101_is_100() -> None:
    """Base sum > 101, sum % 101 == 100 → check = 0 (SNILS 554445444 00)."""
    # 5*9 + 5*8 + 4*7 + 4*6 + 4*5 + 5*4 + 4*3 + 4*2 + 4*1 = 201
    # 201 % 101 == 100 → check = 0
    assert snils_valid("55444544400")


def test_inn12_invalid_first_check() -> None:
    """First check digit (index 10) wrong — returns False at line 51."""
    # Valid INN12: 500100732259. Index 10 ("5") → "9" fails first check.
    assert not inn12_valid("500100732299")
