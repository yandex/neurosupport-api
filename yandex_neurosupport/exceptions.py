class APIError(Exception):
    """Базовая ошибка API."""
    pass

class AuthenticationError(APIError):
    """Ошибка аутентификации."""
    pass