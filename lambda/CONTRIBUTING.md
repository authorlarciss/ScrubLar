# Правила разработки

## Ветки

См. `VERSIONING.md`.

## Коммиты

Conventional Commits:

- `feat:` — новая функциональность
- `fix:` — исправление
- `refactor:` — рефакторинг
- `docs:` — документация
- `test:` — тесты
- `chore:` — рутина

## Перед коммитом

```bash
make format
make lint
make lint-imports
make test
make check
```

`make check` прогоняет `ruff format --check`, `ruff check`,
`lint-imports` и `pytest`. `make format` перед этим — автофикс
(`ruff format` + `ruff check --fix`). Pre-commit hooks сделают часть
автоматически.

## Changelog

`CHANGELOG.md` в корне — единственный источник истории версий.
Формат: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
версии — [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html).

**Когда обновлять:**

- При каждом релизе — в том же коммите, что и bump версии.
- При добавлении/изменении/удалении публичного API — в раздел
  `## [Unreleased]`.
- При исправлении поведения, видимого пользователю, — в
  `## [Unreleased]`.
- При внутренних рефакторингах без изменения поведения — не нужно.

**Категории (в этом порядке):**

`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

**При релизе:**

1. Переместить содержимое `## [Unreleased]` в новый раздел
   `## [X.Y.Z] - YYYY-MM-DD`.
2. Оставить `## [Unreleased]` пустым.
3. Обновить ссылки в конце файла (если используются).
4. Коммит `chore: bump version to X.Y.Z` — атомарно версия +
   changelog.

**На новом проекте из BaseLar:** заменить `CHANGELOG.md` с чистого
листа. Сохранить формат, первую запись начать с `## [0.1.0]`.
Историю BaseLar удалить.

### Нумерация ADR

Номера ADR — **сквозные по экосистеме**, не per-project. BaseLar
занимает 0001–0005 (0001 заменён 0002). Каждый новый проект
продолжает с максимального существующего номера + 1.

Пример:
- BaseLar: 0001–0005
- TirLar: 0006–0007
- IdleLar: с 0006

В новом проекте **не начинать с 0001**. При принятии проектного
решения ссылаться на экосистемный ADR, если оно его продолжает
или отклоняет.

## Работа с контрактами

**Правило:** между модулями — только через `psi.contracts`.

**Внутри модуля** — прямые импорты:

    # nu/beta/_internal/compiler.py
    from nu.beta.public.interfaces import ICompiler

**Из другого модуля** — через `psi.contracts`:

    # nu/delta/_internal/svg_renderer.py
    from nu.psi.contracts.alpha import Point
    from nu.psi.contracts.beta import ICompiler

**Проверка перед коммитом:**

    make lint-imports

Если правило нарушено — `import-linter` покажет, какой модуль и что
импортирует. Это реальное нарушение архитектуры, а не ложная тревога.

**Когда добавляешь публичное имя в модуль:**

1. Помести реализацию в `nu/<module>/_internal/`.
2. Объяви публичный интерфейс/тип в `nu/<module>/public/`.
3. Реэкспортируй через `nu/<module>/public/__init__.py` (explicit re-export).
4. Реэкспортируй через `nu/psi/contracts/<module>.py`.
5. Используй из других модулей через `nu.psi.contracts.<module>`.

**Исключение для `psi`:** композиционный корень может импортировать
модули напрямую (для сборки в `bootstrap`), но не имеет права трогать
их `_internal/` (кроме цепочки через `public/resolver.py`).

## Explicit re-export

Паттерн для `public/__init__.py` и `psi/contracts/<module>.py`:

    from nu.beta.public.interfaces import ICompiler as ICompiler
    from nu.beta.public.interfaces import IExecutor as IExecutor

    __all__ = ["ICompiler", "IExecutor"]

**Почему `as`:**

