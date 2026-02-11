"""Database factory — returns SQLite or PostgreSQL connection based on config."""
import os


def get_db_config():
    """Get DB config from unified config or env vars."""
    try:
        from hurricanesoft_cli.config import load_config
        config = load_config()
        return config.get('database', {})
    except ImportError:
        return {
            'type': os.environ.get('HS_DB_TYPE', 'sqlite'),
            'pg_host': os.environ.get('HS_PG_HOST', ''),
            'pg_port': int(os.environ.get('HS_PG_PORT', '5432')),
            'pg_database': os.environ.get('HS_PG_DB', ''),
            'pg_user': os.environ.get('HS_PG_USER', ''),
            'pg_password': os.environ.get('HS_PG_PASSWORD', ''),
        }


def get_pg_conn(config=None):
    """Get a PostgreSQL connection."""
    if config is None:
        config = get_db_config()
    try:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(
            host=config.get('pg_host', 'localhost'),
            port=config.get('pg_port', 5432),
            database=config.get('pg_database', ''),
            user=config.get('pg_user', ''),
            password=config.get('pg_password', ''),
        )
        conn.autocommit = True
        return conn
    except ImportError:
        raise RuntimeError("psycopg2 not installed. pip install psycopg2-binary")


def use_postgres():
    """Check if PostgreSQL is configured."""
    config = get_db_config()
    return config.get('type') == 'postgresql' and config.get('pg_host')


def get_connection(tool_name, sqlite_init_fn=None, pg_init_fn=None):
    """Get a database connection for a tool.

    Args:
        tool_name: Tool name (for SQLite file naming)
        sqlite_init_fn: Function to init SQLite DB (takes optional path)
        pg_init_fn: Function to init PostgreSQL DB (takes optional config)

    Returns:
        (connection, db_type) tuple
    """
    if use_postgres() and pg_init_fn:
        config = get_db_config()
        conn = pg_init_fn(config)
        return conn, 'postgresql'
    elif sqlite_init_fn:
        conn = sqlite_init_fn()
        return conn, 'sqlite'
    else:
        raise RuntimeError(f"No database backend available for {tool_name}")
