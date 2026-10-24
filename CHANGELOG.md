# Changelog

All notable changes to BaseLar are documented in this file.

Format based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

> **On cloning from BaseLar template:** replace this file with a fresh
> changelog for your project. Keep the format (Keep a Changelog 1.1.0),
> start from `## [0.1.0]` — your first release. BaseLar's own history
> below is for reference; delete it.
>
> For releases before v0.3.0 — see git tags `v0.1.0`, `v0.2.0` and
> `git log <tag>`.

## [Unreleased]

## [0.5.0] - 2026-10-24

### Added

- ADR-0006: beta-layer is an example, not a dogma. Scaffold
  (`IProcessor`, `IWorkflow`, `PipelineWorkflow`, `IEventBus`,
  `IEvent`) is optional; removing it via ADR is normal for
  non-pipeline domains (TirLar ADR-0007 as precedent).
- `CONTRIBUTING.md`: section "Beta-layer: scaffold and deviations" —
  rules for removing/replacing scaffold while keeping ADR-0002
  boundaries.
- `CONTRIBUTING.md`: section "Lazy import in resolver: test every
  factory" — each resolver factory gets its own test, forces
  `_internal/` import, checks `isinstance(..., IInterface)`.
- `--cov-branch` in `[tool.pytest.ini_options] addopts`. Line
  coverage 100% with uncovered branches is a false signal;
  branch coverage is the honest number. No `--cov-fail-under` —
  downstream projects set their own threshold.

### Changed

- Coverage report now shows branch coverage. BaseLar may drop
  below 100% on defensive raises; each case is either covered
  by a test or marked `# pragma: no branch` with justification.

## [0.4.2] - 2026-10-24

### Added

- `pytest` marker `template` — for tests specific to BaseLar's
  `build_application()`. Registered in `[tool.pytest.ini_options]`
  markers.

### Changed

- Template bootstrap tests moved to `tau/unit/test_bootstrap_template.py`
  with explicit docstring and `pytestmark = pytest.mark.template`.
  Reason: when `build_application()` is rewritten for a domain, these
  tests break (TirLar report, section 6.7). Marker allows skipping
  with `pytest -m "not template"` during refactoring.
- `lambda/CONTRIBUTING.md`: ADR numbering section — ADR numbers are
  ecosystem-wide, not per-project. New projects continue from maximum
  existing number + 1.

## [0.4.1] - 2026-10-22

### Fixed

- `tau/` now type-checked. `mypy` in `Makefile` (`typecheck`) and
  `ci.yml` extended from `nu` to `nu tau` — tests were not checked
  in v0.4.0, only in pre-commit.
- Removed unused `# type: ignore[attr-defined]` on `record.request_id`
  / `record.user_id` in `tau/unit/test_sigma_*.py` — same dead ignores
  as in `nu/sigma/_internal/filters.py` (fixed in v0.4.0), caught by
  `warn_unused_ignores` once `tau` is checked.

### Changed

- `.pre-commit-config.yaml`: mypy hook as `repo: local` +
  `language: system` (`.venv/bin/mypy`), `args: [nu, tau, ...]`.
  Replaces `mirrors-mypy` — isolated env cannot resolve project
  dependencies; `language: system` shares `.venv` with `make
  typecheck` and CI. Required for downstream projects with runtime
  deps (`fastapi`, `pydantic`, `transformers`).
- ADR-0005: note on `tau.*` overrides for test fixtures.

## [0.4.0] - 2026-10-22

### Added

- `mypy>=1.10` in `dev` dependencies, `[tool.mypy]` with
  `strict = true`, `warn_return_any`, `warn_unused_ignores`,
  `show_error_codes`, `show_error_context`, `pretty`.
- `[[tool.mypy.overrides]]` for untyped libraries: `transformers`,
  `torch`, `datasets`, `huggingface_hub`, `safetensors` —
  `ignore_missing_imports = true`, `follow_imports = "skip"`.
- `make typecheck` target (`mypy nu`); `make check` includes
  `typecheck` between `lint-imports` and `test`.
- CI step `mypy nu` after `import-linter`, before `pytest`.
- pre-commit hook `mirrors-mypy` v2.4.0 with
  `--config-file=pyproject.toml`.
- ADR-0005: mypy strict mode.
- CONTRIBUTING section "Mypy": strict mode, overrides for untyped
  libs, pydantic plugin for downstream, `ExtendedLogRecord` note
  for sigma context fields.

