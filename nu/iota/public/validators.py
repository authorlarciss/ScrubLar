"""Checksum validators for structured PII.

SNILS and INN have check digits; PHONE, EMAIL, PASSPORT do not (format
only). Passport detection is best-effort: no checksum exists for RF
internal passports, so false positives are possible.
"""

from __future__ import annotations

__all__ = ["inn10_valid", "inn12_valid", "snils_valid"]


def _snils_control(digits9: str) -> int:
    """Compute SNILS check number (0..99) from 9 base digits."""
    weights = (9, 8, 7, 6, 5, 4, 3, 2, 1)
    total = sum(int(d) * w for d, w in zip(digits9, weights, strict=True))
    if total < 100:
        return total
    if total in (100, 101):
        return 0
    total %= 101
    if total == 100:
        return 0
    return total


def snils_valid(digits11: str) -> bool:
    """Validate 11-digit SNILS (9 base + 2 check)."""
    if len(digits11) != 11 or not digits11.isdigit():
        return False
    return _snils_control(digits11[:9]) == int(digits11[-2:])


def inn10_valid(digits10: str) -> bool:
    """Validate 10-digit INN (legal entity)."""
    if len(digits10) != 10 or not digits10.isdigit():
        return False
    weights = (2, 4, 10, 3, 5, 9, 4, 6, 8)
    total = sum(int(d) * w for d, w in zip(digits10[:9], weights, strict=True))
    return (total % 11) % 10 == int(digits10[9])


def inn12_valid(digits12: str) -> bool:
    """Validate 12-digit INN (individual)."""
    if len(digits12) != 12 or not digits12.isdigit():
        return False
    w11 = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
    w12 = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
    t11 = sum(int(d) * w for d, w in zip(digits12[:10], w11, strict=True))
    if (t11 % 11) % 10 != int(digits12[10]):
        return False
    t12 = sum(int(d) * w for d, w in zip(digits12[:11], w12, strict=True))
    return (t12 % 11) % 10 == int(digits12[11])
