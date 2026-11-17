from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from shop.models import Category, Product

PASSWORD = "Str0ng!Pass-2026"


@pytest.fixture(autouse=True)
def fast_password_hasher(settings):
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


def login(client, user):
    response = client.post(
        "/api/auth/login",
        {"username": user.username, "password": PASSWORD},
        format="json",
    )
    assert response.status_code == 200
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")
    return client


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password=PASSWORD,
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="customer",
        email="customer@example.com",
        password=PASSWORD,
    )


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def admin_client(admin_user):
    return login(APIClient(), admin_user)


@pytest.fixture
def user_client(regular_user):
    return login(APIClient(), regular_user)


@pytest.fixture
def category(db):
    return Category.objects.create(name="Каблучки")


@pytest.fixture
def other_category(db):
    return Category.objects.create(name="Сережки")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Каблучка з діамантом",
        description="Біле золото",
        price=Decimal("12500.00"),
        metal="Золото",
        stock=5,
        category=category,
    )


@pytest.fixture
def second_product(other_category):
    return Product.objects.create(
        name="Сережки-гвоздики",
        description="Срібло 925",
        price=Decimal("2300.00"),
        metal="Срібло",
        stock=10,
        category=other_category,
    )


@pytest.fixture
def product_payload(category):
    return {
        "name": "Браслет з перлами",
        "description": "Ручна робота",
        "price": "8700.00",
        "metal": "Срібло",
        "stock": 4,
        "category": category.pk,
    }
