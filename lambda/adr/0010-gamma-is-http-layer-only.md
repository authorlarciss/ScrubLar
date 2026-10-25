# ADR-0010: Gamma — только HTTP-слой

## Контекст

`gamma` — представление (HTTP). В черновике ScrubService жил в
`gamma/_internal/`, собирая `DeltaResolver`, `IDetector`, `IMasker`.
Это нарушает роль `gamma`: представление не должно знать о бизнес-
модулях и их резолверах. TirLar (образец) делает иначе: `gamma`
определяет `ITextIO`, `ICommandParser`, `IResponseFormatter`; оркестрация
живёт в `psi` (`TirLarApplication`).

## Решение

**Gamma** содержит:
- `gamma/public/interfaces.py` — `IScrubService`, `ScrubResult`.
- `gamma/_internal/api.py` — `make_app(scrub_service)`.
- `gamma/_internal/templates.py` — HTML.
- `gamma/public/resolver.py` — `make_app(scrub_service)`.

**Psi** содержит:
- `psi/scrub_service.py` — `ScrubService(IScrubService)`, оркестрация
  parse → detect → mask. Импортирует `DeltaResolver`, `IDetector`,
  `IMasker` из contracts.
- `psi/bootstrap/__init__.py` — собирает `ScrubService`, регистрирует
  `gamma_resolver`, `scrub_service`, возвращает `ScrubLarApplication`.
- `psi/application.py` — `ScrubLarApplication`: `gamma_resolver.make_app(
  scrub_service)`, `uvicorn.Server.serve()`.

Gamma не импортирует `delta`, `beta`, `epsilon` — только `alpha` (типы).
`psi` — композиционный корень, ему можно всё.

## Альтернативы

1. ScrubService в `gamma`. Отвергнуто: `gamma` знал бы про `DeltaResolver`,
   `IDetector`, `IMasker`. Нарушает role of representation.
2. ScrubService в `beta` (бизнес-логика). Отвергнуто: `beta` — детектор
   и маскер как чистые функции (ADR-0007). Парсинг и I/O — не его дело.
   `beta` не должен знать про `DeltaResolver`.

## Последствия

- (+) `gamma` — 3 файла: интерфейс, шаблон, HTTP-хендлер. Никакой сборки.
- (+) `ScrubService` тестируется отдельно от HTTP (`test_psi_scrub_service`).
- (+) По образцу TirLar: `gamma` даёт то, что представлению нужно,
  `psi` реализует.
- (−) `psi` не «плоский» в смысле ARCHITECTURE.md BaseLar: добавлен
  `scrub_service.py` рядом с `application.py`. Допустимо: `psi` — не
  паттерн `public/_internal`, а набор файлов по ролям.

## Связь с предыдущими ADR

- ADR-0007 (контракт ядра): `detect`/`mask` — чистые функции.
- ADR-0009 (scaffold в beta/alpha).
- ADR-0008 BaseLar (scaffold — опционален).

## Статус

Принято (2026-10-25).
