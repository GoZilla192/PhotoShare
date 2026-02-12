import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from app.models import Base
import app.models
from app.core.settings import Settings


app_settings = Settings()
config = context.config

config.set_main_option("sqlalchemy.url", app_settings.database_url)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


def do_run_migration(connection):
    context.configure(
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        connection=connection,
        target_metadata=target_metadata,

    )
    
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(app_settings.database_url, future=True)
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migration)


asyncio.run(run_migrations_online())