# ScrubLar v0.1.0 — отчёт о разработке

**Проект:** ScrubLar — локальный сервис обезличивания ПДн
**Основа:** BaseLar v0.5.0
**Версия:** v0.1.0 (2026-10-25)
**Репозиторий:** authorlarciss/ScrubLar

## 1. Резюме

Играбельный MVP: локальный веб-сервис, загружает DOCX/TXT, находит 6 типов ПДн (ФИО, телефон, email, СНИЛС, ИНН, паспорт), возвращает очищенный документ и отчёт. Работает локально, без внешних вызовов.

**Метрики (50 синтетических документов, seed=42):**

| Метрика | Значение |
|---|---|
| Tests | 217 passed |
| Покрытие | 100% branch |
| Контракты import-linter | 6/6 kept |
| mypy strict | 0 ошибок (98 файлов, nu + tau) |
| Overall recall | 1.00 |
| Overall precision | 0.93 |
| Structured PII (5 типов) | 1.00 / 1.00 |
| NAME (Natasha) | 1.00 / 0.86 |
| Runtime-зависимости | fastapi, uvicorn, python-docx, pymupdf (v0.2), natasha, pymorphy3 |
| Размер .venv | ~280 MB |

## 2. Архитектурные решения (ADR)

- **ADR-0007** (контракт ядра): две чистые функции `detect`/`mask`, детерминизм, иммутабельность, no I/O.
- **ADR-0008** (Natasha NER): бенчмарк 3 моделей — Natasha 0.966 F1 / 30 MB / 22 ms, spaCy 0.833 / 20 MB / 107 ms, GLiNER-small 0.800 / 200 MB / 665 ms. GLiNER-large (2.3 GB) отвергнут pre-benchmark. Natasha выбрана.
- **ADR-0009** (scaffold removal, IDetector): удалены IProcessor, IWorkflow, IEventBus, IEvent (pipeline не подходит для state machine — по образцу TirLar ADR-0007). `IDetector` как ядро beta.
- **ADR-0010** (gamma is HTTP only): ScrubService в psi (композиционный корень), gamma определяет IScrubService, реализуется в psi. По образцу TirLar: gamma — интерфейсы, psi — оркестрация.
- **ADR-0011** (evaluation methodology): clean + adversarial synthetic, overlap-based metrics.

## 3. Что сломалось и как чинили

### 3.1. Natasha: tar-архив пропал после uv sync

`NewsEmbedding()` не падал с ошибкой — молча возвращал пустые спаны, если tar `navec_news_v1_1B_250K_300d_100q.tar` отсутствует. `uv sync` пересоздал `.venv`, файл исчез. Первый `detect()` в тестах висел 66 секунд (скачивание 26 MB).

Решение: скопировать tar из `/tmp` в `.venv/lib/.../natasha/data/emb/`. Долгосрочно — зафиксировать в CONTRIBUTING: «Natasha требует tar в `.venv/.../natasha/data/emb/`; после `uv sync --reinstall` — перекопировать».

### 3.2. Зависание на `test_application_run`

`build_application()` возвращает `ScrubLarApplication`, чей `run()` — `uvicorn.Server.serve()`. Тест `await app.run()` висел 66 секунд, пока не убьёшь.

Решение: заменить `test_application_run` на `test_scrublar_application_builds_fastapi` (собирает FastAPI без `run()`). `ScrubLarApplication.run()` — `# pragma: no cover` с docstring.

**BaseLar:** в шаблон добавить `pytest-timeout` + `timeout = 10` в `[tool.pytest.ini_options]`. Записано в roadmap BaseLar v0.5.1.

### 3.3. INN precision 0.826 на adversarial

`inn10_valid("0000000000")` возвращал True: сумма весов × 0 = 0, check = 0. То же для SNILS/INN12.

Решение: `len(set(digits)) == 1 → False` в `validators.py`. Adversarial тест поймал реальный баг до релиза.

### 3.4. `Source file found twice` в mypy

`tau/fixtures/__init__.py` создал пакет, но `tau/` — без `__init__.py`. mypy видел `tau.fixtures.generator` и `fixtures.generator`.

Решение: `explicit_package_bases = true` + `mypy_path = ["."]` в `[tool.mypy]`.

### 3.5. `dict` инвариантность в mypy

`_render(replacements: dict[str, tuple[str, PIIKind | None]])` не принимал `dict[str, tuple[str, PIIKind]]`.

Решение: `Mapping` вместо `dict` в сигнатуре.

### 3.6. `evaluate.py` не видит `tau/`

`python omega/scripts/evaluate.py` добавляет в sys.path `omega/scripts/`, не корень.

