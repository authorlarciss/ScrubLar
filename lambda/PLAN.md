# План проекта

> Шаблон. Заполняется в конкретном проекте.

## Цель

...

## Этапы

1. ...
2. ...
3. ...

## Критерий завершения MVP

...

## Первый релиз

Когда MVP достигнут:

1. `omicron` → `nu`.
2. Bump версии до `0.1.0` в `nu/mu/public/__init__.py`.
3. `alpha/v0.1.0` → `gamma/v0.1.0` → `omega` + тег `v0.1.0`.
4. `omicron`, `alpha/v0.1.0`, `gamma/v0.1.0` удаляются.
5. После релиза — работа через `iota/` от `nu`.

См. `VERSIONING.md` — раздел «omicron — первый шаг».

## Что в шаблоне BaseLar v0.3.2

Базовая инфраструктура, готовая к использованию:

- Модульная архитектура: `public/` + `_internal/`, explicit re-export.
- `psi/contracts/` — единая точка доступа к публичному API.
- Resolver pattern: `public/resolver.py` — единственная точка доступа
  к `_internal/` из `psi.bootstrap`.
- Async интерфейсы: `IApplication`, `IProcessor`, `IWorkflow`, `IEventBus`,
  `IEvent`. Синхронная реализация — просто без `await`.
- Логирование: `sigma` с `get_logger(__name__)`, ContextVar для
  `request_id` / `user_id`, форматы text/json.
- Тесты: `pytest` + `pytest-asyncio` (`asyncio_mode = auto`).
- CI: GitHub Actions через `uv`.
- `import-linter`: 4 контракта (psi-bootstrap, independence,
  psi-_internal via resolver, zeta-_internal never).
- `CHANGELOG.md` в корне — Keep a Changelog 1.1.0, история BaseLar.
  При клонировании — заменить с чистого листа.
