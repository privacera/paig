import pytest
import pytest_asyncio
from faker import Faker
import random
from app.db_models import User
from core.factory.database_initiator import BaseOperations
import database_setup
from unittest.mock import patch

fake = Faker()


class TestBaseRepository:
    @pytest_asyncio.fixture
    async def repository(self, db_session):
        return BaseOperations(model=User, db_session=db_session)

    @pytest.mark.asyncio
    async def test_get_all(self, repository):
        await repository.create(self._user_data_generator())
        users = await repository.get_all()
        assert len(users) == 1
        users = await repository.get_all(columns=["user_id"])
        assert len(users) == 1

    @pytest.mark.asyncio
    async def test_get_count_with_filter(self, repository):
        await repository.create( {
            "user_id": random.randrange(0, 100000, 3),
            "email_id": fake.email(),
            "user_name": "test1",
        })
        await repository.create({
            "user_id": random.randrange(0, 100000, 3),
            "email_id": fake.email(),
            "user_name": "test2",
        })
        filters = {"user_name": "test1"}
        count = await repository.get_count_with_filter(filters)
        assert count == 1

    @pytest.mark.asyncio
    async def test_get_by(self, repository):
        await repository.create({
            "user_id": random.randrange(0, 100000, 3),
            "email_id": fake.email(),
            "user_name": "test1",
        })
        await repository.create({
            "user_id": random.randrange(0, 100000, 3),
            "email_id": fake.email(),
            "user_name": "test2",
        })
        filters = {"user_name": "test1"}
        user = await repository.get_by(filters)
        assert user[0].user_name == "test1"
        user = await repository.get_by(filters, unique=True)
        assert user.user_name == "test1"

    def _user_data_generator(self):
        return {
            "user_id": random.randrange(0, 100000, 3),
            "email_id": fake.email(),
            "user_name": fake.user_name(),
        }

    def test_db_setup(self):
        with patch('core.config.load_config_file') as mock_get_data:
            mock_get_data.return_value = {
                "database": {
                    "url": "sqlite+aiosqlite:///tests/test.db"
                }
            }
            ret = database_setup.create_or_update_tables()
            assert ret is None