Решение: `make evaluate` с `PYTHONPATH=.`.

### 3.7. Pre-commit mypy падал на промежуточном коммите

`pass_filenames: false` в mypy-хуке — проверяет весь проект. Коммит «инфраструктуры» (test_application.py) без фичи (ScrubLarApplication) не проходил.

Решение: фича + тесты — атомарны. Разделять можно только код и документацию. Записано в roadmap BaseLar.

## 4. Что работает

**Модульная независимость.** Ноль нарушений import-linter. `gamma` не знает про `beta`/`delta`/`epsilon` (ADR-0010), `beta` не знает про `epsilon` напрямую (через contracts). psi — композиционный корень.

**Детерминизм через seed.** Natasha детерминирована, regex + checksums — детерминированы. Один seed → один результат.

**Adversarial тестирование реально работает.** FP-кандидаты нашли баг в валидаторе ИНН (all-same-digit). Без adversarial было бы 100% в тестах и баг в проде.

**Размер.** 280 MB `.venv` (Natasha 30 MB + fastapi + python-docx + pymorphy3 + dev-tools). Укладывается в «лёгкий локальный сервис». GLiNER-large (2.3 GB) отвергнут правильно.

**Покрытие 100% branch на 98 файлах.** 217 тестов.

## 5. Известные ограничения (для README и курсовой)

- NAME precision 0.86 на синтетике: не отличает ФИО от «ООО «Иванов и партнёры»». Контекстный слой — v0.2.
- PDF не поддерживается — v0.2.
- Адреса, банковские реквизиты, ОГРН — v0.2.
- Инициалы — только «Фамилия И.О.» и «Фамилия И. О.».
- 50 синтетических документов — не реальный benchmark. 20–30 вручную размеченных — v0.2.

## 6. Уроки для v0.2 / следующих проектов

**Переносится:**

- ADR перед кодом (0007–0011 — все до или одновременно с реализацией).
- Adversarial fixtures с первого дня (clean = smoke, adversarial = quality).
- Resolver pattern с DI выдержал: beta не импортирует epsilon._internal.
- `zetal` для spike (ner-benchmark) — правильно, ADR в iota, код в zeta не вливается.
- Tiny architecture (две чистые функции detect/mask) — проще тестировать и объяснять.

**Сложнее в v0.2:**

- PDF: `pymupdf` или `pdfplumber` — извлечение текста из PDF с колонками/таблицами — нетривиально.
- Контекстный слой для NER: словарь компаний/ООО, правила «Иванов после ООО = компания», нормализация падежей через pymorphy3 до NER.
- Реальный benchmark: 20–30 вручную размеченных документов (волонтёры, обезличенные).
- Адреса, банковские реквизиты, ОГРН — новые regex + checksums (ОГРН 13 цифр, контрольная сумма).

**BaseLar долги (roadmap v0.5.1):**

- `pytest-timeout` глобально.
- `test_application_run` в шаблоне — заменить на `builds_fastapi`.
- `pass_filenames: false` + `mypy_path` — документация в CONTRIBUTING.
- `--cov-branch` — уже в v0.5.0, ок.

## 7. Чек-лист инициализации (для следующего проекта)

При создании проекта из BaseLar v0.5.0:

- [x] GitHub Template → репо, Private
- [x] `git clone`, `make install`
- [x] `omega` существует (или создать)
- [x] `omicron` от `nu`
- [x] Идентичность: version 0.0.0, name, description, README, CHANGELOG, PLAN
- [x] Первая ADR — продолжает нумерацию BaseLar
- [x] `make check` зелёный
- [x] Первый коммит + push

**Что добавить из ScrubLar в чек-лист:**

- [ ] Проверить `httpx2` (а не `httpx`) в `dev` — Starlette 1.2+ prefers `httpx2`.
- [ ] `tau/` без `__init__.py` + `explicit_package_bases` в mypy — либо `tau/__init__.py`.
- [ ] `make evaluate` для проектов с моделями — `PYTHONPATH=.` в Makefile.
- [ ] Adversarial fixtures с первого дня — clean = smoke, adversarial = quality.

## 8. Заключение

ScrubLar v0.1.0 — стабильный играбельный MVP. 217 тестов, 100% branch, ноль нарушений архитектуры, метрики честные (adversarial поймал баг в валидаторе ИНН до релиза).

Проверка на прочность — v0.2: PDF, реальный benchmark, контекстный слой для NER, дополнительные типы ПДн.

**ScrubLar в проде.** Запускайте `make run`, проверяйте вывод, находите, что не так: баланс между recall и precision, ограничения на реальных документах, UX.

---

**Конец отчёта.**
