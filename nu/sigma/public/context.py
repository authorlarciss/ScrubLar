"""ContextVars для контекстных полей логов.

ContextVar изолирован между asyncio-задачами. В async-коде
request_id одного запроса не «протечёт» в другой.

Публичное состояние: set_request_id, set_user_id пишут сюда,
ContextFilter (в _internal) читает отсюда.
"""

from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)


__all__ = ["request_id_var", "user_id_var"]
