import uuid
from datetime import timedelta, datetime
from functools import wraps
from typing import Literal

from httpx import HTTPStatusError
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.vpn_server import VpnServerCrud
from src.schemas.response import AdminAuth, ClientSettings, ClientsSettings
from src.schemas.tariff import TariffSchema
from src.schemas.vpn_server import VpnServerSchema
from src.utils import common_request, CommonRequestError
from src.utils.common import create_vpn_url
from src.utils.vpn_server import update_cookies


class AuthError(Exception):
    def __init__(self, message):
        super().__init__(message)


class RequestError(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class ClientCreateError(Exception):
    def __init__(self, message):
        super().__init__(message)


class AuthRequestError(AuthError):
    def __init__(self, message):
        super().__init__(message)


async def __create_session(
    *, session: AsyncSession, crud: VpnServerCrud, url: str
) -> dict[str, str]:
    try:
        vpn_creds = await crud.get_one(session, url=url)
    except SQLAlchemyError as e:
        raise AuthError(f"Get vp server credentials failed: {e}")

    auth_settings = AdminAuth(
        username=vpn_creds.login, password=vpn_creds.password
    )
    resp = await common_request(
        method="POST",
        url=f"{url}/login",
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
            url = kwargs.get("url")
            session = kwargs.get("session")
            crud = kwargs.get("crud")
            logger.info(f"Session {url} expired. Create new")
            cookies = await __create_session(
                session=session, crud=crud, url=url
            )
            await update_cookies(
                session=session, crud=crud, url=url, cookies=cookies
            )

        return await func(*args, **kwargs)

    return wrapped


@__auth_if_need
async def __vpn_request(
    *,
    vpn_data: VpnServerSchema,
    method: Literal["POST", "GET"],
    url: str,
    route: str,
    headers: dict = None,
    json_: dict = None,
    request_timeout: float = 10,
    verify: bool = False,
) -> dict:
    response = await common_request(
        method=method,
        url=url + route,
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
    *,
    url: str,
    telegram_id: int,
    tariff: TariffSchema,
    vpn_data: VpnServerSchema,
    inbound_id: int = 1,
) -> str:
    days = datetime.now() + timedelta(days=tariff.days)
    expiry_time = datetime.timestamp(days) * 1000
    user_id = uuid.uuid4()

    user_setting = ClientSettings(
        id=user_id,
        tgId=str(telegram_id),
        email=str(telegram_id),
        expiryTime=int(expiry_time),
    )
    users_settings = ClientsSettings(clients=[user_setting])

    try:
        await __vpn_request(
            vpn_data=vpn_data,
            method="POST",
            url=url,
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
        url=url, user_id=user_id, telegram_id=telegram_id, vpn_data=vpn_data
    )
    logger.debug(
        f"Add client {user_id!r} (tg_id: {telegram_id}) "
        f"to VPN server with link: {user_link}"
    )
    return user_link
