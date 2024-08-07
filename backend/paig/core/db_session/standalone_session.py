# This module provides a standalone async session for database operations
from core import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, select, func
from api.user.database.db_models.user_model import Tenant

# Load config
cnf = config.load_config_file()
database_url = cnf["database"]["url"]

# Create async engine
engine = create_async_engine(url=database_url)

# Define async session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def execute_query(query):
    async with async_session() as session:
        result = await session.execute(query)
        return result.fetchall()


async def get_counts_group_by(table_name: str, field_name: str):
    try:
        async with engine.connect() as conn:
            metadata = MetaData()
            # Reflect the database schema asynchronously
            await conn.run_sync(metadata.reflect)

            if table_name not in metadata.tables:
                raise ValueError(f"Table '{table_name}' does not exist")

            table = metadata.tables[table_name]

            if field_name not in table.columns:
                raise ValueError(f"Field '{field_name}' does not exist in table '{table_name}'")

            query = select(table.c[field_name], func.count().label('count')).group_by(table.c[field_name])
            return await execute_query(query)
    except:
        return []


async def get_field_counts(table_name: str, field_name: str):
    return len(await get_counts_group_by(table_name, field_name))


async def get_tenant_uuid():
    tenants = await execute_query(select(Tenant.uuid))
    if tenants:
        return tenants[0][0]


