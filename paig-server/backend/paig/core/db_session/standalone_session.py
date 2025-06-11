import logging
from typing import List, Dict

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, select, func, update, insert

from core import config

logger = logging.getLogger(__name__)
cnf = config.load_config_file()
database_url = cnf["database"]["url"]

# Create engine factory
def get_engine():
    return create_async_engine(
        url=database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        echo=False,
        future=True
    )

# Session factory
def get_session():
    engine = get_engine()
    return async_sessionmaker(engine, expire_on_commit=False)()

# Reflect table by name
async def reflect_table(table_name: str):
    engine = get_engine()
    metadata = MetaData()
    async with engine.connect() as conn:
        await conn.run_sync(metadata.reflect)
    return metadata.tables.get(table_name)

# Execute a generic query
async def execute_query(query):
    session = get_session()
    async with session:
        result = await session.execute(query)
        return result.fetchall()

# Get counts grouped by a field
async def get_counts_group_by(table_name: str, field_name: str):
    try:
        table = await reflect_table(table_name)
        if table is None:
            raise ValueError(f"Table '{table_name}' does not exist")

        if field_name not in table.columns:
            raise ValueError(f"Field '{field_name}' does not exist in table '{table_name}'")

        query = select(table.c[field_name], func.count().label('count')).group_by(table.c[field_name])
        return await execute_query(query)
    except Exception as e:
        logger.error(f"Error in get_counts_group_by: {e}")
        return []

# Count how many unique values a field has
async def get_field_counts(table_name: str, field_name: str):
    return len(await get_counts_group_by(table_name, field_name))

# Get tenant UUID from model
async def get_tenant_uuid():
    global Tenant
    if 'Tenant' not in globals():
        from api.user.database.db_models.user_model import Tenant
    tenants = await execute_query(select(Tenant.uuid))
    if tenants:
        return tenants[0][0]

# Execute an update query
async def execute_update(query):
    session = get_session()
    async with session.begin():
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

# Update multiple fields in a table row
async def update_table_fields(
    table_name: str,
    updates: dict,
    condition_field: str,
    condition_value
):
    try:
        table = await reflect_table(table_name)
        if table is None:
            raise ValueError(f"Table '{table_name}' does not exist")

        for field in updates:
            if field not in table.columns:
                raise ValueError(f"Field '{field}' does not exist in table '{table_name}'")

        if condition_field not in table.columns:
            raise ValueError(f"Condition field '{condition_field}' does not exist")

        query = (
            update(table)
            .where(table.c[condition_field] == condition_value)
            .values(updates)
        )
        return await execute_update(query)

    except Exception as e:
        logger.error(f"Error in update_table_fields: {e}")
        return f"Error: {e}"

# Bulk insert data into a table
async def bulk_insert_into_table(table_name: str, records: List[Dict[str, any]]):
    BATCH_SIZE = 400
    if not records:
        return "No records provided for insertion"

    try:
        table = await reflect_table(table_name)
        if table is None:
            return f"Error: Table '{table_name}' does not exist"

        total_inserted = 0
        session = get_session()
        async with session.begin():
            for i in range(0, len(records), BATCH_SIZE):
                batch = records[i : i + BATCH_SIZE]
                await session.execute(insert(table), batch)
                total_inserted += len(batch)

        return f"{total_inserted} rows inserted successfully"

    except Exception as e:
        logger.error(f"Error in bulk_insert_into_table: {e}")
        return f"Error: {e}"
