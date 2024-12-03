import asyncio
import os
import sys
from logging.config import fileConfig

import loguru
from alembic.script import ScriptDirectory
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# for ez enum sync
import alembic_postgresql_enum  # noqa

from src.models import Base
from src.utils.settings import get_settings


def check_revision_fluency():
    """Check all migrations have different down_revision
    on same branch_labels (check issues with multiple children migration
    for a single one on same branch)"""
    no_check = context.get_x_argument(as_dictionary=True).get("no-check")
    if no_check:
        return loguru.logger.info("down_revision check step skipped")

    script_dir = ScriptDirectory("alembic")
    for rev in script_dir.walk_revisions():
        if len(rev.nextrev) <= 1:
            continue
        assert_revs = script_dir.get_revisions(list(rev.nextrev))
        diff_branches = {tuple(rev_.branch_labels) for rev_ in assert_revs}

        if len(diff_branches) != len(assert_revs):
            loguru.logger.error(
                f"Same 'down_revision' {rev.revision} in files: \n- "
                + "\n- ".join(
                    [rev_.path.split(os.sep)[-1] for rev_ in assert_revs]
                )
            )
            loguru.logger.warning(
                "Seems like a migration issue, check file. "
                'For force migrate run alembic with "-x=no-check=1"'
            )

            sys.exit(-1)


DB_URL = get_settings().db.driver_url
check_revision_fluency()

# Add all models to the Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", DB_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    def do_run_migrations(conn_):
        context.configure(
            connection=conn_,
            target_metadata=target_metadata,
            dialect_opts={"paramstyle": "named"},
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DB_URL
    connectable = async_engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
