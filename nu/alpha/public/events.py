"""Маркер события. Конкретные события — frozen dataclass в проектах."""


class IEvent:
    """Базовый маркер для событий.

    IEvent — marker class. Инстанцировать напрямую нельзя: событие
    без полей не имеет смысла. Конкретные события наследуют IEvent
    и являются frozen dataclass.

    Пример:

        from dataclasses import dataclass
        from nu.psi.contracts.alpha import IEvent

        @dataclass(frozen=True)
        class UserRegistered(IEvent):
            user_id: int
            email: str
    """

    def __new__(cls, *args: object, **kwargs: object) -> "IEvent":
        if cls is IEvent:
            raise TypeError("IEvent is a marker; instantiate a concrete event instead")
        return super().__new__(cls)


__all__ = ["IEvent"]
