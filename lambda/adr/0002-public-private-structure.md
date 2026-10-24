# ADR-0002: Публичная и приватная структура модулей

## Контекст

ADR-0001 ввёл модель: модули независимы, каждый имеет `contract.py`
с namespace-классом `ModuleContract`, реэкспортируемым через
`psi/contracts/<module>.py`.

При реализации (Phase 2) выяснилось:

1. **Namespace-классы дублируют `public/__init__.py`.** `ModuleContract`
   не используется — `psi/contracts` реэкспортирует имена напрямую
   из исходных файлов, минуя namespace-класс.

2. **`TypeAlias` не проходит ruff** (`UP040` — требует PEP 695).

3. **`type X = Y` создаёт `TypeAliasType`** — невызываемый объект.
   Для классов и функций не подходит.

4. **Плоская структура модулей** (все файлы на одном уровне) смешивает
   публичное и приватное. Нет явной границы, import-linter не может
   её проверить.

5. **Интерфейсы не имеют места.** Если `IRenderer` в `alpha`, а
   `SvgRenderer` в `delta` — `alpha` начинает зависеть от конкретного
   провайдера. Нарушение модульности.

## Решение

Перейти на **публичную/приватную структуру** модулей.

### Структура модуля

    nu/<module>/
    ├── __init__.py         # docstring-указатель на public/
    ├── public/             # публичный API модуля
    │   ├── __init__.py     # explicit re-exports
    │   ├── interfaces.py   # интерфейсы (если есть)
    │   ├── types.py        # публичные типы (если есть)
    │   └── resolver.py     # публичный резолвер (если есть)
    └── _internal/          # приватная реализация
        ├── __init__.py
        ├── <реализации>
        └── normalizers.py  # приватные нормализаторы

### `contract.py` удаляется

Его функцию выполняет `public/__init__.py`. `psi/contracts/<module>.py`
реэкспортирует из `nu/<module>/public/`.

### Explicit re-export

Паттерн `from X import Y as Y`:

    from nu.beta.public.interfaces import ICompiler as ICompiler
    from nu.beta.public.interfaces import IExecutor as IExecutor

    __all__ = ["ICompiler", "IExecutor"]

`as Y` — явный маркер реэкспорта. Без него ruff считает импорт
неиспользуемым, mypy не понимает намерения. `TypeAlias` и
`type X = Y` отвергнуты (см. контекст).

### Интерфейсы — в модулях-провайдерах

Интерфейс живёт там, где его реализации:

- `IRenderer`, `IExporter` → `delta/public/interfaces.py`
- `ICompiler`, `IExecutor` → `beta/public/interfaces.py`
- `IProcessor`, `IWorkflow`, `IEventBus` → `beta/public/interfaces.py`
- `IApplication` → `psi/public/interfaces.py` (отдельно, если psi плоский — в `psi/`)
- `IEvent` → `alpha/events.py` (DTO, часть алфавита)
- `alpha` — только типы (алфавит), не интерфейсы исполнителей

### Resolver pattern

**Factory (публичный, в `public/resolver.py`)** — создаёт исполнителей
из статических параметров. Используется `psi.bootstrap`.

**Normalizer (приватный, в `_internal/normalizers.py`)** — приводит
partial-параметры от других модулей к полным.

`psi.bootstrap` никогда не импортирует `_internal/` напрямую — только
через `public/resolver.py`.

### Особые случаи

**Zeta:** следует стандартному паттерну, но с особой семантикой:

- `zeta/public/` — легаси для отладки (импортируемо через contracts,
  нестабильно).
- `zeta/_internal/` — строго экспериментальное (не импортируется никем).

**Psi:** **не следует** паттерну `public/` + `_internal/`. Причина:
это две половины одной границы. Если нет `_internal/`, нет смысла
в `public/`. Psi структурирован по ролям (`contracts/`, `bootstrap/`,
`application.py`, `context.py`), каждая уже явно публична.
Приватные helper'ы — с `_prefix` в файлах/функциях.

### Правила импорта

- Внутри модуля: `_internal/` → `public/` и `_internal/` напрямую.
- `public/` → `_internal/` — запрещено (кроме `public/resolver.py`).
- Из другого модуля: только `nu.psi.contracts.<module>`.
- `psi.bootstrap/application/context` — только для `psi` и `main.py`.

Проверяется `import-linter`.

## Альтернативы

1. **Оставить namespace-классы (ADR-0001)** — отвергнуто: дублирование,
   не используется, `TypeAlias` не работает.

2. **`type X = Y` вместо `from X import Y as Y`** — отвергнуто:
   `TypeAliasType` невызываемый.

3. **Плоская структура модулей** — отвергнуто: нет границы
   публичного/приватного, import-linter не может проверить.

4. **Все интерфейсы в `alpha`** — отвергнуто: `alpha` начинает
   зависеть от провайдеров, нарушение модульности.

## Последствия

- (+) Чёткая граница публичного/приватного в каждом модуле.
- (+) `import-linter` может проверять нарушения границ.
- (+) `psi.bootstrap` не знает о `_internal/` — только через резолверы.
- (+) Интерфейсы в провайдерах — правильное направление зависимостей.
- (+) Explicit re-export работает с ruff/mypy/pyright.
- (−) Требуется перенос существующего кода (Phase 2 миграция).
- (−) Больше файлов и папок в модулях.
- (−) Правило «интерфейс в провайдере» требует дисциплины.

## Связь с ADR-0001

Заменяет ADR-0001. Принципы модульной независимости и связи через
`psi.contracts` сохранены. Изменена только внутренняя структура
модулей и способ объявления публичного API.

## Статус

Принято (2026-10-20). Заменяет ADR-0001.
