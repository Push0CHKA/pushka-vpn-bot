from functools import cache

from src.crud.common import CRUDBase
from src.models.vpn_server import VpnServer
from src.schemas.vpn_server import VpnServerSchema, VpnServerSchemaCreate


class VpnServerCrud(
    CRUDBase[VpnServer, VpnServerSchema, VpnServerSchemaCreate]
): ...


@cache
def get_vpn_server_crud() -> VpnServerCrud:
    return VpnServerCrud(VpnServer)
