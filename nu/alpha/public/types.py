"""PII domain types for ScrubLar.

Frozen dataclasses and errors for the anonymization core. All types
are immutable; `detect` and `mask` return new instances, never mutate.

See ADR-0007 for the core contract: `detect(text, config) ->
DetectionReport` and `mask(text, report) -> MaskResult`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

__all__ = [
    "DetectionConfig",
    "DetectionError",
    "DetectionReport",
    "MaskResult",
    "MaskingError",
    "PIIEntity",
    "PIIKind",
    "ParsingError",
    "ScrubLarError",
    "UnsupportedFormatError",
]


class ScrubLarError(Exception):
    """Base exception for ScrubLar domain errors."""


class DetectionError(ScrubLarError):
    """Raised when PII detection fails."""


class MaskingError(ScrubLarError):
    """Raised when masking fails (e.g., inconsistent report)."""


class ParsingError(ScrubLarError):
    """Raised when a document cannot be parsed."""


class UnsupportedFormatError(ParsingError):
    """Raised when the document format is not supported."""


class PIIKind(StrEnum):
    """Kind of personally identifiable information."""

    NAME = "NAME"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    SNILS = "SNILS"
    INN = "INN"
    PASSPORT = "PASSPORT"


@dataclass(frozen=True, slots=True)
class PIIEntity:
    """Single detected PII entity with position in source text.

    `value` must equal `text[start:end]` for the original text;
    this is enforced by the detector, not by the dataclass (the
    dataclass does not carry the source text).
    """

    kind: PIIKind
    value: str
    start: int  # inclusive
    end: int  # exclusive

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError(f"start must be >= 0, got {self.start}")
        if self.end <= self.start:
            raise ValueError(f"end must be > start, got end={self.end}, start={self.start}")
        if self.end - self.start != len(self.value):
            raise ValueError(f"span {self.end - self.start} != value length {len(self.value)}")


@dataclass(frozen=True, slots=True)
class DetectionReport:
    """Result of `detect(text, config)`.

    `entities` are non-overlapping, sorted by `start`. `text_length`
    is the length of the source text; entity `end` must be <= it.
    """

    entities: tuple[PIIEntity, ...]
    text_length: int

    def __post_init__(self) -> None:
        if self.text_length < 0:
            raise ValueError(f"text_length must be >= 0, got {self.text_length}")
        prev_end = 0
        for entity in self.entities:
            if entity.start < prev_end:
                raise ValueError(f"entities overlap at {entity.start} (prev end {prev_end})")
            if entity.end > self.text_length:
                raise ValueError(f"entity end {entity.end} > text_length {self.text_length}")
            prev_end = entity.end


@dataclass(frozen=True, slots=True)
class MaskResult:
    """Result of `mask(text, report)`.

    `mapping` is read-only: holds the placeholder -> original entity
    mapping in memory only. Never persisted to disk.
    """

    masked_text: str
    mapping: Mapping[str, PIIEntity]
    report: DetectionReport

    def __post_init__(self) -> None:
        object.__setattr__(self, "mapping", MappingProxyType(dict(self.mapping)))


@dataclass(frozen=True, slots=True)
class DetectionConfig:
    """Configuration for `detect(text, config)`.

    `enabled_kinds` limits the set of PII kinds to detect (default:
    all). `ner_model_version` is required when NAME is enabled (the
    detector validates); `None` otherwise.
    """

    enabled_kinds: frozenset[PIIKind] = field(default_factory=lambda: frozenset(PIIKind))
    ner_model_version: str | None = None
