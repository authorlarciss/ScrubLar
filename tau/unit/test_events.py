"""Тесты IEvent."""

from dataclasses import FrozenInstanceError, dataclass

import pytest

from nu.psi.contracts.alpha import IEvent


def test_i_event_cannot_be_instantiated() -> None:
    """IEvent нельзя инстанцировать напрямую — это маркер."""
    with pytest.raises(TypeError, match="marker"):
        IEvent()


def test_concrete_event_instantiable() -> None:
    """Наследник IEvent инстанцируется нормально."""

    @dataclass(frozen=True)
    class UserRegistered(IEvent):
        user_id: int
        email: str

    event = UserRegistered(user_id=42, email="test@example.com")
    assert event.user_id == 42
    assert event.email == "test@example.com"


def test_concrete_event_frozen() -> None:
    """Конкретное событие — frozen dataclass."""

    @dataclass(frozen=True)
    class UserRegistered(IEvent):
        user_id: int

    event = UserRegistered(user_id=42)
    with pytest.raises(FrozenInstanceError):
        setattr(event, "user_id", 99)  # noqa: B010


def test_concrete_event_equality() -> None:
    """Frozen dataclass сравнивается по полям."""

    @dataclass(frozen=True)
    class EventA(IEvent):
        value: int

    assert EventA(1) == EventA(1)
    assert EventA(1) != EventA(2)
