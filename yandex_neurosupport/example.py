import os
from yandex_neurosupport import YandexCloudNeuroSupportClient, get_iam_token

client = YandexCloudNeuroSupportClient(
    auth_token=get_iam_token(),         # Или используйте свой способ
    folder_id=os.getenv('FOLDER_ID'),   # Или укажите вручную: 'your_folder_id'
    service=os.getenv('SERVICE'),       # Или укажите вручную: 'your_service'
    product=os.getenv('PRODUCT')        # Или укажите вручную: 'your_product'
)

print(client.check_api())