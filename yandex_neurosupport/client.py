import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional
from .exceptions import APIError, AuthenticationError

class BaseClient(ABC):
    """
    Абстрактный базовый клиент, содержащий общую логику для запросов к API.
    Механизм аутентификации и предоставление специфичных параметров (например, folder_id)
    должны быть реализованы в дочерних классах.
    """
    def __init__(
        self,
        service: str,
        product: str,
        base_url: str = "https://supportgpt.api.cloud.yandex.net"
    ):
        """
        Инициализирует клиент API.

        Args:
            service: Идентификатор сервиса. Выдается после обработки заявки на подключение (обязательный).
            product: Идентификатор продукта. Выдается после обработки заявки на подключение(обязательный).
            base_url: Базовый URL API (по умолчанию "https://supportgpt.api.cloud.yandex.net").

        Raises:
            TypeError: Если обязательные параметры не переданы.
        """
        self.service = service
        self.product = product
        self.base_url = base_url
        self.session = requests.Session()
        self._configure_auth()

    @abstractmethod
    def _configure_auth(self):
        """
        Абстрактный метод для настройки аутентификации.
        Должен быть реализован в дочерних классах для настройки self.session.headers.
        """
        raise NotImplementedError("Метод аутентификации должен быть реализован в дочернем классе.")

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Унифицированный метод для запросов. Возвращает {'body': dict or None, 'headers': dict}."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        try:
            response.raise_for_status()
            body = response.json() if response.content else None
            headers = dict(response.headers)
            return {'body': body, 'headers': headers}
        except requests.HTTPError as e:
            error_details = e.response.text
            raise APIError(f"Ошибка HTTP: {e} - {error_details}")
        except requests.RequestException as e:
            raise APIError(f"Ошибка сети или подключения: {e}")

    def check_api(self) -> bool:
        """
        Проверяет доступность API.

        Returns:
        True, если запрос к API прошел успешно.

        Raises:
        APIError: При ошибке HTTP запроса.
        """
        endpoint = '/indexer/v1/indexes'
        headers = {'x-folder-id': self.folder_id}
        try:
            self._request(method='GET', endpoint=endpoint, headers=headers)
            return True
        except APIError:
            raise

    def create_or_update_index(
        self,
        index_name: str,
        documents: List[Dict[str, Any]],
        meta: Optional[Dict[str, Any]] = None,
        auto_switch: Optional[bool] = None,
        diff: Optional[bool] = None,
        index_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Создание индекса или обновление существующего.

        Args:
            index_name: Строковое имя индекса (обязательное). Обязано содержать переданый префикс, после обработки заявки на подключение.
            documents: Список документов для индексации.
            meta: Метаинформация об индексе.
            auto_switch: Флаг автоматического переключения на новый индекс после создания.
            diff: Флаг, указывающий, что нужно создать индекс на основе текущего. **Не использовать для создания нового индекса.**
            index_version: Версия индекса.

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибке HTTP запроса.

        Note:
        Из-за особенностей API, флаг `diff=True` предназначен **строго для обновления**
        существующих индексов. Его передача при создании нового индекса с нуля
        приведет к ошибке.

        Example:
        # Правильно: обновление существующего индекса
        client.create_or_update_index(
            index_name='my-existing-index',
            documents=[{'id': 1, 'text': 'new data'}],
            diff=True
        )

        # Неправильно: попытка создать новый индекс с флагом diff
        client.create_or_update_index(
            index_name='my-brand-new-index',
            documents=[{'id': 1, 'text': 'some data'}],
            diff=True  # Так делать нельзя, приведет к ошибке!
        )
        """
        endpoint = f'/indexer/v1/indexes/{index_name}/documents'
        body = {
            "service": self.service,
            "product": self.product,
            "documents": documents,
        }
        if index_version is not None:
            body["index_version"] = index_version
        if meta is not None:
            body["meta"] = meta
        if auto_switch is not None:
            body["auto_switch"] = auto_switch
        if diff is not None:
            body["diff"] = diff
        return self._request(method='POST', endpoint=endpoint, json=body)

    def get_index_info(
        self,
        index_name: str,
        index_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Получение подробной информации о конкретной версии индекса.

        Args:
            index_name: Имя индекса, информацию о котором нужно получить (обязательный).
            index_version: Версия индекса. Если не указана, то API вернет информацию о текущей активной версии.

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибке HTTP запроса или проблемах с сетью.
        """
        endpoint = f'/indexer/v1/indexes/{index_name}'
        body = {
            "service": self.service,
            "product": self.product,
        }
        if index_version is not None:
            body["index_version"] = index_version
        return self._request(method='GET', endpoint=endpoint, json=body)

    def get_indexes_full(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Получение имен и метаданных всех индексов, на которые у пользователя есть права.

        Args:
            page: Номер страницы для постраничной загрузки (по умолчанию 1).
            size: Количество записей на странице (по умолчанию 10).

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибке HTTP запроса.
        """
        endpoint = '/indexer/v1/indexes'
        params = {
            "service": self.service,
            "product": self.product,
        }
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        return self._request(method='GET', endpoint=endpoint, params=params)

    def get_documents_from_index(
        self,
        index_name: str,
        index_version: Optional[int] = None,
        after_id: Optional[str] = None,
        search_query: Optional[str] = None,
        document_id: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Получение документов из индекса.

        Args:
            index_name: Строковое имя индекса (обязательное). Обязано содержать переданый префикс, после обработки заявки на подключение.
            index_version: Версия индекса.
            after_id: Для пагинации - вернуть документы с id больше заданного.
            search_query: Поисковой запрос по прямому вхождению текста.
            document_id: Получить один документ по заданному id.
            limit: Максимальное количество документов на запрос.
            sort_by: Поле для сортировки.
            sort_order: Порядок сортировки (asc или desc).

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибке HTTP запроса.
        """
        endpoint = f'/indexer/v1/indexes/{index_name}/documents'
        params = {
            "product": self.product,
            "service": self.service
        }
        if index_version is not None:
            params["index_version"] = index_version
        if after_id is not None:
            params["after_id"] = after_id
        if search_query is not None:
            params["search_query"] = search_query
        if document_id is not None:
            params["document_id"] = document_id
        if limit is not None:
            params["limit"] = limit
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order

        return self._request(method='GET', endpoint=endpoint, params=params)

    def get_generative_answer(
        self,
        index_name: str,
        dialog: List[Dict[str, Union[str, int]]],
        meta_features: Optional[Dict[str, Any]] = None,
        replies: int = 1,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Получение генеративных ответов от API.

        Args:
            index_name: Строковое имя индекса (обязательное). Обязано содержать переданый префикс, после обработки заявки на подключение.
            dialog: Список сообщений диалога с полями role, text, id (опционально), created (опционально).
            meta_features: Дополнительные метаданные контекста.
            replies: Количество ответов для генерации.
            options: Дополнительные параметры процессинга.

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибках HTTP запроса.
        """
        endpoint = '/api/v1/answer'
        body = {
            "service": self.service,
            "product": self.product,
            "index_name": index_name,
            "dialog": dialog
        }
        if meta_features is not None:
            body["meta_features"] = meta_features
        if options is not None:
            body["options"] = options
        if replies is not None:
            body["replies"] = replies
        return self._request(method='POST', endpoint=endpoint, json=body, timeout=60)

    def switch_index_version(
        self,
        index_name: str,
        index_version: int,
    ) -> Dict[str, Any]:
        """
        Переключение актуальной версии индекса.

        Args:
            index_name: Строковое имя индекса (обязательное). Обязано содержать переданый префикс, после обработки заявки на подключение.
            index_version: Версия индекса для переключения.

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибке HTTP запроса.
        """
        endpoint = f'/indexer/v1/indexes/{index_name}/switch_version'
        body = {
            "service": self.service,
            "product": self.product,
            "index_version": index_version,
        }
        return self._request(method='POST', endpoint=endpoint, json=body)

    def delete_documents_from_index(
        self,
        index_name: str,
        docs_ids: List[str],
        index_version: Optional[int] = None,
        auto_switch: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Удаление документов из индекса.

        Args:
            index_name: Строковое имя индекса (обязательное). Обязано содержать переданый префикс, после обработки заявки на подключение.
            docs_ids: ID документов для удаления (обязательное).
            index_version: Версия индекса.
            auto_switch: Переключиться на новый индекс.

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибке HTTP запроса.
        """
        endpoint = f'/indexer/v1/indexes/{index_name}/documents'
        params = {
            "service": self.service,
            "product": self.product,
            "docs_ids": docs_ids
        }
        if index_version is not None:
            params["index_version"] = index_version
        if auto_switch is not None:
            params["auto_switch"] = auto_switch
        return self._request(method='DELETE', endpoint=endpoint, params=params)

    def delete_index(
        self,
        index_name: str
    ) -> Dict[str, Any]:
        """
        Удаление всех индексов.

        Args:
            index_name: Строковое имя индекса (обязательное). Обязано содержать переданый префикс, после обработки заявки на подключение.

        Returns:
            Dict с данными ответа от API

        Raises:
            APIError: При ошибке HTTP запроса.
        """
        endpoint = f'/indexer/v1/indexes/{index_name}/delete'
        body = {
            "service": self.service,
            "product": self.product
        }
        return self._request(method='DELETE', endpoint=endpoint, json=body)


class YandexCloudNeuroSupportClient(BaseClient):
    """
    Клиент для работы с API через аутентификацию Yandex.Cloud.
    Использует Bearer IAM-токен и folder_id.
    """
    def __init__(
        self,
        auth_token: str,
        folder_id: str,
        service: str,
        product: str,
        base_url: str = "https://supportgpt.api.cloud.yandex.net"
    ):
        """
        Инициализирует клиент API для NeuroSupport в Yandex.Cloud.

        Args:
            auth_token: IAM-токен авторизации для аутентификации в Yandex.Cloud.
            folder_id: Идентификатор каталога в Yandex.Cloud.
            service: Идентификатор сервиса. Выдается после обработки заявки на подключение (обязательный).
            product: Идентификатор продукта. Выдается после обработки заявки на подключение (обязательный).
            base_url: Базовый URL API.
        """
        if not auth_token or not folder_id:
            raise AuthenticationError("`auth_token` и `folder_id` являются обязательными.")

        self.auth_token = auth_token
        self.folder_id = folder_id

        super().__init__(service=service, product=product, base_url=base_url)

    def _configure_auth(self):
        """
        Реализует настройку аутентификации с помощью Bearer IAM-токена.
        """
        self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})