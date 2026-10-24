# ADR-0004: Полнота import-linter

## Контекст

ADR-0002 ввёл границу `public/` ↔ `_internal/` и resolver pattern.
`pyproject.toml` в BaseLar v0.2.0 содержит 4 контракта import-linter:

1. Только `psi` — к `psi.bootstrap/application/context`.
2. Модули независимы друг от друга.
3. `psi` не импортирует `_internal` напрямую (кроме resolver).
4. `zeta._internal` не импортируется никем.

При аудите выявлены дыры:

1. **`public → _internal` не проверяется.** ADR-0002 заявляет: «`public/`
   → `_internal/` — запрещено (кроме `public/resolver.py`)». Ни одно из
   четырёх правил это не проверяет. Граница держится только на code review.
2. **`nu/main.py` не покрыт.** `main.py` — тонкий лаунчер, должен
   импортировать только `psi` entry points. Фактически может импортировать
   любой модуль напрямую, включая `_internal`, и import-linter промолчит.
3. **`unmatched_ignore_imports_alerting = "none"`** скрывает мёртвые
   правила. В правиле 3 перечислены resolver-цепочки для модулей, у
   которых resolver ещё нет (`alpha`, `gamma`, `delta`, `epsilon`, `iota`,
   `mu`). При рефакторинге правило тихо перестанет работать.

## Решение

Довести import-linter до полноты, заявленной в ADR-0002.

### Правило 5 — `public` не импортирует `_internal`

```toml
[[tool.importlinter.contracts]]
name = "Public does not import _internal except via resolver"
type = "forbidden"
source_modules = [<все>.public]
forbidden_modules = [<все>._internal]
ignore_imports = [<resolver-цепочки существующих модулей>]
unmatched_ignore_imports_alerting = "error"
```

### Правило 6 — `main.py` импортирует только из `psi`

```toml
[[tool.importlinter.contracts]]
name = "main.py imports only from nu.psi"
type = "forbidden"
source_modules = ["nu.main"]
forbidden_modules = [<все модули, кроме psi>]
```

**Уточнение.** Правило 6 проверяет **прямые** импорты в `main.py`.
Транзитивные цепочки (`main → psi.bootstrap → psi.contracts.beta →
beta.public`) — не нарушения: `main` делегирует сборку `psi.bootstrap`,
и что `bootstrap` использует внутри — ответственность `psi`, а не
`main`. Для этого в контракте стоит `allow_indirect_imports = true`.
Иначе `forbidden` по умолчанию ловит всю цепочку и правило 6
превращается в дубликат правила 2 «Модули независимы», только с
другой стороны.

### Расширение правил 3 и 4

Добавить `nu.main` в `source_modules` правил 3 и 4 — `main.py` тоже не
должен импортировать `_internal` или `zeta._internal`.

### Ужесточение alerting

`unmatched_ignore_imports_alerting = "none"` → `"error"` во всех правилах,
где есть `ignore_imports`. Мёртвое правило — ошибка CI, а не тишина.

### Чистка ignore_imports правила 3

Удалить несуществующие resolver-цепочки (`alpha`, `gamma`, `delta`,
`epsilon`, `iota`, `mu`). Оставить только реальные — `beta`, `sigma`.
При добавлении resolver в другой модуль — добавить явно в правила 3 и 5.

## Альтернативы

1. **Оставить как есть, компенсировать code review.** Отвергнуто:
   архитектура, которая держится на дисциплине, а не на автоматике,
   деградирует. Для шаблона, клонируемого в десятки проектов, — недопустимо.
2. **Использовать wildcard `nu.*.public` / `nu.*._internal`.** Частично
   работает, но `ignore_imports` всё равно требует явных записей на модуль.
   Явное перечисление модулей — заодно ловит добавление нового модуля без
   обновления конфига.
3. **`"warn"` вместо `"error"`.** Отвергнуто: предупреждения игнорируются.
   В шаблоне — только `error`.

## Последствия

- (+) Границы ADR-0002 полностью покрыты автоматикой.
- (+) `main.py` под контролем.
- (+) Мёртвые правила ловятся CI.
- (−) При добавлении модуля — нужно обновить конфиг в 5–6 местах. Это
  осознанно: явный конфиг ловит добавления.
- (−) Если downstream-проект имеет нарушения — при обновлении шаблона
  CI упадёт. Это правильно: нарушения были и раньше, просто не ловились.

## Связь с предыдущими ADR

Реализует enforcement ADR-0002 в полном объёме. Новых архитектурных
решений не вводит.

## Статус

Принято (2026-10-21).
