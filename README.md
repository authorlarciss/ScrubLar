# BaseLar

Инвариантный шаблон греческих проектов экосистемы LAR.

## Назначение

BaseLar — пустой модульный каркас:

- греческая структура модулей (alpha, beta, gamma, delta, epsilon, zeta, iota, sigma, mu, psi);
- композиционный корень (psi) и метаданные (mu);
- конфигурация Python-проекта (pyproject, pre-commit, Makefile);
- базовый CI;
- документация по архитектуре и версионированию в `lambda/`.

BaseLar **не содержит бизнес-логики** — только структуру, контракты и
конфиги. Исключение — примеры инфраструктурных паттернов:
`PipelineWorkflow` в `beta/_internal/`, `BetaResolver`, `SigmaResolver`,
`LoggingSetup`. Их назначение — показать паттерн, а не реализовать
конкретную логику; в проекте они заменяются.

## Требования

- Python 3.13 (или 3.14 после готовности экосистемы)
- [uv](https://github.com/astral-sh/uv) — настоятельно рекомендуется
- git, make

## Быстрый старт

```bash
# Установить зависимости (uv — рекомендуется)
make install

# Или, если uv не установлен
make install-pip

# Проверить
make test
make run
```

## Использование шаблона

1. На GitHub — «Use this template» → «Create a new repository».
2. Клонировать локально:
   ```bash
   cd ~/projects/Greek/<category>
   git clone git@github.com:<user>/<ProjectName>.git
   cd <ProjectName>
   ```
3. Настроить окружение:
   ```bash
   make install
   ```
4. Создать ветку `omicron` для разработки до первого релиза:
   ```bash
   git checkout -b omicron
   git push -u origin omicron
   ```
 5. Обновить идентичность:
    - `nu/mu/public/__init__.py`: `__version__ = "0.0.0"`
    - `pyproject.toml`: `name`, `description`
    - `README.md`
    - `CHANGELOG.md`
    - `lambda/PLAN.md`
6. Первая ADR: `lambda/adr/0001-...md`
7. Первый коммит в `omicron`:
   ```bash
   git add .
   git commit -m "chore: initialize <ProjectName> from BaseLar template"
   git push
   ```

## Структура

- `nu/` — код (аналог `src/`).
  - `alpha/` — фундаментальные типы (алфавит).
  - `beta/` — бизнес-логика (процессоры, workflow).
  - `gamma/` — представление (UI, CLI).
  - `delta/` — адаптеры.
  - `epsilon/` — независимые сервисы.
  - `zeta/` — эксперименты и легаси.
  - `iota/` — утилиты.
  - `sigma/` — логирование.
  - `mu/` — метаданные (версия).
  - `psi/` — композиционный корень (contracts, bootstrap, Application).
  - Каждый модуль: `public/` (API) + `_internal/` (реализация).
- `tau/` — тесты.
- `lambda/` — документация (ADR, архитектура, версионирование).
- `omega/` — сборка и релиз.

Полное описание — в `lambda/ARCHITECTURE.md`.

## Версионирование

Модель ветвления и правила релизов — в `lambda/VERSIONING.md`.

## Асинхронность и логирование

Все интерфейсы — async (`asyncio.run` в `main.py`). Логирование
централизовано через `sigma`: `get_logger(__name__)` в каждом модуле,
настройка в `psi/bootstrap` первой. Контекст (`request_id`, `user_id`)
— через `ContextVar`, автоматически добавляется в записи.

Подробности — в `lambda/CONTRIBUTING.md`.

## Документация

- `lambda/ARCHITECTURE.md` — архитектура
- `lambda/VERSIONING.md` — Hellenic Git Flow
- `lambda/PLAN.md` — план проекта (заполняется в конкретном проекте)
- `lambda/CONTRIBUTING.md` — правила разработки
- `lambda/adr/` — Architecture Decision Records
- `CHANGELOG.md` — история версий (Keep a Changelog 1.1.0). При
  клонировании шаблона — заменить с чистого листа, первую запись
  начать с `## [0.1.0]`.

## Окружение

**Рекомендуется uv:**

```bash
make install
```

**Fallback через venv+pip:**

```bash
make install-pip
```

**PyCharm / Zed:** открыть корень проекта как папку, указать `.venv/bin/python` как интерпретатор.

## Лицензия

Внутренний проект экосистемы LAR.
