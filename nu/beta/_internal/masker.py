"""Placeholder-based masker.

Replaces each PIIEntity with `<KIND_N>`, where N is a per-kind
counter. Mapping placeholder -> entity is in memory only (MaskResult
wraps it in MappingProxyType). Pure function: same (text, report)
produces same result. See ADR-0007.
"""

from __future__ import annotations

from nu.beta.public.interfaces import IMasker
from nu.psi.contracts.alpha import (
    DetectionReport,
    MaskResult,
    PIIEntity,
    PIIKind,
)

__all__ = ["Masker"]


class Masker(IMasker):
    def mask(self, text: str, report: DetectionReport) -> MaskResult:
        if not report.entities:
            return MaskResult(masked_text=text, mapping={}, report=report)

        counters: dict[PIIKind, int] = {}
        mapping: dict[str, PIIEntity] = {}
        parts: list[str] = []
        prev_end = 0

        for entity in report.entities:
            parts.append(text[prev_end : entity.start])
            counters[entity.kind] = counters.get(entity.kind, 0) + 1
            placeholder = f"<{entity.kind.value}_{counters[entity.kind]}>"
            mapping[placeholder] = entity
            parts.append(placeholder)
            prev_end = entity.end

        parts.append(text[prev_end:])
        return MaskResult(
            masked_text="".join(parts),
            mapping=mapping,
            report=report,
        )
