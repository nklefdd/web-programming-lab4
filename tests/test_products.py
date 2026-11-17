from decimal import Decimal

import pytest

from shop.models import Product

LIST_URL = "/api/products"
ADMIN_ONLY_MESSAGE = "Змінювати каталог може лише адміністратор."
PRODUCT_FIELDS = {"id", "name", "description", "price", "metal", "stock", "category", "category_name"}


def detail_url(pk):
    return f"{LIST_URL}/{pk}"


def assert_error(response, status_code):
    assert response.status_code == status_code
    error = response.json()["error"]
    assert error["status"] == status_code
    assert error["message"]
    return error


@pytest.mark.django_db
class TestListProducts:
    def test_anonymous_gets_empty_list(self, anon_client):
        response = anon_client.get(LIST_URL)

        assert response.status_code == 200
        assert response.json() == []

    def test_products_are_ordered_by_id(self, anon_client, product, second_product):
        response = anon_client.get(LIST_URL)

        assert response.status_code == 200
        assert [item["id"] for item in response.json()] == [product.pk, second_product.pk]

    def test_item_contains_expected_fields(self, anon_client, product):
        response = anon_client.get(LIST_URL)

        item = response.json()[0]
        assert set(item) == PRODUCT_FIELDS
        assert item["price"] == "12500.00"
        assert item["category"] == product.category.pk
        assert item["category_name"] == "Каблучки"

    def test_regular_user_can_list(self, user_client, product):
        response = user_client.get(LIST_URL)

        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_anonymous_gets_product(self, anon_client, product):
        response = anon_client.get(detail_url(product.pk))

        assert response.status_code == 200
        assert response.json()["id"] == product.pk
        assert response.json()["name"] == "Каблучка з діамантом"

    def test_missing_product_returns_404(self, anon_client):
        response = anon_client.get(detail_url(99999))

        error = assert_error(response, 404)
        assert "99999" in error["message"]

    def test_invalid_token_returns_401(self, anon_client, product):
        anon_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.value")

        response = anon_client.get(detail_url(product.pk))

        assert_error(response, 401)


@pytest.mark.django_db
class TestCreateProduct:
    def test_admin_creates_product(self, admin_client, product_payload):
        response = admin_client.post(LIST_URL, product_payload, format="json")

        assert response.status_code == 201
        body = response.json()
        assert set(body) == PRODUCT_FIELDS
        assert body["name"] == "Браслет з перлами"
        assert body["category_name"] == "Каблучки"
        assert Product.objects.count() == 1
        assert Product.objects.get(pk=body["id"]).price == Decimal("8700.00")

    def test_optional_fields_use_defaults(self, admin_client, product_payload):
        del product_payload["stock"]
        del product_payload["description"]

        response = admin_client.post(LIST_URL, product_payload, format="json")

        assert response.status_code == 201
        assert response.json()["stock"] == 0
        assert response.json()["description"] == ""

    def test_anonymous_gets_401(self, anon_client, product_payload):
        response = anon_client.post(LIST_URL, product_payload, format="json")

        assert_error(response, 401)
        assert Product.objects.count() == 0

    def test_regular_user_gets_403(self, user_client, product_payload):
        response = user_client.post(LIST_URL, product_payload, format="json")

        error = assert_error(response, 403)
        assert error["message"] == ADMIN_ONLY_MESSAGE
        assert Product.objects.count() == 0

    @pytest.mark.parametrize(
        "field, value",
        [
            ("price", "0"),
            ("price", "-5"),
            ("price", "abc"),
            ("name", ""),
            ("name", "x" * 201),
            ("metal", ""),
            ("stock", -1),
            ("category", 99999),
        ],
    )
    def test_invalid_value_returns_400(self, admin_client, product_payload, field, value):
        product_payload[field] = value

        response = admin_client.post(LIST_URL, product_payload, format="json")

        error = assert_error(response, 400)
        assert field in error["details"]
        assert Product.objects.count() == 0

    @pytest.mark.parametrize("field", ["name", "price", "metal", "category"])
    def test_missing_required_field_returns_400(self, admin_client, product_payload, field):
        del product_payload[field]

        response = admin_client.post(LIST_URL, product_payload, format="json")

        error = assert_error(response, 400)
        assert field in error["details"]
        assert Product.objects.count() == 0

    def test_non_positive_price_message(self, admin_client, product_payload):
        product_payload["price"] = "0"

        response = admin_client.post(LIST_URL, product_payload, format="json")

        error = assert_error(response, 400)
        assert error["details"]["price"] == ["Ціна має бути більшою за 0."]


