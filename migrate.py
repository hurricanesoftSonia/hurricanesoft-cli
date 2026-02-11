#!/usr/bin/env python3
"""SQLite → PostgreSQL 資料遷移工具。

Usage:
    hs migrate --tool todo --sqlite-path /path/to/todo.db
    hs migrate --tool all
    hs migrate --dry-run --tool msg
"""
import sqlite3
import os
import sys
import json
import argparse


TOOL_TABLES = {
    'todo': {
        'module': 'todotool',
        'prefix': 'todo',
        'tables': ['users', 'todos', 'audit_log'],
        'db_file': 'todo.db',
    },
    'memo': {
        'module': 'memotool',
        'prefix': 'memo',
        'tables': ['users', 'memos'],
        'db_file': 'memo.db',
    },
    'account': {
        'module': 'accountool',
        'prefix': 'acct',
        'tables': ['users', 'categories', 'entries'],
        'db_file': 'accounts.db',
    },
    'announce': {
        'module': 'announcetool',
        'prefix': 'ann',
        'tables': ['users', 'contacts', 'announcements', 'acks'],
        'db_file': 'announce.db',
    },
    'msg': {
        'module': 'msgtool',
        'prefix': 'msg',
        'tables': ['users', 'messages', 'mentions'],
        'db_file': 'msg.db',
    },
}


def get_pg_conn():
    """Get PG connection from unified config."""
    try:
        from hurricanesoft_cli.config import load_config
        config = load_config()
        db_config = config.get('database', {})
    except ImportError:
        db_config = {}

    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(
        host=db_config.get('pg_host', os.environ.get('HS_PG_HOST', 'localhost')),
        port=db_config.get('pg_port', int(os.environ.get('HS_PG_PORT', '5432'))),
        database=db_config.get('pg_database', os.environ.get('HS_PG_DB', '')),
        user=db_config.get('pg_user', os.environ.get('HS_PG_USER', '')),
        password=db_config.get('pg_password', os.environ.get('HS_PG_PASSWORD', '')),
    )
    conn.autocommit = True
    return conn


def find_sqlite_db(tool_name, custom_path=None):
    """Find SQLite DB file for a tool."""
    info = TOOL_TABLES[tool_name]
    if custom_path:
        return custom_path

    # Search common locations
    candidates = [
        os.path.join(os.getcwd(), info['module'], info['db_file']),
        os.path.join(os.path.expanduser('~/.hurricanesoft/data'), info['db_file']),
        os.path.join(os.getcwd(), info['db_file']),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def migrate_table(sqlite_conn, pg_conn, sqlite_table, pg_table, dry_run=False):
    """Migrate a single table from SQLite to PostgreSQL."""
    cur = sqlite_conn.cursor()
    cur.execute(f"SELECT * FROM {sqlite_table}")
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    if not rows:
        print(f"  📭 {sqlite_table} → {pg_table}: 空的，跳過")
        return 0

    if dry_run:
        print(f"  📋 {sqlite_table} → {pg_table}: {len(rows)} 筆（dry run）")
        return len(rows)

    pg_cur = pg_conn.cursor()

    # Filter out 'id' column (let PG auto-generate SERIAL)
    non_id_cols = [c for c in columns if c != 'id']
    col_indices = [columns.index(c) for c in non_id_cols]

    placeholders = ', '.join(['%s'] * len(non_id_cols))
    col_names = ', '.join(non_id_cols)
    insert_sql = f"INSERT INTO {pg_table} ({col_names}) VALUES ({placeholders})"

    count = 0
    for row in rows:
        values = tuple(row[i] for i in col_indices)
        try:
            pg_cur.execute(insert_sql, values)
            count += 1
        except Exception as e:
            print(f"    ⚠️ 跳過: {e}")

    print(f"  ✅ {sqlite_table} → {pg_table}: {count}/{len(rows)} 筆")
    return count


def migrate_tool(tool_name, sqlite_path=None, dry_run=False):
    """Migrate all tables for a tool."""
    info = TOOL_TABLES[tool_name]
    db_path = find_sqlite_db(tool_name, sqlite_path)

    if not db_path:
        print(f"❌ 找不到 {tool_name} 的 SQLite DB")
        return False

    print(f"\n🔄 遷移 {tool_name} ({db_path})")
    print(f"{'─' * 50}")

    # Init PG tables first
    if not dry_run:
        pg_conn = get_pg_conn()
        # Import and run init_db for PG
        try:
            mod = __import__(f'{info["module"]}.db_pg', fromlist=['init_db'])
            mod.init_db()
            print(f"  ✅ PG tables 初始化完成")
        except Exception as e:
            print(f"  ⚠️ PG init: {e}")
    else:
        pg_conn = None

    # Open SQLite
    sqlite_conn = sqlite3.connect(db_path)
    sqlite_conn.row_factory = sqlite3.Row

    total = 0
    for table in info['tables']:
        pg_table = f"{info['prefix']}_{table}"
        try:
            count = migrate_table(sqlite_conn, pg_conn, table, pg_table, dry_run)
            total += count
        except Exception as e:
            print(f"  ❌ {table}: {e}")

    sqlite_conn.close()
    if pg_conn:
        pg_conn.close()

    print(f"  📊 總計: {total} 筆")
    return True


def main():
    parser = argparse.ArgumentParser(prog='hs migrate',
                                   description='SQLite → PostgreSQL 資料遷移')
    parser.add_argument('--tool', required=True,
                       help=f'工具名稱 ({", ".join(TOOL_TABLES.keys())}, all)')
    parser.add_argument('--sqlite-path', help='SQLite DB 路徑（自動偵測）')
    parser.add_argument('--dry-run', action='store_true', help='只顯示不實際遷移')
    args = parser.parse_args()

    if args.tool == 'all':
        tools = list(TOOL_TABLES.keys())
    elif args.tool in TOOL_TABLES:
        tools = [args.tool]
    else:
        print(f"❌ 未知工具: {args.tool}")
        print(f"可用: {', '.join(TOOL_TABLES.keys())}, all")
        return

    print("🚀 HurricaneSoft SQLite → PostgreSQL 遷移工具")
    if args.dry_run:
        print("⚠️ DRY RUN 模式 — 不會實際寫入")

    for tool in tools:
        migrate_tool(tool, args.sqlite_path, args.dry_run)

    print("\n✅ 遷移完成！")


if __name__ == '__main__':
    main()
