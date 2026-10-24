# Архитектура проекта

## Модули

Проект состоит из независимых модулей. Каждый модуль — самодостаточная
единица с собственным функционалом, публичным API и приватной
реализацией. Иерархии зависимостей между модулями **нет**.

| Модуль | Роль |
|--------|------|
| `alpha` | Фундаментальные типы (алфавит проекта) |
| `beta` | Бизнес-логика: процессоры, workflow, event bus |
| `gamma` | Внешнее представление: UI, CLI, API |
| `delta` | Адаптеры: реализации интерфейсов Beta |
| `epsilon` | Независимые стабильные сервисы |
| `zeta` | Эксперименты и легаси. См. раздел «Zeta — особый модуль» |
| `iota` | Утилиты |
| `sigma` | Логи и метрики |
| `mu` | Метаданные проекта (версия) |
| `psi` | Композиционный корень: контракты, bootstrap, Application |

Корневые директории вне `nu/`:

| Директория | Назначение |
|------------|------------|
| `tau` | Тесты (импортируют `nu` как пакет) |
| `lambda` | Документация: архитектура, ADR, версионирование |
| `omega` | Сборка и релиз: Docker, скрипты |

## Структура модуля

    nu/<module>/
    ├── __init__.py         # docstring-указатель на public/
    ├── public/             # публичный API модуля
    │   ├── __init__.py     # explicit re-exports
    │   ├── interfaces.py   # интерфейсы исполнителей (если есть)
    │   ├── types.py        # публичные типы (если есть)
    │   └── resolver.py     # публичный резолвер (если есть)
    └── _internal/          # приватная реализация
        ├── __init__.py
        └── <реализации>

`_internal/` не упоминается в `public/__init__.py`, поэтому недоступен
извне. Единственное исключение — `public/resolver.py`, которому
разрешён доступ к `_internal/` (см. Resolver pattern).

## Публичное и приватное в каждом модуле

Каждый модуль следует единому правилу:

- Всё, что реэкспортируется через `public/__init__.py`, считается
  публичным API модуля.
- Приватная реализация живёт в `_internal/` и не импортируется из
  других модулей.
- `psi/contracts/<module>.py` реэкспортирует публичный API модуля.

**Исключения:** `zeta` и `psi` — см. разделы ниже.

## Zeta — особый модуль

Zeta — для экспериментов и легаси. Следует стандартному паттерну
`public/` + `_internal/`, но с особой семантикой:

| Папка | Что содержит | Импортируемо? |
|---|---|---|
| `zeta/public/` | Легаси, на которое можно ссылаться для отладки | ✅ через `psi.contracts.zeta` |
| `zeta/_internal/` | Строго экспериментальное, прототипы | ❌ никогда |

**Смысл:**

- `zeta/public` — «старый код, который работает, но не развивается».
  Другие модули могут **временно** использовать его для отладки.
- `zeta/_internal` — «в разработке, может сломаться в любой момент».
  Никто не должен на это ссылаться.

**Правило:** `psi/contracts/zeta.py` реэкспортирует **только** из
`zeta.public`. Никогда из `_internal`.

**При рефакторинге** — код из `zeta.public` переносится в `beta`,
`delta` или `epsilon`, либо удаляется. Zeta — временное пристанище.

## Psi — композиционный корень

Psi **не следует** паттерну `public/` + `_internal/`. Причина:
`public/` и `_internal/` — это **две половины одной границы**.
Если нет `_internal/`, нет смысла и в `public/`.

Psi структурирован по ролям:

- `psi/contracts/` — публичный API для всех модулей.
- `psi/bootstrap/` — сборка приложения (публично для `main.py`).
- `psi/application.py` — базовый `Application` (публично для `main.py`).
- `psi/context.py` — DI-контейнер (публично для `main.py`).
- `psi/interfaces.py` — `IApplication` (интерфейс, отдельно от реализации).

**Правило:** psi остаётся плоским. Если в `bootstrap/` появляются
приватные helper'ы — они помечаются `_prefix` (функции) или кладутся
в файлы с `_prefix` внутри `bootstrap/`.

## Контракты

**Публичный API модуля** (`nu/<module>/public/__init__.py`) —
explicit re-export публичных имён:

    # nu/alpha/public/__init__.py
    from nu.alpha.public.events import IEvent as IEvent

    __all__ = ["IEvent"]

**Единый контракт** (`nu/psi/contracts/<module>.py`) — реэкспорт
из `nu/<module>/public/`. Единственная точка, откуда модули берут
имена друг друга.

**Использование контрактов — только для типов и вызовов:**

    from nu.psi.contracts.alpha import IEvent
    from nu.psi.contracts.beta import ICompiler

    def render(e: IEvent, c: ICompiler) -> None:
        ...

**Инициализация через контракты запрещена.** Контракт описывает
типы и публичные функции, не создаёт объекты. Инициализация — только
через `psi.bootstrap` (см. Resolver pattern).

