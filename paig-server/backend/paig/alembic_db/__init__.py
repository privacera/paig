import sys
from alembic.config import Config
from alembic import command
import os
from core.config import load_config_file, load_default_ai_config
from api.user.database.db_models import User
from api.governance.database.db_models.ai_app_model import AIApplicationModel
from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel
from core.utils import generate_unique_identifier_key
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select
import asyncio

config = load_config_file()
database_url = config["database"]["url"]

def create_or_update_tables(root_dir: str = None):
    try:
        if "sqlite+aiosqlite" in database_url:
            db_location = database_url.split("sqlite+aiosqlite:///")[-1]
            if not os.path.exists(db_location):
                os.makedirs(os.path.dirname(db_location), exist_ok=True)
        script_location = "alembic_db"
        if root_dir is not None:
            script_location = os.path.join(root_dir, 'alembic_db')
        alembic_cfg = Config(os.path.join(script_location, 'alembic.ini'))
        alembic_cfg.set_main_option('script_location', script_location)
        command.upgrade(alembic_cfg, 'head')
        print("Tables creation or changes applied on database.")
    except Exception as e:
        print(f"An error occurred during tables creation on database: {e}")
        sys.exit(f"An error occurred during tables creation on database: {e}")


async def check_and_create_default_user():
    security_config = config["security"]

    engine = None
    try:
        engine = create_async_engine(url=database_url)

        class SyncSession(Session):
            def get_bind(self, mapper=None, clause=None, **kwargs):
                return engine.sync_engine

        async_session = sessionmaker(
            class_=AsyncSession,
            sync_session_class=SyncSession,
            expire_on_commit=False
        )
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(User).filter_by(username="admin"))
                user = result.scalars().first()
                if user:
                    print("Default User already exists")
                    return
                default_user = User(
                    status=1,
                    username="admin",
                    first_name="Admin",
                    password=security_config['basic_auth']['secret'],
                    is_tenant_owner=True
                )
                session.add(default_user)
                await session.commit()
                print("Default User created successfully")
    except Exception as e:
        print(f"An error occurred during default user creation: {e}")
        sys.exit(f"An error occurred during default user creation: {e}")
    finally:
        if engine:
            await engine.dispose()


async def check_and_create_default_ai_application():
    default_ai_app = load_default_ai_config()

    engine = None
    try:
        engine = create_async_engine(url=database_url)

        class SyncSession(Session):
            def get_bind(self, mapper=None, clause=None, **kwargs):
                return engine.sync_engine

        async_session = sessionmaker(
            class_=AsyncSession,
            sync_session_class=SyncSession,
            expire_on_commit=False
        )
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(AIApplicationModel).filter_by())
                user = result.scalars().first()
                if user:
                    print("At least one application already exists")
                    return
                ai_application = default_ai_app.get('aiApplication')
                default_app = AIApplicationModel(
                    status=ai_application.get("status"),
                    name=ai_application.get("name"),
                    description=ai_application.get("description"),
                    application_key=generate_unique_identifier_key(),
                    vector_dbs=''
                )
                session.add(default_app)
                await session.flush()
                ai_application_config = default_ai_app.get('configs')
                default_config = AIApplicationConfigModel(
                    status=ai_application_config.get("status", 1),
                    allowed_users=ai_application_config.get("allowedUsers"),
                    allowed_groups=ai_application_config.get("allowedGroups"),
                    allowed_roles=ai_application_config.get("allowedRoles"),
                    denied_users=ai_application_config.get("deniedUsers"),
                    denied_groups=ai_application_config.get("deniedGroups"),
                    denied_roles=ai_application_config.get("deniedRoles"),
                    application_id=default_app.id
                )
                session.add(default_config)
                # update policies
                ai_application_policies = default_ai_app.get('policies')
                for policy in ai_application_policies:
                    default_policy = AIApplicationPolicyModel(
                        name=policy.get("name", ""),
                        status=policy.get("status", 1),
                        description=policy.get("description", ""),
                        users=",".join(policy.get("users", [])),
                        groups=",".join(policy.get("groups", [])),
                        roles=",".join(policy.get("roles", [])),
                        tags=",".join(policy.get("tags", [])),
                        prompt=policy.get("prompt", "ALLOW"),
                        reply=policy.get("reply", "ALLOW"),
                        enriched_prompt=policy.get("enrichedPrompt", "ALLOW"),
                        application_id=default_app.id
                    )
                    session.add(default_policy)
                await session.commit()
                print("Default Application created successfully")
    except Exception as e:
        print(f"An error occurred during default application creation: {e}")
        sys.exit(f"An error occurred during default application creation: {e}")
    finally:
        if engine:
            await engine.dispose()


def create_default_user():
    asyncio.run(check_and_create_default_user())


def create_default_ai_application():
    asyncio.run(check_and_create_default_ai_application())


def create_default_user_and_ai_application():
    if not config.get("skip_default_user_creation", False):
        create_default_user()
    if not config.get("skip_default_application_creation", False):
        create_default_ai_application()
