import shutil
from os import environ
environ['SECURE_CHAT_DEPLOYMENT'] = environ["APP_ENV"] = 'test'
environ['DEBUG'] = "False"
environ['CONFIG_PATH'] = 'configs'
environ['OPENAI_API_KEY'] = "This is test open api key"
environ["DISABLE_PAIG_SHIELD_PLUGIN"] = str(True)
import asyncio
import os
from typing import Generator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core import config
from app.db_models import Base
import core.database.transactional as transactional
from core import constants


# Override the config to use the test database
cnf = config.load_config_file()
config.Config = cnf
config.Config['database']['url'] = "sqlite+aiosqlite:///tests/test.db"
config.Config['AI_applications']['sales_model']['vectordb']['index_path'] = "tests/test_index_path"
config.Config['AI_applications']['sales_model']['vectordb']['data_path'] = "tests/test_data_path"



@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
@pytest.mark.asyncio
async def db_session() -> AsyncSession:
    async_engine = create_async_engine(config.Config['database']['url'] )
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        transactional.session = s
        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


def pytest_sessionstart(session):
    os.makedirs('tests/test_index_path', exist_ok=True)
    os.makedirs('tests/test_data_path', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('templates/static', exist_ok=True)


def pytest_sessionfinish(session, exitstatus):
    try:
        os.remove('tests/test.db')
        shutil.rmtree('tests/test_index_path')
        shutil.rmtree('tests/test_data_path')
        shutil.rmtree('templates')
        shutil.rmtree('securechat')
        constants.MODE = 'docker'
    except:
        pass
