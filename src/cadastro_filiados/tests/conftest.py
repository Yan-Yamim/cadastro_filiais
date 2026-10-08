import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from testcontainers.community.postgres import PostgresContainer

from cadastro_filiados.app import app
from cadastro_filiados.database import get_session
from cadastro_filiados.models import table_registry


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16", driver="psycopg") as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        user = postgres.username
        password = postgres.password
        dbname = postgres.dbname

        url_sa = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"

        os.environ["DATABASE_URL"] = url_sa
        os.environ["POSTGRES_HOST"] = host
        os.environ["POSTGRES_PORT"] = str(port)
        os.environ["POSTGRES_USER"] = user
        os.environ["POSTGRES_PASSWORD"] = password
        os.environ["POSTGRES_DB"] = dbname

        yield postgres


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine(postgres_container):
    url = os.environ["DATABASE_URL"]

    _engine = create_async_engine(url, poolclass=NullPool)

    async with _engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    yield _engine

    async with _engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await _engine.dispose()


@pytest_asyncio.fixture(loop_scope="function")
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(loop_scope="function")
async def client(session):
    async def _get_test_session():
        yield session

    app.dependency_overrides[get_session] = _get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()