# ADR-0005: Mypy в strict-режиме

## Контекст

BaseLar v0.3.3 проверяет архитектурные границы (import-linter),
форматирование (ruff format) и линтинг (ruff check), но не проверяет
типы. Для downstream-проектов с бизнес-логикой (ScrubLar: детектор
PII, FastAPI-сервис) ошибки типов — реальный риск: несовместимость
`PIIEntity` и `MaskResult`, неверный тип в `DetectionReport`,
некорректная аннотация в route handler.

`mypy` — стандарт де-факто, интегрируется с pre-commit и CI,
поддерживает плагины для `pydantic`.

## Решение

Добавить `mypy` в `dev`-зависимости и `[tool.mypy]` с `strict = true`.
Включить `make typecheck` в `make check` и в CI. Pre-commit хук —
`mirrors-mypy` с версией, синхронизированной с `.venv`.

Для нетипизированных библиотек (`transformers`, `torch`, `datasets`,
`huggingface_hub`, `safetensors`) — точечные `[[tool.mypy.overrides]]`
с `ignore_missing_imports = true` и `follow_imports = "skip"`.
Глобальный `ignore_missing_imports` не используется: он скрыл бы
ошибки в типизированных пакетах (`fastapi`, `pydantic`).

`pydantic.mypy` плагин в шаблоне не включён (нет `pydantic`).
В downstream-проектах с `pydantic` — добавить `plugins = ["pydantic.mypy"]`
и `[tool.pydantic-mypy]` (см. CONTRIBUTING).

## Альтернативы

1. **`pyright` вместо `mypy`.** Отвергнуто: требует Node.js в CI,
   хуже работает с научными библиотеками, меньше плагинов.
2. **`ignore_missing_imports = true` глобально.** Отвергнуто: скрывает
   ошибки в типизированных пакетах.
3. **Не добавлять `mypy` в шаблон, только в downstream.** Отвергнуто:
   downstream-проекты будут настраивать `mypy` по-разному; шаблон
   задаёт единую планку.

## Последствия

- (+) Ошибки типов ловятся в CI и pre-commit.
- (+) `strict = true` для нового кода — планка с первого дня.
- (+) Точечные overrides для нетипизированных библиотек — не глобальное
  отключение.
- (+) `warn_unused_ignores = true` ловит устаревшие `# type: ignore`
  при обновлении typeshed или mypy — игноры не накапливаются.
- (−) `strict` может потребовать аннотаций в местах, где раньше было
  `Any`. В BaseLar это минимально; в downstream — по мере роста кода.
- (−) `mypy` в pre-commit не видит зависимости проекта без
  `additional_dependencies`. Полная проверка — в `make check` и CI.

## Связь с предыдущими ADR

Не затрагивает ADR-0002 (архитектура) и ADR-0003/0004 (тулинг).
Дополняет их: типы — ещё один слой автоматического контроля.

## Статус

Принято (2026-10-22).
