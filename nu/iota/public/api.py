"""Public API for structured PII detection.

Each `find_*` returns a tuple of non-overlapping `PIIEntity` sorted by
position. `find_structured_pii` combines all kinds and resolves
overlaps by priority (EMAIL > SNILS > INN > PASSPORT > PHONE).

NER (ФИО) is not handled here — that's `epsilon`'s job; `beta.Detector`
combines iota + epsilon. See ADR-0007.
"""

from __future__ import annotations

import re

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
from nu.iota.public.validators import inn10_valid, inn12_valid, snils_valid
from nu.psi.contracts.alpha import PIIEntity, PIIKind

__all__ = [
    "find_emails",
    "find_initials",
    "find_inns",
    "find_passports",
    "find_phones",
    "find_snils",
    "find_structured_pii",
]

_PRIORITY: dict[PIIKind, int] = {
    PIIKind.EMAIL: 6,
    PIIKind.SNILS: 5,
    PIIKind.INN: 4,
    PIIKind.PASSPORT: 3,
    PIIKind.PHONE: 2,
    PIIKind.NAME: 1,
}


def _collect(pattern: re.Pattern[str], text: str, kind: PIIKind) -> list[PIIEntity]:
    return [
        PIIEntity(kind=kind, value=m.group(), start=m.start(), end=m.end())
        for m in pattern.finditer(text)
    ]


def find_emails(text: str) -> tuple[PIIEntity, ...]:
    return tuple(_collect(EMAIL_PATTERN, text, PIIKind.EMAIL))


def find_phones(text: str) -> tuple[PIIEntity, ...]:
    return tuple(_collect(PHONE_PATTERN, text, PIIKind.PHONE))


def find_passports(text: str) -> tuple[PIIEntity, ...]:
    return tuple(_collect(PASSPORT_PATTERN, text, PIIKind.PASSPORT))


def find_initials(text: str) -> tuple[PIIEntity, ...]:
    """Find surname + initials ("Сидоров А.П.") as PIIKind.NAME.

    Full names (no initials, dots) are out of scope — those go through
    NER in epsilon. See ADR-0008.
    """
    return tuple(_collect(INITIALS_PATTERN, text, PIIKind.NAME))


def find_snils(text: str) -> tuple[PIIEntity, ...]:
    result: list[PIIEntity] = []
    for m in SNILS_FORMATTED_PATTERN.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        if snils_valid(digits):
            result.append(
                PIIEntity(kind=PIIKind.SNILS, value=m.group(), start=m.start(), end=m.end())
            )
    for m in SNILS_RAW_PATTERN.finditer(text):
        if snils_valid(m.group()):
            result.append(
                PIIEntity(kind=PIIKind.SNILS, value=m.group(), start=m.start(), end=m.end())
            )
    return tuple(result)


def find_inns(text: str) -> tuple[PIIEntity, ...]:
    result: list[PIIEntity] = []
    for m in INN12_PATTERN.finditer(text):
        if inn12_valid(m.group()):
            result.append(
                PIIEntity(kind=PIIKind.INN, value=m.group(), start=m.start(), end=m.end())
            )
    for m in INN10_PATTERN.finditer(text):
        if inn10_valid(m.group()):
            result.append(
                PIIEntity(kind=PIIKind.INN, value=m.group(), start=m.start(), end=m.end())
            )
    return tuple(result)


def find_structured_pii(text: str) -> tuple[PIIEntity, ...]:
    """Find all structured PII (no NER). Sorted, non-overlapping."""
    entities: list[PIIEntity] = []
    entities.extend(find_emails(text))
    entities.extend(find_inns(text))
    entities.extend(find_snils(text))
    entities.extend(find_phones(text))
    entities.extend(find_passports(text))
    entities.extend(find_initials(text))
    return _resolve_overlaps(entities)


def _resolve_overlaps(entities: list[PIIEntity]) -> tuple[PIIEntity, ...]:
    if not entities:
        return ()
    entities.sort(key=lambda item: (-_PRIORITY[item.kind], -(item.end - item.start), item.start))
    chosen: list[PIIEntity] = []
    for entity in entities:
        if not any(_overlaps(entity, kept) for kept in chosen):
            chosen.append(entity)
    chosen.sort(key=lambda item: item.start)
    return tuple(chosen)


def _overlaps(a: PIIEntity, b: PIIEntity) -> bool:
    return a.start < b.end and b.start < a.end
