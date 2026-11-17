from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema

from .serializers import ErrorSerializer, ProductSerializer

TAGS = ["Products"]
JWT = [{"jwtAuth": []}]

PRODUCT_ID = OpenApiParameter(
    name="pk",
    type=int,
    location=OpenApiParameter.PATH,
    description="Ідентифікатор прикраси.",
)

PRODUCT_EXAMPLE = {
    "id": 1,
    "name": "Каблучка з діамантом",
    "description": "Біле золото",
    "price": "12500.00",
    "metal": "Золото",
    "stock": 5,
    "category": 1,
    "category_name": "Каблучки",
}

PRODUCT_REQUEST_EXAMPLE = {
    "name": "Каблучка з діамантом",
    "description": "Біле золото",
    "price": "12500.00",
    "metal": "Золото",
    "stock": 5,
    "category": 1,
}

UNAUTHORIZED_EXAMPLE = OpenApiExample(
    "Немає токена",
    value={
        "error": {
            "status": 401,
            "message": "Потрібно увійти в акаунт. Перевірте логін і пароль або оновіть токен.",
        }
    },
    response_only=True,
    status_codes=["401"],
)

FORBIDDEN_EXAMPLE = OpenApiExample(
    "Недостатньо прав",
    value={
        "error": {
            "status": 403,
            "message": "Змінювати каталог може лише адміністратор.",
        }
    },
    response_only=True,
    status_codes=["403"],
)

NOT_FOUND_EXAMPLE = OpenApiExample(
    "Прикрасу не знайдено",
    value={
        "error": {
            "status": 404,
            "message": "Прикрасу з id=99999 не знайдено.",
        }
    },
    response_only=True,
    status_codes=["404"],
)

VALIDATION_EXAMPLE = OpenApiExample(
    "Невалідна ціна",
    value={
        "error": {
            "status": 400,
            "message": "Некоректні дані. Перевірте поля запиту.",
            "details": {"price": ["Ціна має бути більшою за 0."]},
        }
    },
    response_only=True,
    status_codes=["400"],
)

product_list = extend_schema(
    tags=TAGS,
    summary="Список прикрас",
    description="Повертає всі прикраси, відсортовані за id. Доступно без авторизації.",
    responses={200: ProductSerializer(many=True)},
    examples=[OpenApiExample("Список прикрас", value=[PRODUCT_EXAMPLE], response_only=True, status_codes=["200"])],
)

product_create = extend_schema(
    tags=TAGS,
    summary="Додати прикрасу",
    description="Створює прикрасу. Лише адміністратор (`is_staff`). Потрібен хедер `Authorization: Bearer <access>`.",
    auth=JWT,
    request=ProductSerializer,
    responses={
        201: ProductSerializer,
        400: ErrorSerializer,
        401: ErrorSerializer,
        403: ErrorSerializer,
    },
    examples=[
        OpenApiExample("Нова прикраса", value=PRODUCT_REQUEST_EXAMPLE, request_only=True),
        OpenApiExample("Створено", value=PRODUCT_EXAMPLE, response_only=True, status_codes=["201"]),
        VALIDATION_EXAMPLE,
        UNAUTHORIZED_EXAMPLE,
        FORBIDDEN_EXAMPLE,
    ],
)

product_retrieve = extend_schema(
    tags=TAGS,
    summary="Одна прикраса",
    description="Повертає прикрасу за id. Доступно без авторизації.",
    parameters=[PRODUCT_ID],
    responses={200: ProductSerializer, 404: ErrorSerializer},
    examples=[
        OpenApiExample("Прикраса", value=PRODUCT_EXAMPLE, response_only=True, status_codes=["200"]),
        NOT_FOUND_EXAMPLE,
    ],
)

product_update = extend_schema(
    tags=TAGS,
    summary="Змінити прикрасу",
    description=(
        "Повністю оновлює прикрасу: обов'язкові поля передаються повністю. "
        "Лише адміністратор (`is_staff`). Потрібен хедер `Authorization: Bearer <access>`."
    ),
    auth=JWT,
    parameters=[PRODUCT_ID],
    request=ProductSerializer,
    responses={
        200: ProductSerializer,
        400: ErrorSerializer,
        401: ErrorSerializer,
        403: ErrorSerializer,
        404: ErrorSerializer,
    },
    examples=[
        OpenApiExample("Нові дані", value=dict(PRODUCT_REQUEST_EXAMPLE, price="13900.00", stock=3), request_only=True),
        OpenApiExample(
            "Оновлено",
            value=dict(PRODUCT_EXAMPLE, price="13900.00", stock=3),
            response_only=True,
            status_codes=["200"],
        ),
        VALIDATION_EXAMPLE,
        UNAUTHORIZED_EXAMPLE,
        FORBIDDEN_EXAMPLE,
        NOT_FOUND_EXAMPLE,
    ],
)

product_delete = extend_schema(
    tags=TAGS,
    summary="Видалити прикрасу",
    description="Видаляє прикрасу. Лише адміністратор (`is_staff`). Потрібен хедер `Authorization: Bearer <access>`.",
    auth=JWT,
    parameters=[PRODUCT_ID],
    responses={
        204: None,
        401: ErrorSerializer,
        403: ErrorSerializer,
        404: ErrorSerializer,
    },
    examples=[UNAUTHORIZED_EXAMPLE, FORBIDDEN_EXAMPLE, NOT_FOUND_EXAMPLE],
)
