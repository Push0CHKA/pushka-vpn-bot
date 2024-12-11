from functools import wraps
from typing import Literal

from httpx import HTTPStatusError
from loguru import logger

from src.crud.vpn_server import get_vpn_server_crud
from src.database.database import AsyncSessionLocal
from src.schemas.response import AdminAuth, ClientSettings, ClientsSettings
from src.schemas.vpn_server import VpnServerSchema
from src.utils import common_request, CommonRequestError
from src.utils.common import create_vpn_url
from src.utils.vpn_server import update_cookies


class RequestError(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class AuthError(RequestError):
    def __init__(self, message):
        super().__init__(message)


class ClientError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ClientCreateError(ClientError):
    def __init__(self, message):
        super().__init__(message)


class ClientUpdateError(ClientError):
    def __init__(self, message):
        super().__init__(message)


async def __create_session(*, vpn_data: VpnServerSchema) -> dict[str, str]:
    auth_settings = AdminAuth(
        username=vpn_data.login, password=vpn_data.password
    )
    resp = await common_request(
        method="POST",
        url=f"{vpn_data.url}/login",
        json_=auth_settings.model_dump(),
        dispatch=False,
    )
    return dict(resp.cookies)


def __auth_if_need(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPStatusError:
            vpn_data = kwargs.get("vpn_data")
            logger.info(f"Session {vpn_data.url} expired. Create new...")
            cookies = await __create_session(vpn_data=vpn_data)
            async with AsyncSessionLocal() as session:
                await update_cookies(
                    session=session,
                    crud=get_vpn_server_crud(),
                    url=vpn_data.url,
                    cookies=cookies,
                )

        return await func(*args, **kwargs)

    return wrapped


@__auth_if_need
async def __vpn_request(
    *,
    vpn_data: VpnServerSchema,
    method: Literal["POST", "GET"],
    route: str,
    headers: dict = None,
    json_: dict = None,
    request_timeout: float = 10,
    verify: bool = False,
) -> dict:
    response = await common_request(
        method=method,
        url=vpn_data.url + route,
        headers=headers,
        json_=json_,
        request_timeout=request_timeout,
        dispatch=True,
        verify=verify,
        cookies=vpn_data.cookies,
    )

    if response.get("success", False) is False:
        logger.error(f"Response status error: {response}")
        raise CommonRequestError(response)

    return response


async def add_vpn_client(
    *, vpn_data: VpnServerSchema, settings: ClientSettings, inbound_id: int = 1
) -> str:
    users_settings = ClientsSettings(clients=[settings])

    try:
        await __vpn_request(
            vpn_data=vpn_data,
            method="POST",
            route="/panel/api/inbounds/addClient",
            json_={
                "id": inbound_id,
                "settings": users_settings.model_dump_json(),
            },
        )
    except HTTPStatusError as e:
        raise ClientCreateError(e)
    except CommonRequestError as e:
        raise ClientCreateError(e)

    user_link = create_vpn_url(
        url=vpn_data.url,
        user_id=settings.id,
        telegram_id=int(settings.tgId),
        vpn_data=vpn_data,
    )
    logger.debug(
        f"Add client {settings.id!r} (tg_id: {settings.tgId}) "
        f"to VPN server with link: {user_link}"
    )
    return user_link


async def update_vpn_client(
    *, vpn_data: VpnServerSchema, settings: ClientSettings, inbound_id: int = 1
) -> None:
    users_settings = ClientsSettings(clients=[settings])

    try:
        await __vpn_request(
            vpn_data=vpn_data,
            method="POST",
            route=f"/panel/api/inbounds/updateClient/{settings.id}",
            json_={
                "id": inbound_id,
                "settings": users_settings.model_dump_json(),
            },
        )
    except HTTPStatusError as e:
        raise ClientUpdateError(e)
    except CommonRequestError as e:
        raise ClientUpdateError(e)

    logger.debug(
        f"Update client {settings.id!r} (tg_id: {settings.tgId}) settings"
    )
