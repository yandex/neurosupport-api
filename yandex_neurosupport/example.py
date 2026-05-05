import os
from yandex_neurosupport import NeuroSupportClient

client = NeuroSupportClient(
    auth_token=os.getenv('TOKEN'),      # Или укажите свой токен вручную
    service=os.getenv('SERVICE'),       # Или укажите выданный при регистрации сервис вручную
    product=os.getenv('PRODUCT')        # Или укажите выданный при регистрации продукт вручную
)

print(client.check_api())
