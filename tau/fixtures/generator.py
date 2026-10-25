"""Deterministic synthetic PII documents for metrics.

Each document is a short business text (contract, letter, statement)
with a known set of PII spans. Generated from a seed — same seed,
same documents, same ground truth.

Two flavours, mixed 50/50 by index:
- **clean** (even idx): nominal case, straightforward patterns. Smoke
  test that pipeline works end-to-end.
- **adversarial** (odd idx): oblique cases (genitive/dative) for ФИО,
  plus 1–2 false-positive candidates ("ООО «Ромашка»", "приказ № …",
  invalid SNILS/INN checksums). Honest quality estimate: NER is
  weaker on oblique cases, regex must reject non-PII look-alikes.

Ground truth: list of (kind, value, start, end) with exact offsets
into `text`. Generated values pass checksums (SNILS, INN) where
applicable.

Not a test module (no `test_` prefix) — used by `test_metrics.py`
and `omega/scripts/evaluate.py`.
"""

from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass

from nu.psi.contracts.alpha import PIIKind

__all__ = ["FixtureDocument", "generate_documents"]


@dataclass(frozen=True, slots=True)
class FixtureDocument:
    name: str
    text: str
    spans: tuple[tuple[PIIKind, str, int, int], ...]


_SURNAMES_M = (
    "Иванов",
    "Петров",
    "Сидоров",
    "Кузнецов",
    "Смирнов",
    "Морозов",
    "Волков",
    "Николаев",
    "Соколов",
    "Фёдоров",
)
_SURNAMES_F = (
    "Иванова",
    "Петрова",
    "Сидорова",
    "Кузнецова",
    "Смирнова",
    "Морозова",
    "Волкова",
    "Николаева",
    "Соколова",
    "Фёдорова",
)
_NAMES_M = (
    "Иван",
    "Пётр",
    "Сергей",
    "Алексей",
    "Дмитрий",
    "Андрей",
    "Николай",
    "Михаил",
    "Артём",
    "Олег",
)
_NAMES_F = (
    "Мария",
    "Анна",
    "Ольга",
    "Екатерина",
    "Дарья",
    "Елена",
    "Наталья",
    "Ирина",
    "Татьяна",
    "Юлия",
)
_PATRONYMICS_M = (
    "Иванович",
    "Петрович",
    "Сергеевич",
    "Алексеевич",
    "Дмитриевич",
    "Андреевич",
    "Николаевич",
)
_PATRONYMICS_F = (
    "Ивановна",
    "Петровна",
    "Сергеевна",
    "Алексеевна",
    "Дмитриевна",
    "Андреевна",
    "Николаевна",
)

_TEMPLATES_CLEAN = (
    "Настоящий договор заключён между ООО «Ромашка» и {fio}, телефон {phone}, email {email}.",
    "Заявление от {fio}. Контактные данные: {phone}, {email}. СНИЛС {snils}, ИНН {inn}.",
    "Клиент: {fio}. Паспорт {passport}. Телефон: {phone}.",
    "Служебная записка. Ответственный: {fio}, тел. {phone}, e-mail {email}, ИНН {inn}.",
    "Согласие на обработку персональных данных. Субъект: {fio}, СНИЛС {snils}, паспорт {passport}.",
    "Реквизиты для перевода: получатель {fio}, ИНН {inn}, телефон {phone}.",
    "Обращение гражданина {fio} по вопросу договора. Связаться: {phone} или {email}.",
)

# Fixed oblique forms — no full Russian morphology, just examples
# that cover genitive and dative for common surname patterns.
# (nominative, genitive, dative)
_FIO_OBLIQUE = (
    ("Иванов Иван Иванович", "Иванова Ивана Ивановича", "Иванову Ивану Ивановичу"),
    ("Петрова Мария Сергеевна", "Петровой Марии Сергеевны", "Петровой Марии Сергеевне"),
    ("Сидоров Пётр Алексеевич", "Сидорова Петра Алексеевича", "Сидорову Петру Алексеевичу"),
    ("Кузнецова Анна Дмитриевна", "Кузнецовой Анны Дмитриевны", "Кузнецовой Анне Дмитриевне"),
    ("Смирнов Алексей Николаевич", "Смирнова Алексея Николаевича", "Смирнову Алексею Николаевичу"),
    ("Морозова Екатерина Ивановна", "Морозовой Екатерины Ивановны", "Морозовой Екатерине Ивановне"),
)

_TEMPLATES_OBLIQUE = (
    "Договор заключён с {fio_gen}. Телефон: {phone}.",
    "Обращение от гражданина {fio_gen}. СНИЛС {snils}.",
    "Настоящим уведомляем {fio_dat}. Email: {email}.",
    "Претензия предъявлена {fio_dat}. ИНН {inn}.",
    "Запрос поступил от {fio_gen}, контакт {phone}.",
)

# False-positive candidates: look like PII but must be rejected.
# "ООО «Иванов и партнёры»" is a company, not a person — NER may
# misclassify "Иванов" as PER, this is a real limitation.
# "СНИЛС 123-456-789 00" / "ИНН 0000000000" have valid format but
# invalid checksums — regex should find them, validator should reject.
_FP_CANDIDATES = (
    "приказ № 1234567",
    "код ошибки 1234",
    "дата 12.03.1985",
    "ООО «Ромашка»",
    "ООО «Иванов и партнёры»",
    "версия 8.999.123",
    "СНИЛС 123-456-789 00",
    "ИНН 0000000000",
)