### Fixed

- `nu/sigma/_internal/filters.py`: removed unused
  `# type: ignore[attr-defined]` on `record.request_id` and
  `record.user_id` — typeshed now accepts arbitrary `LogRecord`
  attribute assignment. `warn_unused_ignores=true` caught them on
  first run.

### Changed

- `uv.lock`: regenerated with `mypy`.

## [0.3.3] - 2026-10-22

### Fixed

- Coverage: `JsonFormatter` exception branch (`nu/sigma/_internal/formatters.py:68`)
  now covered by `tau/unit/test_sigma_formatters.py::test_json_formatter_includes_exception`.
  BaseLar coverage: 97% → 100% for measured code.

### Changed

- `[tool.coverage.run] omit = ["nu/main.py"]` in `pyproject.toml` —
  launcher excluded from coverage. `main.py` is a thin entry point,
  not business logic; excluded explicitly rather than left at 0%.

## [0.3.2] - 2026-10-22

### Added

- `CHANGELOG.md` at repository root (Keep a Changelog 1.1.0 format).
- `pytest-cov` enabled in default `addopts`:
  `--cov=nu --cov-report=term-missing`. Coverage printed on every
  `pytest` run. No `--cov-fail-under` — downstream projects set their
  own threshold.

### Changed

- `lambda/VERSIONING.md`: rule 10 — every release updates `CHANGELOG.md`
  in the same commit as the version bump.
- `lambda/CONTRIBUTING.md`: section «Changelog» — when and how to update.
- `lambda/PLAN.md`: step «reset `CHANGELOG.md` on clone» in the
  quick-start.
- `README.md`: `CHANGELOG.md` in the documentation list, note about
  resetting it for a new project.

## [0.3.1] - 2026-10-21

### Fixed

- `tau/unit/test_structure.py` reformatted with `ruff format` —
  v0.3.0 shipped it black-formatted, which broke CI on
  `ruff format --check`. Black and ruff format wrap `assert`
  statements differently: black breaks the condition, ruff wraps
  the message.

### Changed

- `.pre-commit-config.yaml`: `black` + `isort` hooks replaced with
  `ruff` (`--fix`) + `ruff-format` from `astral-sh/ruff-pre-commit`.
  Hooks synced with `ruff` version in `.venv` to avoid oscillation.

## [0.3.0] - 2026-10-21

### Added

- ADR-0003: ruff format replaces black + isort.
- ADR-0004: import-linter completeness.
- import-linter rules 5 (`public → _internal`, except resolver) and
  6 (`main.py → psi only`, `allow_indirect_imports = true`).
- Makefile targets: `format-check`, `check`, `ci`.
- `[tool.ruff.format]` section in `pyproject.toml`.
- `tau/unit/test_structure.py` — structural tests for the template.

### Changed

- `pyproject.toml`: `ruff format` replaces `black` + `isort`;
  `ruff>=0.6`; `unmatched_ignore_imports_alerting = "error"` in all
  contracts; `nu.main` added to rules 3 and 4; resolver chains
  cleaned to `beta` + `sigma` only.
- `lambda/VERSIONING.md`: majors go `nu → alpha → beta → gamma →
  omega`, minors via `epsilon`. `beta` mandatory for majors.
- `lambda/ARCHITECTURE.md`: 6 contracts listed, `alpha` is types-only,
  contract examples updated (`IEvent`/`ICompiler` instead of
  `Point`/`Transform`).
- `lambda/CONTRIBUTING.md`: `make check` in pre-commit, `make ci`,
  both factory methods of `BetaResolver` shown, note about removed
  `per-file-ignores` for `F401`.
- `README.md`: correct version path (`nu/mu/public/__init__.py`),
  `zeta` and `iota` added to module list, examples vs business logic
  clarified.
- `Makefile`: `clean` also removes `.coverage`, `htmlcov`,
  `.mypy_cache`.
- `ci.yml`: `black --check` and `isort --check-only` replaced with
  `ruff format --check`.

### Removed

- `black`, `isort` from `[project.optional-dependencies].dev`.
- `[tool.black]`, `[tool.isort]` from `pyproject.toml`.
- `per-file-ignores` for `F401` — explicit re-export
  (`from X import Y as Y`) passes without it.
- `black` and `isort` hooks from `.pre-commit-config.yaml`.

## [0.2.0] and earlier

See git tags `v0.2.0`, `v0.1.0` and `git log <tag>` for details.
