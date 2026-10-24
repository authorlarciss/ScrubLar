"""Тесты форматтеров (внутренняя реализация sigma)."""

import json
import logging
import sys

# noinspection PyProtectedMember
from nu.sigma._internal.formatters import JsonFormatter, TextFormatter


def _make_record(
    msg: str = "test message",
    level: int = logging.INFO,
    request_id: str | None = None,
    user_id: int | None = None,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name="nu.test",
        level=level,
        pathname="test.py",
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )
    if request_id is not None:
        record.request_id = request_id
    if user_id is not None:
        record.user_id = user_id
    return record


def test_text_formatter_basic() -> None:
    formatter = TextFormatter(include_context=False)
    record = _make_record("hello")
    output = formatter.format(record)
    assert "INFO" in output
    assert "nu.test" in output
    assert "hello" in output


def test_text_formatter_with_context() -> None:
    formatter = TextFormatter(include_context=True)
    record = _make_record("hello", request_id="abc", user_id=42)
    output = formatter.format(record)
    assert "[req=abc user=42]" in output


def test_json_formatter_basic() -> None:
    formatter = JsonFormatter(include_context=False)
    record = _make_record("hello")
    output = formatter.format(record)
    payload = json.loads(output)
    assert payload["level"] == "INFO"
    assert payload["logger"] == "nu.test"
    assert payload["message"] == "hello"


def test_json_formatter_with_context() -> None:
    formatter = JsonFormatter(include_context=True)
    record = _make_record("hello", request_id="abc", user_id=42)
    output = formatter.format(record)
    payload = json.loads(output)
    assert payload["request_id"] == "abc"
    assert payload["user_id"] == 42


def test_json_formatter_includes_exception() -> None:
    """Exception info is serialized into the 'exception' field.

    Covers the `if record.exc_info:` branch in JsonFormatter.format:
    stdlib's formatException output is attached when a record carries
    an active exception.
    """
    formatter = JsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            name="nu.test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=0,
            msg="failed",
            args=(),
            exc_info=sys.exc_info(),
        )

    payload = json.loads(formatter.format(record))
    assert "exception" in payload
    assert "ValueError" in payload["exception"]
    assert "boom" in payload["exception"]
