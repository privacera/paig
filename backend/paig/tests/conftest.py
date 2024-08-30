import os
import uuid
from functools import partial

os.environ["PAIG_DEPLOYMENT"] = "test"
os.environ["CONFIG_PATH"] = "conf"
os.environ["EXT_CONFIG_PATH"] = "tests/test_conf"
os.environ["LOG_PATH"] = "tests/logs"
import pytest
import pytest_asyncio
from core import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.db_session import Base
import asyncio
from typing import Generator
import shutil
from core.db_session.session import set_session_context
from core import constants

cnf = config.load_config_file()
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
os.environ["PAIG_ROOT_DIR"] = ROOT_DIR

# setting MODE as test
constants.MODE = "test"


@pytest.mark.asyncio(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def set_context_session():
    session_id = uuid.uuid4()
    set_session_context(session_id=str(session_id))


@pytest_asyncio.fixture(scope="function")
async def db_session():
    database_url = cnf['database']['url']
    async_engine = create_async_engine(database_url)
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


def pytest_collection_modifyitems(session, config, items):
    # Custom sorting function to move specific tests to the end
    total_cases = len(items)
    print(f"Total test cases: {total_cases}")

    def get_order(item, total_cases):
        # print(item.nodeid)
        if item.nodeid.startswith("tests/authz"):
            print(item.nodeid)
            return total_cases  # High order to run last
        return 0

    custom_get_order = partial(get_order, total_cases=total_cases)

    items.sort(key=custom_get_order)


def pytest_sessionstart(session):
    os.makedirs('tests/logs', exist_ok=True)


def pytest_sessionfinish(session, exitstatus):
    try:
        os.remove('tests/test.db')
        shutil.rmtree('tests/logs')
        shutil.rmtree('tests/api/shield/audit_spool_dir')
        shutil.rmtree('tests/api/shield/workdir')
        shutil.rmtree('tests/api/shield/test_directory_path')
    except:
        pass
