from json import JSONDecodeError
from typing import Literal

from httpx import (
    TimeoutException,
    ConnectError,
    AsyncClient,
    Response,
    Cookies,
)
from loguru import logger


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class CommonRequestError(Exception):
    def __init__(self, message, data=None):
        self.data = data
        super().__init__(message)


async def common_request(
    *,
    method: Literal["POST", "GET"],
    url: str,
    headers: dict = None,
    json_: dict = None,
    request_timeout: float = 10,
    dispatch: bool = True,
    verify: bool = False,
    cookies: Cookies | dict[str, str] = None,
) -> dict | str | Response:
    def dispatch_response(response: Response):
        try:
            return response.json()
        except JSONDecodeError as e:
            logger.error(
                f"Got not jsonable response with body {response.text}"
            )
            raise CommonRequestError(str(e), response.text)

    try:
        async with AsyncClient(verify=verify, cookies=cookies) as client:
            resp = await client.request(
                method,
                url,
                headers=headers,
                json=json_,
                timeout=request_timeout,
            )
    except TimeoutException as err:
        logger.error(f"Timeout error on sending req to {url}. Reason: {err}")
        raise
    except ConnectError as err:
        logger.error(
            f"Connection error on sending req to {url}. Reason: {err}"
        )
        raise

    resp.raise_for_status()

    if dispatch:
        return dispatch_response(resp) if len(resp.text) else ""

    return resp
