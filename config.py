"""HurricaneSoft 統一設定檔管理。

設定檔位置: ~/.hurricanesoft/config.json
所有工具共用一份設定。
"""
import json
import os

CONFIG_DIR = os.path.expanduser('~/.hurricanesoft')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

DEFAULT_CONFIG = {
    'user': {
        'username': '',
        'display_name': '',
    },
    'lids': {
        'server': 'http://host.docker.internal:8073',
        'client_id': '',
        'client_secret': '',
        'use_lids': False,
    },
    'database': {
        'type': 'sqlite',  # sqlite or postgresql
        'sqlite_dir': '~/.hurricanesoft/data',
        'pg_host': '',
        'pg_port': 5432,
        'pg_database': '',
        'pg_user': '',
        'pg_password': '',
    },
    'mail': {
        'pop3_host': '',
        'pop3_port': 995,
        'smtp_host': '',
        'smtp_port': 465,
        'email': '',
        'password': '',
        'signature': '',
    },
    'msg': {
        'server': '',  # MsgTool server URL for client mode
    },
    'health': {
        'alert_email': [],
        'alert_telegram_token': '',
        'alert_telegram_chat_id': '',
    },
}


def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data_dir = os.path.expanduser(DEFAULT_CONFIG['database']['sqlite_dir'])
    os.makedirs(data_dir, exist_ok=True)


def load_config():
    """Load config, create default if not exists."""
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            stored = json.load(f)
        # Merge with defaults (add new keys)
        config = _deep_merge(DEFAULT_CONFIG, stored)
        return config
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save config to file."""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    os.chmod(CONFIG_FILE, 0o600)  # Restrict permissions


def get(key, default=None):
    """Get a config value by dot-separated key. e.g. 'database.pg_host'"""
    config = load_config()
    parts = key.split('.')
    val = config
    for p in parts:
        if isinstance(val, dict) and p in val:
            val = val[p]
        else:
            return default
    return val


def set_value(key, value):
    """Set a config value by dot-separated key."""
    config = load_config()
    parts = key.split('.')
    d = config
    for p in parts[:-1]:
        if p not in d:
            d[p] = {}
        d = d[p]
    # Auto-convert types
    if isinstance(value, str):
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
    d[parts[-1]] = value
    save_config(config)
    return value


def init_config(interactive=False):
    """Initialize config, optionally interactive."""
    config = load_config()
    if interactive:
        print("🌀 HurricaneSoft 設定精靈")
        print("─" * 40)
        config['user']['username'] = input(f"用戶名 [{config['user']['username']}]: ").strip() or config['user']['username']
        config['user']['display_name'] = input(f"顯示名稱 [{config['user']['display_name']}]: ").strip() or config['user']['display_name']

        use_lids = input(f"使用 LIDS 認證? (y/n) [{config['lids']['use_lids']}]: ").strip().lower()
        if use_lids in ('y', 'yes'):
            config['lids']['use_lids'] = True
            config['lids']['server'] = input(f"LIDS Server [{config['lids']['server']}]: ").strip() or config['lids']['server']

        db_type = input(f"資料庫類型 (sqlite/postgresql) [{config['database']['type']}]: ").strip() or config['database']['type']
        config['database']['type'] = db_type
        if db_type == 'postgresql':
            config['database']['pg_host'] = input(f"PG Host [{config['database']['pg_host']}]: ").strip() or config['database']['pg_host']
            config['database']['pg_port'] = int(input(f"PG Port [{config['database']['pg_port']}]: ").strip() or config['database']['pg_port'])
            config['database']['pg_database'] = input(f"PG Database [{config['database']['pg_database']}]: ").strip() or config['database']['pg_database']
            config['database']['pg_user'] = input(f"PG User [{config['database']['pg_user']}]: ").strip() or config['database']['pg_user']
            config['database']['pg_password'] = input(f"PG Password: ").strip() or config['database']['pg_password']

    save_config(config)
    print(f"✅ 設定已儲存到 {CONFIG_FILE}")
    return config


def show_config():
    """Print current config (mask passwords)."""
    config = load_config()
    masked = _mask_sensitive(config)
    print(json.dumps(masked, indent=2, ensure_ascii=False))


def _deep_merge(base, override):
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _mask_sensitive(d, sensitive_keys=('password', 'secret', 'token')):
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _mask_sensitive(v, sensitive_keys)
        elif any(s in k.lower() for s in sensitive_keys) and v:
            result[k] = '***' + str(v)[-4:] if len(str(v)) > 4 else '****'
        else:
            result[k] = v
    return result
