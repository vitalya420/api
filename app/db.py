from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import config


engine = create_async_engine(
    f'postgresql+asyncpg://{config["POSTGRES_USER"]}:{config["POSTGRES_PASSWORD"]}@'
    f'{config["POSTGRES_HOST"]}:{config["POSTGRES_PORT"]}/{config["POSTGRES_DB"]}'
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()
