from alembic_db import create_or_update_tables, create_default_user
import alembic_db
import pytest
import os


@pytest.fixture
def modify_global_variable():
    original_value = alembic_db.database_url
    alembic_db.database_url = "invalid_db_url"  # Change the global variable for the test
    yield
    alembic_db.database_url = original_value


def test_create_or_update_tables():
    create_or_update_tables()
    assert True


def test_create_or_update_tables_with_root_dir():
    create_or_update_tables(os.environ["PAIG_ROOT_DIR"])
    assert True


def test_create_or_update_tables_with_exception():
    with pytest.raises(SystemExit) as e:
        create_or_update_tables("invalid_tests_path")

    assert str(e.value)


def test_create_default_user():
    create_default_user()
    assert True
    create_default_user()


def test_create_default_user_with_exception(modify_global_variable):
    with pytest.raises(SystemExit) as e:
        create_default_user()
    assert str(e.value) is not None


