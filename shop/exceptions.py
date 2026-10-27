from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Конфлікт з поточним станом даних."
    default_code = "conflict"


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    details = None
    if isinstance(exc, ValidationError):
        message = "Некоректні дані. Перевірте поля запиту."
        details = response.data
    else:
        detail = getattr(exc, "detail", None)
        message = str(detail) if detail else "Сталася помилка."

    error = {"status": response.status_code, "message": message}
    if details is not None:
        error["details"] = details
    response.data = {"error": error}
    return response
