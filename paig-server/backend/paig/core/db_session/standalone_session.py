# This module provides a standalone async session for database operations
import logging
from typing import List, Dict

from core import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, select, func, update, insert
from api.user.database.db_models.user_model import Tenant

logger = logging.getLogger(__name__)
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


# Function to execute an update query
async def execute_update(query):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            await session.commit()
            return result.rowcount  # Return the number of affected rows


# Function to update multiple fields in one go
async def update_table_fields(
    table_name: str,
    updates: dict,
    condition_field: str,
    condition_value
):
    """
    Update multiple fields in a table.

    :param table_name: Name of the table
    :param updates: Dictionary of field names and their new values
    :param condition_field: Field to filter rows
    :param condition_value: Value to filter rows
    :return: Number of rows updated or error message
    """
    try:
        async with engine.connect() as conn:
            metadata = MetaData()
            # Reflect the database schema asynchronously
            await conn.run_sync(metadata.reflect)

            if table_name not in metadata.tables:
                raise ValueError(f"Table '{table_name}' does not exist")

            table = metadata.tables[table_name]

            # Validate that all update fields exist in the table
            for field in updates:
                if field not in table.columns:
                    raise ValueError(f"Field '{field}' does not exist in table '{table_name}'")

            if condition_field not in table.columns:
                raise ValueError(f"Condition field '{condition_field}' does not exist in table '{table_name}'")

            # Construct the update query
            query = (
                update(table)
                .where(table.c[condition_field] == condition_value)
                .values(updates)  # Pass the updates dictionary
            )
            # Execute the update query
            return await execute_update(query)
    except Exception as e:
        return f"Error: {e}"


async def bulk_insert_into_table(table_name: str, records: List[Dict[str, any]]):
    """
    Bulk inserts records into a table in batches using a single AsyncSession.

    :param table_name: Name of the table
    :param records: List of dictionaries containing field names and values
    :return: Number of records inserted or error message
    """
    BATCH_SIZE = 400
    if not records:
        return "No records provided for insertion"

    try:
        async with engine.connect() as conn:  # Use engine connection for reflection
            metadata = MetaData()
            await conn.run_sync(metadata.reflect)

            if table_name not in metadata.tables:
                return f"Error: Table '{table_name}' does not exist"

            table = metadata.tables[table_name]

            total_inserted = 0

            async with async_session() as session:  # Single session for everything
                async with session.begin():  # Use session.begin() for transaction safety
                    for i in range(0, len(records), BATCH_SIZE):
                        batch = records[i : i + BATCH_SIZE]
                        await session.execute(insert(table), batch)
                        total_inserted += len(batch)

            return f"{total_inserted} rows inserted successfully"

    except Exception as e:
        logger.error(f"Error: {e}")
