from functools import cache

from src.crud.common import CRUDBase
from src.models import UserLink
from src.models.user import User
from src.schemas.user import (
    UserSchema,
    UserSchemaCreate,
    UserWithLinksSchema,
    UserWithTransactionsSchema,
    UserLinkSchema,
    UserLinkSchemaCreate,
    UserLinkWithUserSchema,
)


class UserCrud(CRUDBase[User, UserSchema, UserSchemaCreate]): ...


class UserWithLinksCrud(
    CRUDBase[User, UserWithLinksSchema, UserSchemaCreate]
): ...


class UserWithTransactionsCrud(
    CRUDBase[User, UserWithTransactionsSchema, UserSchemaCreate]
): ...


@cache
def get_user_crud() -> UserCrud:
    return UserCrud(User)


@cache
def get_user_with_links_crud() -> UserWithLinksCrud:
    return UserWithLinksCrud(User)


@cache
def get_user_with_transactions_crud() -> UserWithTransactionsCrud:
    return UserWithTransactionsCrud(User)


class UserLinkCrud(
    CRUDBase[UserLink, UserLinkSchema, UserLinkSchemaCreate]
): ...


class UserLinkWithUserCrud(
    CRUDBase[UserLink, UserLinkWithUserSchema, UserLinkSchemaCreate]
): ...


@cache
def get_user_link_crud() -> UserLinkCrud:
    return UserLinkCrud(UserLink)


@cache
def get_user_link_with_user_crud() -> UserLinkWithUserCrud:
    return UserLinkWithUserCrud(UserLink)
