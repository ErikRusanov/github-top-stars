import requests
from requests import RequestException

from app.core import settings
from app.core.logging_config import logger


def send_request_to_yandex_cloud_function(data: dict = None, params: dict = None) -> dict:
    url = settings.YCF_URL
    try:
        resp = requests.post(
            url=url,
            json=data or {},
            params=params or {}
        )
        return resp.json()
    except RequestException as e:
        logger.error(f"Can't parse data from {url}. Error: {e}")

    return dict()
