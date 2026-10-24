"""Общие фикстуры для тестов."""

import pytest


@pytest.fixture
def sample_fixture() -> str:
    """Пример фикстуры. Удалить при первом реальном тесте."""
    return "sample"
