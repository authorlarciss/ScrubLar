# ADR-0009: Удаление BaseLar scaffold, IDetector как ядро beta

## Контекст

BaseLar v0.5.0 поставляет scaffold в `beta`/`alpha`:
`IProcessor`, `IWorkflow`, `PipelineWorkflow`, `IEventBus`, `IEvent`.
ScrubLar — не pipeline: две чистые функции (`detect`, `mask`, ADR-0007).
Scaffold не используется ни одним модулем. ADR-0008 BaseLar разрешает
удаление scaffold через ADR (прецедент — TirLar ADR-0007).

## Решение

Удалить scaffold:
- `nu/alpha/public/events.py` (`IEvent`),
- `nu/beta/_internal/workflow.py` (`PipelineWorkflow`),
- `IProcessor`, `IWorkflow`, `IEventBus` из `beta/public/interfaces.py`.

Добавить `IDetector` в `beta`: `detect(text, config) -> DetectionReport`.
Реализация `Detector` объединяет `iota.find_structured_pii` (regex +
checksums, включая инициалы) и `epsilon.INameDetector` (Natasha, полные
ФИО). Merge: structured выигрывает на пересечении (детерминированный >
статистический).

`BetaResolver.make_detector(name_detector)` — фабрика. `psi.bootstrap`
собирает `Detector` с `NatashaNameDetector` через `EpsilonResolver`.

## Альтернативы

1. Оставить scaffold рядом с `IDetector`. Отвергнуто: мёртвый код,
   соблазн использовать pipeline для mask (вторая функция — не шаг
   пайплайна).
2. Расширить scaffold (IProcessor как detect). Отвергнуто: пайплайн
   не подходит для двух независимых чистых функций.

## Последствия

- (+) `beta` содержит ровно то, что нужно: `IDetector` (и в следующей
  iota — `IMasker`).
- (+) `alpha` — только типы, без `IEvent`, который нигде не нужен.
- (−) `beta` ScrubLar не похож на `beta` BaseLar. Норма по ADR-0008
  BaseLar; зафиксировано здесь.
- (−) При обновлении шаблона (если) — scaffold не вернуть без ADR.

## Связь с предыдущими ADR

- ADR-0007 (контракт ядра) — `detect` и `mask` как чистые функции.
- ADR-0008 (Natasha) — NER-часть `IDetector`.
- ADR-0008 BaseLar — scaffold опционален, удаление через ADR.

## Статус

Принято (2026-10-24).