- Без `as` — ruff считает импорт неиспользуемым (`F401`), если имени
  нет в `__all__`, или mypy не понимает, что реэкспорт намеренный.
- `TypeAlias` — ruff требует PEP 695 (`UP040`).
- `type X = Y` — создаёт `TypeAliasType`, невызываемый объект.
  Для классов и функций не подходит.

`from X import Y as Y` — единственный паттерн, который работает
с ruff, mypy, pyright и не ломает вызовы.

`per-file-ignores` для `F401` в `__init__.py` **удалён**. Это
осознанно: explicit re-export (`from X import Y as Y`) проходит
без него, а если где-то забыт `as` — CI это поймает. Для
агрегата в `psi/contracts/__init__.py` — используйте
`from . import alpha as alpha`.

## Resolver pattern

Каждый модуль может предоставить **публичный резолвер** — фабрику
для создания своих исполнителей. Резолвер используется в `psi.bootstrap`,
чтобы не импортировать `_internal/` напрямую.

**Factory (публичный, в `public/resolver.py`):**

    class BetaResolver:
        def __init__(self, config: BetaConfig | None = None) -> None:
            self._config = config or BetaConfig()

        def make_compiler(self) -> ICompiler:
            # noinspection PyProtectedMember
            from nu.beta._internal.compiler import Compiler
            return Compiler(max_instructions=self._config.max_instructions)

        def make_workflow(self, initial_data: Any = None) -> IWorkflow:
            # noinspection PyProtectedMember
            from nu.beta._internal.workflow import PipelineWorkflow
            return PipelineWorkflow(initial_data=initial_data)

**Normalizer (приватный, в `_internal/normalizers.py`):**

Приводит partial-параметры от других модулей к полным:

    def normalize_run_request(partial: RunRequest) -> FullRunRequest:
        return FullRunRequest(
            program=partial.program,
            step_limit=partial.step_limit if partial.step_limit is not None
                       else DEFAULT_STEP_LIMIT,
        )

**Правило:** `psi.bootstrap` **никогда** не импортирует из `_internal/`
напрямую. Только через `public/resolver.py`.

### Lazy import в resolver: тест на каждую фабрику

Resolver-методы импортируют `_internal/` **внутри** метода, а не на
уровне модуля:

    def make_compiler(self) -> ICompiler:
        # noinspection PyProtectedMember
        from nu.beta._internal.compiler import Compiler
        return Compiler(...)

Это правильно: модуль `_internal` не загружается, пока фабрика не
вызвана. Но у этого есть побочный эффект — **покрытие**.

Если ни один тест не вызывает `make_compiler`, строка `from ... import`
не исполняется, файл `_internal/compiler.py` не загружается, coverage
показывает 0% на нём. Это не баг, но ложный сигнал: код есть, он
работает, но не проверен.

**Правило:** каждый фабричный метод resolver'а тестируется отдельным
тестом. Тест:

1. Вызывает фабрику.
2. Проверяет `isinstance(result, IInterface)` — что вернулся
   ожидаемый интерфейс, не реализация.
3. Форсирует импорт `_internal/` (побочный эффект вызова).
4. Покрывает строку lazy import.

Пример (TirLar, `tau/unit/test_gamma_resolver.py`):

    def test_make_text_io_returns_itextio() -> None:
        resolver = GammaResolver()
        io = resolver.make_text_io()
        assert isinstance(io, ITextIO)

**Не покрывать фабрику через другие тесты.** Если `make_engine`
используется в `test_engine.py`, это не считается покрытием
`make_engine` — `test_engine.py` тестирует движок, не фабрику.
Фабрика — отдельная точка входа, отдельный тест.

**Исключение:** фабрика, которая сама по себе тривиальна
(`return SomeImpl()` без параметров) и вызывается в каждом тесте
модуля. Тогда отдельный тест не нужен — но и `resolver`-метод
не должен содержать логики, только создание.

## Выбор паттерна взаимодействия