Проверяется `import-linter` (см. `[tool.importlinter]` в `pyproject.toml`).

Шесть контрактов:

1. Только `psi` — к `psi.bootstrap/application/context`.
2. Модули независимы друг от друга; связи — через `psi.contracts`.
3. `psi` и `main` не импортируют `_internal` напрямую (кроме resolver).
4. `zeta._internal` не импортируется никем.
5. `public` не импортирует `_internal` (кроме `public/resolver.py`).
6. `main.py` импортирует только из `nu.psi`.

`unmatched_ignore_imports_alerting = "error"` — мёртвое правило валит CI.

Проверяется `import-linter` (см. `[tool.importlinter]` в `pyproject.toml`).

## Resolver pattern

`public/resolver.py` — единственное место в модуле, которому разрешён
доступ к `_internal/` из `public/`. Это делает `psi.bootstrap`
зависимым от `public/resolver.py`, а не от `_internal/` напрямую:

    psi.bootstrap → nu.X.public → nu.X.public.resolver → nu.X._internal.*

Import-linter разворачивает цепочку и формально видит «psi
импортирует _internal». Это **разрешённое исключение** — оно
прописано в `ignore_imports` правила 3 для всех стандартных модулей.

**Zeta — исключение.** Её `_internal/` не импортируется никем
(правило 4). Даже через resolver.

**Factory** (публичный, `public/resolver.py`) — создаёт исполнителей
из статических параметров. Используется `psi.bootstrap`.

**Normalizer** (приватный, `_internal/normalizers.py`) — приводит
partial-параметры от других модулей к полным.

## Асинхронные интерфейсы

Все интерфейсы в BaseLar — `async def`, чтобы не переписывать при
появлении async-шагов. Синхронная реализация просто не содержит
`await` внутри.

Стандартные интерфейсы:

| Интерфейс | Модуль | Назначение |
|---|---|---|
| `IApplication` | `psi/interfaces.py` | Точка входа проекта, `async def run()` |
| `IProcessor` | `beta/public/interfaces.py` | Один шаг обработки, `async def process(data)` |
| `IWorkflow` | `beta/public/interfaces.py` | Оркестратор процессоров, `async def run(stages)` |
| `IEventBus` | `beta/public/interfaces.py` | Асинхронная шина событий |
| `IEvent` | `alpha/public/events.py` | Маркер события (DTO) |

**`IEvent`** — marker class. Инстанцировать напрямую нельзя
(`__new__`-guard). Конкретные события наследуют `IEvent` и являются
`frozen dataclass`. Событие — DTO, не мутирует после создания.

**`IEventBus`** — только интерфейс. Реализация — в проектах, где
реально нужна (например, async bot). В BaseLar core не реализована.

**`IWorkflow`** — единый обработчик для проектов со статическими
взаимодействиями. `PipelineWorkflow` в `beta/_internal/workflow.py` —
пример реализации (fail-fast, sequential). Проекты могут писать свои.

См. CONTRIBUTING → «Выбор паттерна взаимодействия»: direct call →
workflow → event bus.

## Sigma — логирование

Sigma предоставляет централизованное логирование.

**Публичный API** (`sigma/public/`):

- `get_logger(name)` — получить логгер. Все логгеры проекта под
  префиксом `nu.`. Работает **до** настройки (дефолтное поведение
  `logging`), но настройка нужна для единого формата.
- `set_request_id(id)`, `set_user_id(id)`, `clear_context()` —
  контекстные поля (ContextVar, изолированы между asyncio-задачами).
- `LoggingConfig` — frozen dataclass: `level`, `format` (`text`/`json`),
  `include_context`, `stream` (`stdout`/`stderr`).
- `SigmaResolver.setup_logging(config)` — настройка корневого логгера
  `nu`. Идемпотентна.

**Реализация** (`sigma/_internal/`):

- `LoggingSetup` — конфигурирует root logger `nu` (`propagate=False`).
- `ContextFilter` — добавляет `request_id` / `user_id` в `LogRecord`.
- `TextFormatter` / `JsonFormatter` — форматы для dev / prod.

**Инициализация** — в `psi/bootstrap` **первой**, до всех остальных
модулей. Ранние логи не теряются.

**Использование в модулях:**

    from nu.psi.contracts.sigma import get_logger
    logger = get_logger(__name__)

    logger.info("Compiling program", extra={"instructions": 42})

**Context:** в async-коде middleware (или bootstrap) ставит
`set_user_id` / `set_request_id`, filter автоматически добавляет их
к каждой записи. `clear_context()` — после завершения задачи.

## Путь созревания кода

    zeta/_internal/  →  zeta/public/  →  epsilon/  →  beta/ или delta/
    (эксперимент)      (легаси для       (стабильный   (часть ядра)
                        отладки)          сервис)

- Код из `zeta/_internal/` не импортируется никем.
- Код из `zeta/public/` импортируем через `psi.contracts.zeta`,
  но считается временным.
