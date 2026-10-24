"""Compiled regex patterns for structured PII.

Patterns are permissive; validation (checksums for SNILS/INN) happens
in validators.py. Patterns use re.ASCII so \\b, \\d, \\w are ASCII-only
— Cyrillic letters and digits are never matched by \\d.
"""

from __future__ import annotations

import re

__all__ = [
    "EMAIL_PATTERN",
    "INITIALS_PATTERN",
    "INN10_PATTERN",
    "INN12_PATTERN",
    "PASSPORT_PATTERN",
    "PHONE_PATTERN",
    "SNILS_FORMATTED_PATTERN",
    "SNILS_RAW_PATTERN",
]

# Phone: +7XXXXXXXXXX, 8XXXXXXXXXX, and variants with spaces/dashes/parens.
# Negative lookbehind for digit or "+" prevents matching inside longer
# numeric or "++"-prefixed sequences.
PHONE_PATTERN = re.compile(
    r"(?<![\d+])(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\d)",
    re.ASCII,
)

# Email: RFC-subset. No anchors — finditer handles position.
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.ASCII,
)

# SNILS formatted: XXX-XXX-XXX YY or XXX-XXX-XXX-YY.
SNILS_FORMATTED_PATTERN = re.compile(
    r"\b\d{3}-\d{3}-\d{3}[ \-]?\d{2}\b",
    re.ASCII,
)

# SNILS raw: 11 consecutive digits. Negative lookbehind for "+" so a
# phone like +79991234567 is not picked up as SNILS.
SNILS_RAW_PATTERN = re.compile(
    r"(?<!\+)(?<!\d)\d{11}(?!\d)",
    re.ASCII,
)

# INN: 10 (legal) or 12 (individual) digits, not inside a longer number.
INN10_PATTERN = re.compile(r"(?<!\d)\d{10}(?!\d)", re.ASCII)
INN12_PATTERN = re.compile(r"(?<!\d)\d{12}(?!\d)", re.ASCII)

# RF internal passport: series 4 digits + number 6 digits, with a space
# between groups. Canonical "XX XX NNNNNN" or combined "XXXX NNNNNN".
# No checksum; conservative format only to reduce false positives.
PASSPORT_PATTERN = re.compile(r"\b\d{2}\s?\d{2}\s+\d{6}\b", re.ASCII)

# Surname + initials: "Сидоров А.П.", "Иванова А. И.".
# Requires 3+ chars in surname (excludes 1-letter words), both
# initials capitalized with mandatory dots, no newlines between.
#
# Known false positive: "Москва А.С." — rare in business documents;
# documented in tests. Mitigation in v0.2: surname suffix check or
# NER cross-validation.
INITIALS_PATTERN = re.compile(
    r"(?<![А-ЯЁа-яё])[А-ЯЁ][а-яё]{2,}[ \t]+[А-ЯЁ]\.[ \t]?[А-ЯЁ]\.",
    re.ASCII,
)
