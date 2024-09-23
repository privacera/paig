# PAIG Database Setup
Paig Supports database setup and migration using Alembic. 
Paig provides the ability for users to set up various database types like Postgres, MySQL, SQLite, etc.



!!! tip "This section is optional"

    PAIG creates a database schema for you when you first run the application. If you want to customize the database schema, you can use the Alembic migration tool to create and manage database migrations.


### How to Setup Database Configuration <a name="setup_configure"></a>

1. Configure the database URL in the configuration file as per your environment
   You have to follow the below format to configure the database URL. Format should be as follows:
   ```yaml
   dialect+driver://username:password@host:port/database
   ```
   If you are using Postgres :-
   ```yaml
    database:
      url: postgresql+asyncpg://<username>:<password>@<host>:<port>/<database_name>
    ```
   If you are using sqlite :-
    ```yaml
    database:
      url: sqlite+aiosqlite:///db/database.db
    ```

    **Note** - Paig uses **Async** SQLAlchemy to connect to the database.Database driver should support async operations

### Create and apply migrations for new Tables<a name="add_tables"></a>
1. Import the newly created models in the `alembic_db/env.py` file

    Example:
    ```bash
     from <service_name>.database.db_models import <model_file_name>
    ```
   
2. Create migration run below command
    ```bash
    alembic -c alembic_db/alembic.ini revision --autogenerate -m "Your migration message here"
    ```
3. To apply latest or all pending migration on Database
    ```bash
    alembic -c alembic_db/alembic.ini upgrade head # apply latest migration or all pending migrations.
    ```

### Developers Guide<a name="developers_guide"></a>
If developers want to add new tables or modify existing tables, they can take note of the following commands:-

1. Import the newly created models in the `alembic_db/env.py` file
   
    Example:
    ```bash
     from <service_name>.database.db_models import <model_file_name>
    ```

2. Create migration run below command
    ```bash
    alembic -c alembic_db/alembic.ini revision --autogenerate -m "Your migration message here"
    ```

3. To apply latest or all pending migration on Database
    ```bash
    alembic -c alembic_db/alembic.ini upgrade head # apply latest migration or all pending migrations.
    ```

4. To apply migrations till any specific migration
    ```bash
    alembic -c alembic_db/alembic.ini upgrade <revision_id> # apply all pending migrations till this migration.
    ```

5. Revert last applied migration on database
    ```bash
    alembic -c alembic_db/alembic.ini downgrade -1
    ```

6. Revert migrations till any specific migration
    ```bash
    alembic -c alembic_db/alembic.ini downgrade <revision_id>
    ```

7. Revert all applied migrations.(Don't use this command )
    ```bash
    alembic -c alembic_db/alembic.ini downgrade base # This commend will revert all applied migrations and bring the database back to the state it was
    ```