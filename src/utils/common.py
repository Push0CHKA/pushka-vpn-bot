import re
import uuid

from src.schemas.vpn_server import VpnServerSchema

REGULAR_COMP = re.compile(r"((?<=[a-z\d])[A-Z]|(?!^)[A-Z](?=[a-z]))")


def camel_to_snake(camel_string):
    return REGULAR_COMP.sub(r"_\1", camel_string).lower()


def extract_ip(url: str) -> str | None:
    pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    match = re.search(pattern, url)

    if match:
        return match.group(0)
    else:
        return None


def create_vpn_url(
    *,
    url: str,
    telegram_id: int,
    user_id: uuid.UUID,
    vpn_data: VpnServerSchema,
):
    ip_addr = extract_ip(url)
    return (
        f"vless://{str(user_id)}@{ip_addr}:{vpn_data.port}?type={vpn_data.type}"
        f"&security={vpn_data.security}&pbk={vpn_data.pbk}"
        f"&fp={vpn_data.fp}&sni={vpn_data.sni}&sid={vpn_data.sid}"
        f"&spx={vpn_data.spx}&flow={vpn_data.flow}{telegram_id}"
    )