def _snils_valid(rng: random.Random) -> str:
    while True:
        base = "".join(str(rng.randint(0, 9)) for _ in range(9))
        weights = (9, 8, 7, 6, 5, 4, 3, 2, 1)
        total = sum(int(d) * w for d, w in zip(base, weights, strict=True))
        if total < 100:
            check = total
        elif total in (100, 101):
            check = 0
        else:
            check = total % 101
            if check == 100:
                check = 0
        candidate = base + f"{check:02d}"
        digits = candidate
        weights2 = (9, 8, 7, 6, 5, 4, 3, 2, 1)
        t = sum(int(d) * w for d, w in zip(digits[:9], weights2, strict=True))
        c = t if t < 100 else (0 if t in (100, 101) else (t % 101 if t % 101 != 100 else 0))
        if int(digits[-2:]) == c:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:9]} {digits[9:]}"


def _inn_valid(rng: random.Random) -> str:
    base9 = "".join(str(rng.randint(0, 9)) for _ in range(9))
    w = (2, 4, 10, 3, 5, 9, 4, 6, 8)
    total = sum(int(d) * ww for d, ww in zip(base9, w, strict=True))
    check = (total % 11) % 10
    return base9 + str(check)


def _phone(rng: random.Random) -> str:
    return f"+79{rng.randint(100000000, 999999999)}"


def _email(rng: random.Random) -> str:
    local = "".join(rng.choices("abcdefghijklmnopqrstuvwxyz", k=6))
    domain = rng.choice(("example.com", "test.ru", "mail.ru", "corp.io"))
    return f"{local}@{domain}"


def _passport(rng: random.Random) -> str:
    series = f"{rng.randint(10, 99)} {rng.randint(10, 99)}"
    number = f"{rng.randint(100000, 999999)}"
    return f"{series} {number}"


def _fio(rng: random.Random) -> str:
    female = rng.random() < 0.5
    surname = rng.choice(_SURNAMES_F if female else _SURNAMES_M)
    name = rng.choice(_NAMES_F if female else _NAMES_M)
    patronymic = rng.choice(_PATRONYMICS_F if female else _PATRONYMICS_M)
    return f"{surname} {name} {patronymic}"


def _render(
    template: str,
    replacements: Mapping[str, tuple[str, PIIKind | None]],
) -> tuple[str, list[tuple[PIIKind, str, int, int]]]:
    """Fill template placeholders, tracking offsets. None kind = no span."""
    parts: list[str] = []
    spans: list[tuple[PIIKind, str, int, int]] = []
    cursor = 0
    rest = template
    while True:
        positions = [(rest.find(k), k) for k in replacements if k in rest]
        if not positions:
            break
        pos, key = min(positions)
        parts.append(rest[:pos])
        cursor += pos
        value, kind = replacements[key]
        if kind is not None:
            start = cursor
            end = start + len(value)
            spans.append((kind, value, start, end))
        parts.append(value)
        cursor += len(value)
        rest = rest[pos + len(key) :]
    parts.append(rest)
    return "".join(parts), spans


def _make_clean_document(rng: random.Random, idx: int) -> FixtureDocument:
    template = rng.choice(_TEMPLATES_CLEAN)
    fio = _fio(rng)
    phone = _phone(rng)
    email = _email(rng)
    snils = _snils_valid(rng)
    inn = _inn_valid(rng)
    passport = _passport(rng)
    replacements = {
        "{fio}": (fio, PIIKind.NAME),
        "{phone}": (phone, PIIKind.PHONE),
        "{email}": (email, PIIKind.EMAIL),
        "{snils}": (snils, PIIKind.SNILS),
        "{inn}": (inn, PIIKind.INN),
        "{passport}": (passport, PIIKind.PASSPORT),
    }
    text, spans = _render(template, replacements)
    return FixtureDocument(name=f"clean_{idx:03d}.txt", text=text, spans=tuple(spans))


def _make_adversarial_document(rng: random.Random, idx: int) -> FixtureDocument:
    template = rng.choice(_TEMPLATES_OBLIQUE)
    fio_nom, fio_gen, fio_dat = rng.choice(_FIO_OBLIQUE)
    phone = _phone(rng)
    email = _email(rng)
    snils = _snils_valid(rng)
    inn = _inn_valid(rng)
    replacements = {
        "{fio_nom}": (fio_nom, PIIKind.NAME),
        "{fio_gen}": (fio_gen, PIIKind.NAME),
        "{fio_dat}": (fio_dat, PIIKind.NAME),
        "{phone}": (phone, PIIKind.PHONE),
        "{email}": (email, PIIKind.EMAIL),
        "{snils}": (snils, PIIKind.SNILS),
        "{inn}": (inn, PIIKind.INN),
    }
    text, spans = _render(template, replacements)
    # Add 1–2 FP candidates at the end (don't shift existing spans).
    fp_count = rng.randint(1, 2)
    for _ in range(fp_count):
        fp = rng.choice(_FP_CANDIDATES)
        text += f" {fp}."
    return FixtureDocument(name=f"adv_{idx:03d}.txt", text=text, spans=tuple(spans))


def generate_documents(seed: int = 42, count: int = 50) -> list[FixtureDocument]:
    """Generate deterministic documents from seed, mixed clean/adversarial."""
    rng = random.Random(seed)
    docs: list[FixtureDocument] = []
    for i in range(count):
        if i % 2 == 0:
            docs.append(_make_clean_document(rng, i))
        else:
            docs.append(_make_adversarial_document(rng, i))
    return docs