От простого к сложному:

1. **Direct call через contract.** Если A вызывает B и знает его —
   вызывайте напрямую. Быстрее, type-safe, traceable.

2. **Workflow (`IProcessor` + `IWorkflow`).** Если есть
   последовательность шагов с трансформацией данных. Один обработчик
   на шаг, порядок известен.

3. **Event bus (`IEvent` + `IEventBus`).** Только если:
   - у события несколько обработчиков, **И**
   - обработчики могут меняться в рантайме.

**Правило:** «Если можете вызвать функцию напрямую — вызывайте.
Event bus — только когда без него нельзя».

## Beta-слой: scaffold и отклонения

`beta/` поставляет scaffold для pipeline-задач: `IProcessor`,
`IWorkflow`, `PipelineWorkflow`, `IEventBus`, `IEvent` (в `alpha/`).

**Это примеры, не догма.** Если домен проекта — не pipeline
(машина состояний, тиковый движок, event-sourced система), scaffold
можно заменить своим паттерном или удалить. См. ADR-0006.

**Правила при отклонении:**

1. Удаление/замена фиксируется ADR. Пример: TirLar ADR-0007 —
   удалены `IProcessor`/`IWorkflow`/`IEventBus`/`IEvent`, движок
   стал машиной состояний.
2. Архитектурные границы ADR-0002 сохраняются: `public/` + `_internal/`,
   resolver, связь через `psi.contracts`. Меняется содержимое `beta/`,
   не правила.
3. `psi.bootstrap` собирает то, что есть. Если scaffold удалён —
   `build_application()` переписывается под домен, шаблонные тесты
   `test_bootstrap_*` обновляются или удаляются (они помечены
   `pytest.mark.template`).

**Что остаётся обязательным:** `alpha/` как алфавит типов, `delta/`
как адаптеры, `gamma/` как представление, `sigma/` как логирование,
`psi/` как композиционный корень. Опционален только **контент**
`beta/`, не сама роль модуля.

## Async в интерфейсах

Все интерфейсы — `async def`, даже если реализация синхронная:

    class MyProcessor(IProcessor):
        async def process(self, data: Any) -> Any:
            return data + 1  # sync внутри, async снаружи

**Точка входа** — `main.py`:

    def main() -> None:
        app = build_application()
        asyncio.run(app.run())

`asyncio.run` — на границе. Внутри — async, но синхронная реализация
просто не содержит `await`.

## Логирование

**Каждый модуль** использует `get_logger(__name__)`:

    from nu.psi.contracts.sigma import get_logger
    logger = get_logger(__name__)

    logger.info("Compiling program")
    logger.warning("Step limit reached", extra={"case_id": case.id})

**Правила:**

- **Не `print`.** Только `logger`.
- **`get_logger(__name__)`** на уровне модуля — безопасно, даже если
  настройка ещё не выполнена (дефолтное поведение `logging`).
- **Context** (`request_id`, `user_id`) — устанавливается
  middleware или bootstrap. Filter добавит автоматически.
- **Формат:** `text` для разработки, `json` для production.

**Настройка** — в `psi/bootstrap` **первой**, до всех модулей:

    def build_application() -> Application:
        context = Context()

        sigma_resolver = SigmaResolver()
        sigma_resolver.setup_logging(LoggingConfig(level="INFO", format="text"))
        context.register("sigma_resolver", sigma_resolver)

        # ... остальные модули
        return Application(context)

**Context в async-коде:**

    from nu.psi.contracts.sigma import set_request_id, set_user_id, clear_context

    # в middleware или bootstrap
    set_user_id(update.from_user.id)
    set_request_id(str(uuid.uuid4()))

    try:
        await handle(update)
    finally:
        clear_context()

## Zeta — правила использования

Zeta — модуль для экспериментов и легаси.

### `zeta/public/` — легаси

