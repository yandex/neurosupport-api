import re
import subprocess
from typing import Optional, Union, List, Dict, Any


def get_folder_id(folder_id: str) -> str:
    """Получает folder ID"""
    return folder_id

def get_service(service: str) -> str:
    """Получает service. Выдается после обработки заявки на подключение"""
    return service

def get_product(product: str) -> str:
    """Получает product. Выдается после обработки заявки на подключение"""
    return product

def get_index_name(index: str) -> str:
    """Получает prefix index. Выдается после обработки заявки на подключение"""
    return index

def get_iam_token() -> Optional[str]:
    """Получает IAM-токен через yc CLI."""
    try:
        result = subprocess.run(['yc', 'iam', 'create-token'],
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении IAM-токена: {e}")
        return None
    except FileNotFoundError:
        print("Команда 'yc' не найдена. Убедитесь, что Yandex Cloud CLI установлен.")
        return None

def mask_response_fields(
    data: Union[Dict, List, Any],
    keys_to_mask: Optional[List[str]] = None,
    values_to_mask: Optional[List[str]] = None,
    placeholder: str = "******"
) -> Union[Dict, List, Any]:
    """
    Рекурсивно маскирует чувствительные данные в словарях, списках и строках.

    1. Если ключ словаря совпадает с одним из `keys_to_mask`, его значение
       полностью заменяется на плейсхолдер. Сравнение ключей регистронезависимо.
    2. Если встречается строка, в ней ищутся и заменяются все подстроки,
       совпадающие с `values_to_mask`. Поиск и замена регистронезависимы.

    Args:
        data: Входные данные для маскирования.
        keys_to_mask: Список ключей, значения которых нужно полностью замаскировать.
        values_to_mask: Список строк, которые нужно найти и замаскировать внутри других строк.
        placeholder: Строка, используемая для замены.

    Returns:
        Данные с замаскированными значениями.

    Examples:
    1.
    # Вход: data = "Password PASSWORD password and password123, product is my-secret-product"
    # mask_response_fields(data, values_to_mask=['password', 'my-secret'])
    # Выход: "****** ****** ****** and ******123, product is ******-product"

    2.
    # Вход: data = {"password":"1234", "username":"John"}
    # mask_response_fields(data, keys_to_mask=["password", "token", "apiKey", "username"])
    # Выход: {'password': '******', 'username': '******'}
    """
    keys_to_mask = keys_to_mask or []
    values_to_mask = values_to_mask or []

    lower_keys_to_mask = {k.lower() for k in keys_to_mask}

    value_mask_regex = None
    filtered_values = [v for v in values_to_mask if v]
    if filtered_values:
        pattern = '|'.join(re.escape(v) for v in filtered_values)
        value_mask_regex = re.compile(pattern, re.IGNORECASE)

    def _mask_recursive(item: Any) -> Any:
        if isinstance(item, dict):
            new_dict = {}
            for k, v in item.items():
                if k.lower() in lower_keys_to_mask:
                    new_dict[k] = placeholder
                else:
                    new_dict[k] = _mask_recursive(v)
            return new_dict
        elif isinstance(item, list):
            return [_mask_recursive(sub_item) for sub_item in item]

        elif isinstance(item, str):
            if value_mask_regex:
                return value_mask_regex.sub(placeholder, item)
            return item

        else:
            return item

    return _mask_recursive(data)