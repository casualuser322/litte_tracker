import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Включает доступ к БД для всех тестов"""
    pass


@pytest.fixture
def client():
    """Фикстура Django test client"""
    from django.test import Client
    return Client()