@pytest.mark.django_db
class TestUpdateProduct:
    def test_admin_updates_product(self, admin_client, product, product_payload):
        product_payload["price"] = "13900.00"
        product_payload["stock"] = 3

        response = admin_client.put(detail_url(product.pk), product_payload, format="json")

        assert response.status_code == 200
        product.refresh_from_db()
        assert product.price == Decimal("13900.00")
        assert product.stock == 3
        assert product.name == "Браслет з перлами"

    def test_admin_moves_product_to_other_category(self, admin_client, product, product_payload, other_category):
        product_payload["category"] = other_category.pk

        response = admin_client.put(detail_url(product.pk), product_payload, format="json")

        assert response.status_code == 200
        assert response.json()["category_name"] == "Сережки"
        product.refresh_from_db()
        assert product.category == other_category

    def test_missing_required_field_returns_400(self, admin_client, product, product_payload):
        del product_payload["name"]

        response = admin_client.put(detail_url(product.pk), product_payload, format="json")

        error = assert_error(response, 400)
        assert "name" in error["details"]

    def test_invalid_price_returns_400_and_keeps_data(self, admin_client, product, product_payload):
        product_payload["price"] = "-1"

        response = admin_client.put(detail_url(product.pk), product_payload, format="json")

        assert_error(response, 400)
        product.refresh_from_db()
        assert product.price == Decimal("12500.00")

    def test_missing_product_returns_404(self, admin_client, product_payload):
        response = admin_client.put(detail_url(99999), product_payload, format="json")

        assert_error(response, 404)

    def test_anonymous_gets_401(self, anon_client, product, product_payload):
        response = anon_client.put(detail_url(product.pk), product_payload, format="json")

        assert_error(response, 401)
        product.refresh_from_db()
        assert product.name == "Каблучка з діамантом"

    def test_regular_user_gets_403(self, user_client, product, product_payload):
        response = user_client.put(detail_url(product.pk), product_payload, format="json")

        error = assert_error(response, 403)
        assert error["message"] == ADMIN_ONLY_MESSAGE
        product.refresh_from_db()
        assert product.name == "Каблучка з діамантом"


@pytest.mark.django_db
class TestDeleteProduct:
    def test_admin_deletes_product(self, admin_client, product, second_product):
        response = admin_client.delete(detail_url(product.pk))

        assert response.status_code == 204
        assert not Product.objects.filter(pk=product.pk).exists()
        assert Product.objects.filter(pk=second_product.pk).exists()

    def test_second_delete_returns_404(self, admin_client, product):
        admin_client.delete(detail_url(product.pk))

        response = admin_client.delete(detail_url(product.pk))

        assert_error(response, 404)

    def test_missing_product_returns_404(self, admin_client):
        response = admin_client.delete(detail_url(99999))

        assert_error(response, 404)

    def test_anonymous_gets_401(self, anon_client, product):
        response = anon_client.delete(detail_url(product.pk))

        assert_error(response, 401)
        assert Product.objects.filter(pk=product.pk).exists()

    def test_regular_user_gets_403(self, user_client, product):
        response = user_client.delete(detail_url(product.pk))

        error = assert_error(response, 403)
        assert error["message"] == ADMIN_ONLY_MESSAGE
        assert Product.objects.filter(pk=product.pk).exists()


@pytest.mark.django_db
class TestProductLifecycle:
    def test_create_read_update_delete(self, admin_client, anon_client, product_payload):
        created = admin_client.post(LIST_URL, product_payload, format="json")
        assert created.status_code == 201
        pk = created.json()["id"]

        fetched = anon_client.get(detail_url(pk))
        assert fetched.status_code == 200
        assert fetched.json()["name"] == "Браслет з перлами"

        product_payload["stock"] = 0
        updated = admin_client.put(detail_url(pk), product_payload, format="json")
        assert updated.status_code == 200
        assert updated.json()["stock"] == 0

        deleted = admin_client.delete(detail_url(pk))
        assert deleted.status_code == 204
        assert anon_client.get(detail_url(pk)).status_code == 404


@pytest.mark.django_db
class TestOpenApiSchema:
    def test_schema_describes_products(self, anon_client):
        response = anon_client.get("/api/schema", {"format": "json"})

        assert response.status_code == 200
        paths = response.json()["paths"]
        assert {"get", "post"} <= set(paths["/api/products"])
        assert any(path.startswith("/api/products/") for path in paths)
