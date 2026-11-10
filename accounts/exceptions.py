from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    error = {"status": response.status_code}
    if isinstance(exc, ValidationError):
        error["message"] = "Некоректні дані. Перевірте поля запиту."
        error["details"] = response.data
    elif response.status_code == 401:
        error["message"] = "Потрібно увійти в акаунт. Перевірте логін і пароль або оновіть токен."
    else:
        error["message"] = str(response.data.get("detail", "Сталася помилка."))
    response.data = {"error": error}
    return response
