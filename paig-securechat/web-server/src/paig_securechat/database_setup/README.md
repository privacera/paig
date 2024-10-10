# Secure Chat Database Setup
Secure Chat Supports database setup and migration using Alembic.
Secure Chat provides ability for users to setup various database types like Postgres, MySQL, SQLite etc.

## Contents
- [How to Setup Database Configuration](#setup_configure)
- [How to Setup/Update Database Manually](#setup_database)
- [Developers Guide](#developers_guide)


### How to Setup Database Configuration <a name="setup_configure"></a>

1. Configure database URL in configuration file as per your environment.
   You have to follow below format to configure database URL.
   Format should be as follows:
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
      url: sqlite+aiosqlite:///secure_chat.db
    ```
   
   **Note** - Secure chat uses **Async** SQLAlchemy to connect to the database.Database driver should support async operations.

### How to Setup/Update Database Manually <a name="setup_database"></a>

1. Configure database URL as mentioned above
2. Download reposiotry and change directory to web-server/src/paig_securechat
3. Run below command to set up database
    ```bash
    python database_setup/database_standalone.py --secure_chat_deployment dev|prod --config_path <path to config folder>
    
   ```
   One Such example is:
   ```bash
    python database_setup/database_standalone.py --secure_chat_deployment dev --config_path configs
    
   ```

**Note** - You can skip above steps as well and directly start the web server. Web server will automatically create/update the tables in the database.

### Developers Guide<a name="developers_guide"></a>
If developers wants to add new tables or modify existing tables, they can take note of following commands:-

1. Create migration run below command
    ```bash
    alembic -c database_setup/alembic.ini revision --autogenerate -m "Your migration message here"
    ```

2. To apply latest or all pending migration on Database
    ```bash
    alembic -c database_setup/alembic.ini upgrade head # apply latest migration or all pending migrations.
    ```

3. To apply migrations till any specific migration.
    ```bash
    alembic -c database_setup/alembic.ini upgrade <revision_id> # apply all pending migrations till this migration.
    ```

4. Revert last applied migration on database
    ```bash
    alembic -c database_setup/alembic.ini downgrade -1
    ```

5. Revert migrations till any specific migration
   ```bash
    alembic -c database_setup/alembic.ini downgrade <revision_id> 
    ```

6. Revert all applied migrations.(Don't use this command )
   ```bash
    alembic -c database_setup/alembic.ini downgrade base # This commend will revert all applied migrations and bring the database back to the state it was
    ```