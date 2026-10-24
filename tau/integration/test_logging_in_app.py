"""Integration: логирование работает end-to-end."""

import logging

from nu.psi.bootstrap import build_application
from nu.psi.contracts.sigma import clear_context, get_logger, set_request_id, set_user_id


async def test_logging_with_context_in_app() -> None:
    """Контекст устанавливается, логгер видит его через filter."""
    build_application()

    logger = get_logger("test.integration")
    set_request_id("req-xyz")
    set_user_id(777)

    # Проверяем, что filter добавляет поля в record
    record = logging.LogRecord(
        name="nu.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test",
        args=(),
        exc_info=None,
    )
    from nu.sigma._internal.filters import ContextFilter

    ContextFilter().filter(record)
    assert record.request_id == "req-xyz"  # type: ignore[attr-defined]
    assert record.user_id == 777  # type: ignore[attr-defined]

    clear_context()
    logger.info("logged after clear_context")
