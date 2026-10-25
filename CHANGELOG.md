# Changelog

All notable changes to ScrubLar are documented in this file.

Format based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-25

First release. MVP per ADR-0007: local web service for PII
anonymization in DOCX and TXT, no external calls.

### Added

- PII types (`alpha`): `PIIKind` (NAME, PHONE, EMAIL, SNILS, INN,
  PASSPORT), `PIIEntity`, `DetectionReport`, `MaskResult`,
  `DetectionConfig`, error hierarchy.
- Structured detection (`iota`): regex + checksums for phone, email,
  SNILS, INN (10/12), passport; surname + initials ("Сидоров А.П.",
  "Иванова А. И."). All-same-digit rejection for INN/SNILS.
- NER (`epsilon`): Natasha-based `NatashaNameDetector` for full
  names. 30 MB, ONNX, no torch.
- Detector (`beta`): `Detector` combines structured + NER. Structured
  wins on overlap. `Masker` with `<KIND_N>` placeholders, mapping in
  memory only.
- Parsers (`delta`): DOCX (paragraphs + tables), TXT (UTF-8 with
  cp1251 fallback).
- Web UI (`gamma`): FastAPI single-page app, `/mask` endpoint
  (multipart upload), preview with `<mark>` highlights, download
  masked.txt + report.json (client-side Blob). Errors: 400, 413,
  415, 422, 500.
- `ScrubService` (`psi`): parse → detect → mask orchestration.
  `ScrubLarApplication`: uvicorn on asyncio loop.
- CLI: `make run` at http://127.0.0.1:8000.
- ADRs: 0007 (core contract), 0008 (Natasha NER), 0009 (scaffold
  removal, IDetector), 0010 (gamma is HTTP only), 0011 (evaluation
  methodology).
- Evaluation: `tau/fixtures/generator.py` (50 docs, clean +
  adversarial, seed=42), `omega/scripts/evaluate.py` (JSON report),
  `make evaluate`.
- Metrics on synthetic: overall recall 1.0, precision 0.93.
  Structured PII: 1.0 / 1.0 each. NAME: 1.0 / 0.86.

### Changed

- BaseLar scaffold removed from beta/alpha/delta (IProcessor,
  IWorkflow, IEventBus, IEvent, IRenderer, SvgRenderer, workflow).
  See ADR-0009, ADR-0010, BaseLar ADR-0008.
- Runtime: natasha (30 MB, no torch). Adversarial evaluation is
  documented limitation, not a bug.

### Known limitations

- NAME precision 0.86 on synthetic: does not distinguish "ФИО" from
  "ООО «Иванов и партнёры»". Context-aware filtering in v0.2.
- PDF not supported (v0.2).
- Addresses, banking details, OGRN not covered (v0.2).
- 50 synthetic docs, not real-world benchmark. 20–30 manually
  labelled redacted documents in v0.2.
