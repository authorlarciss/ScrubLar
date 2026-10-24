"""Natasha-based NER detector for person names (ADR-0008).

Lazy model load: NewsEmbedding and NewsNERTagger are created on first
detect(). Natasha is not thread-safe during init; the first call
locks. In a FastAPI worker per process there's one instance, so no
contention in practice.
"""

from __future__ import annotations

from typing import Any

from nu.epsilon.public.interfaces import INameDetector
from nu.psi.contracts.alpha import PIIEntity, PIIKind

__all__ = ["NatashaNameDetector"]


class NatashaNameDetector(INameDetector):
    def __init__(self) -> None:
        self._segmenter: Any = None
        self._tagger: Any = None

    def _ensure_loaded(self) -> None:
        if self._tagger is None:
            from natasha import NewsEmbedding, NewsNERTagger, Segmenter

            self._segmenter = Segmenter()
            self._tagger = NewsNERTagger(NewsEmbedding())

    def detect(self, text: str) -> tuple[PIIEntity, ...]:
        self._ensure_loaded()
        from natasha import Doc

        doc = Doc(text)
        doc.segment(self._segmenter)
        doc.tag_ner(self._tagger)
        entities: list[PIIEntity] = []
        for span in doc.spans:
            if span.type == "PER":
                entities.append(
                    PIIEntity(
                        kind=PIIKind.NAME,
                        value=span.text,
                        start=span.start,
                        end=span.stop,
                    )
                )
        entities.sort(key=lambda e: e.start)
        return tuple(entities)
