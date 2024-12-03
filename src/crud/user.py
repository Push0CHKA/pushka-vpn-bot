from functools import cache

from src.crud.common import CRUDBase
from src.models.user import User
from src.schemas.user import UserSchema, UserSchemaCreate


class UserCrud(CRUDBase[User, UserSchema, UserSchemaCreate]): ...


@cache
def get_user_crud() -> UserCrud:
    return UserCrud(User)
