# Yandex Neurosupport Client

Библиотека предоставляет удобный клиент для взаимодействия с Yandex NeuroSupport API. Поддерживает создание/обновление/удаление индексов, получение документов, генеративные ответы и другие операции.

## Установка

Установите через pip:
```bash
pip install yandex_neurosupport
```

Нужно узнать свой `iam_token` и `folder_id` из Yandex Cloud.
И подставить свои параметры: `service`, `product`, `prefix_index` - которые выдадут при регистрации.

```python
import os
from yandex_neurosupport import YandexCloudNeuroSupportClient, get_iam_token

client = YandexCloudNeuroSupportClient(
    auth_token=get_iam_token(),         # Или используйте свой способ
    folder_id=os.getenv('FOLDER_ID'),   # Или укажите вручную: 'your_folder_id'
    service=os.getenv('SERVICE'),       # Или укажите вручную: 'your_service'
    product=os.getenv('PRODUCT')        # Или укажите вручную: 'your_product'
)

print(client.check_api())
# True
```