- **Можно** ссылаться через `psi.contracts.zeta` для отладки.
- **Нестабильный API.** Может измениться или исчезнуть.
- **Временное пристанище.** При рефакторинге — переносите в `beta`,
  `delta` или `epsilon`, либо удаляйте.

### `zeta/_internal/` — эксперименты

- **Никогда** не импортируется другими модулями (включая psi).
- Прототипы, spike, код «в разработке».
- Может сломаться в любой момент.

### Правило

`psi/contracts/zeta.py` реэкспортирует **только** из `zeta.public`.
Никогда из `_internal`. Проверяется на code review.

## Тестирование frozen dataclass

**Правильно:**

    def test_frozen():
        a = Action()
        with pytest.raises(FrozenInstanceError):
            setattr(a, "write", Symbol("1"))  # noqa: B010

**Неправильно:**

    def test_frozen():
        a = Action()
        with pytest.raises(FrozenInstanceError):
            a.write = Symbol("1")  # PyCharm ругается, ruff B010

`setattr` + `# noqa: B010` — единственный способ, который не ломает
ни PyCharm, ни ruff, ни mypy.

## Тестирование async

В проекте `pytest-asyncio` с `asyncio_mode = "auto"`. Тесты на async
пишутся без декораторов:

    async def test_workflow():
        workflow = BetaResolver().make_workflow(initial_data=5)
        await workflow.run([AddOne()])
        assert workflow.get_result() == 6

**Не нужно:** `@pytest.mark.asyncio`, `asyncio.run(...)`.

## Окружение

### Рекомендуется uv

```bash
make install       # uv sync --extra dev
```

`uv` в 10-100 раз быстрее `pip`. Для новых проектов — настоятельно
рекомендуется.

### Fallback: venv + pip

```bash
make install-pip   # python -m venv + pip install -e ".[dev]"
```

Если `uv` не установлен — этот вариант работает так же.

### PyCharm / Zed

Открыть корень проекта как папку, указать `.venv/bin/python` как
интерпретатор.

### Локальный CI
`make ci` — то же, что `make check`. Запускайте перед PR.

## Python 3.13

Проект пинит Python 3.13. Причины:

- Экосистема библиотек (PyCharm, C-расширения, LSP-плагины) готова к 3.13.
- 3.14 вышла, но не все зависимости её поддерживают.
- `ruff` / `black` target — `py313`.

`requires-python = ">=3.13,<3.15"` — диапазон. Обновление до 3.14 —
когда экосистема догонит.

## Mypy

`mypy` в strict-режиме. Конфигурация — `[tool.mypy]` в `pyproject.toml`.
Проверка: `make typecheck` или `make check`.

**Нетипизированные библиотеки** — точечно, через
`[[tool.mypy.overrides]]`:

    [[tool.mypy.overrides]]
    module = ["transformers.*", "torch.*"]
    ignore_missing_imports = true
    follow_imports = "skip"

**Pydantic (downstream-проекты):**

    [tool.mypy]
    plugins = ["pydantic.mypy"]

    [tool.pydantic-mypy]
    init_forbid_extra = true
    init_typed = true
    warn_required_dynamic_aliases = true

**Pre-commit:** `mirrors-mypy` с версией, синхронизированной с
`.venv/bin/mypy --version`. `additional_dependencies` пустой —
полная проверка в `make check` и CI.

**Правило:** `# type: ignore` — только с кодом ошибки
(`# type: ignore[import-untyped]`), не голый. `warn_unused_ignores = true`
ловит устаревшие ignore.

**Расширение `LogRecord`.** `sigma` присваивает `record.request_id` и
`record.user_id` — typeshed принимает это, но типизирует как `Any`
при чтении. Если в downstream-проекте эти поля читаются в типизированном
коде — определить Protocol:

    from typing import Protocol

    class ExtendedLogRecord(Protocol):
        request_id: str | None
        user_id: int | str | None

И приводить `record` к нему на границе чтения.
