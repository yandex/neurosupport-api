# Yandex Neurosupport Client

Библиотека предоставляет удобный клиент для взаимодействия с Yandex NeuroSupport API. Поддерживает создание/обновление/удаление индексов, получение документов, генеративные ответы и другие операции.

## Установка

Установите через pip:
```bash
pip install yandex_neurosupport
```

Нужно подставить свои параметры: `service`, `product`, `prefix_index` - которые выдадут при регистрации.
OAuth-токен `token` нужно получить по ссылке в документации, которую также выдадут при регистрации.

```python
import os
from yandex_neurosupport import NeuroSupportClient

client = NeuroSupportClient(
    auth_token=os.getenv('TOKEN'),      # Или укажите свой токен вручную
    service=os.getenv('SERVICE'),       # Или укажите выданный при регистрации сервис вручную
    product=os.getenv('PRODUCT')        # Или укажите выданный при регистрации продукт вручную
)

print(client.check_api())
# True
```