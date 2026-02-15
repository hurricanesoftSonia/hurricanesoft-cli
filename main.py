#!/usr/bin/env python3
"""HurricaneSoft Unified CLI — hs command."""
import argparse
import sys
import os
import subprocess

# Ensure shiv/zipapp bundled site-packages are on sys.path.
# When running from a shiv archive, the hurricanesoft_cli package is importable
# but sibling packages (announcetool, msgtool, etc.) may not be if the shiv
# cache site-packages dir isn't explicitly in sys.path.
def _fix_shiv_path():
    """Add the shiv cache site-packages to sys.path if needed."""
    try:
        cli_init = os.path.dirname(os.path.abspath(__file__))
        # Walk up to find site-packages (shiv layout: .shiv/<hash>/site-packages/<pkg>/)
        parent = os.path.dirname(cli_init)
        if os.path.basename(parent) == 'site-packages':
            if parent not in sys.path:
                sys.path.insert(0, parent)
            return
        # Also check: maybe we're in a zip — look for .shiv in path
        for p in sys.path:
            if '.shiv' in p and 'site-packages' in p and p not in sys.path:
                sys.path.insert(0, p)
    except Exception:
        pass

_fix_shiv_path()

from hurricanesoft_cli import __version__

# Tool registry: name → (module, description)
TOOLS = {
    'mail':      ('mailtool.cli',      '📧 Email 工具'),
    'todo':      ('todotool.cli',      '📝 待辦事項'),
    'memo':      ('memotool.cli',      '📋 備忘錄'),
    'msg':       ('msgtool.cli',       '💬 內部訊息'),
    'account':   ('accountool.cli',    '💰 記帳工具'),
    'announce':  ('announcetool.cli',  '📢 公告系統'),
    'health':    ('healthtool.cli',    '🏥 系統監控'),
    'auth':      ('hurricanesoft_auth.cli', '🔐 LIDS 認證'),
    'contacthub': ('contacthub.cli',   '📞 聯絡人管理'),
}


def main():
    parser = argparse.ArgumentParser(
        prog='hs',
        description='🌀 HurricaneSoft 統一 CLI 工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_tools_help(),
    )
    parser.add_argument('--version', action='version',
                       version=f'hurricanesoft-cli v{__version__}')

    parser.add_argument('tool', nargs='?', help='工具名稱')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='工具參數')

    args = parser.parse_args()

    if not args.tool:
        parser.print_help()
        return

    tool = args.tool.lower()

    if tool == 'list':
        print_tools()
        return

    if tool == 'config':
        handle_config(args.args)
        return

    if tool == 'migrate':
        from hurricanesoft_cli.migrate import main as migrate_main
        sys.argv = ['hs migrate'] + args.args
        migrate_main()
        return

    if tool not in TOOLS:
        print(f"❌ 未知工具: {tool}")
        print(f"可用工具: {', '.join(sorted(TOOLS.keys()))}")
        return

    module_name, desc = TOOLS[tool]

    # Route to the tool's main()
    try:
        # Reconstruct sys.argv for the sub-tool
        sys.argv = [f'hs {tool}'] + args.args

        # Import and run
        mod = __import__(module_name, fromlist=['main'])
        mod.main()
    except ImportError as e:
        print(f"❌ 無法載入 {tool}: {e}")
        print(f"請確認 {module_name.split('.')[0]} 已安裝")
    except SystemExit:
        pass  # Tools may call sys.exit


def format_tools_help():
    lines = ["\n可用工具:"]
    for name, (_, desc) in sorted(TOOLS.items()):
        lines.append(f"  {name:<12} {desc}")
    lines.append(f"\n範例:")
    lines.append(f"  hs mail fetch          # 收信")
    lines.append(f"  hs todo list           # 列出待辦")
    lines.append(f"  hs msg inbox           # 查看訊息")
    lines.append(f"  hs health check        # 健康檢查")
    lines.append(f"  hs auth login          # LIDS 登入")
    lines.append(f"  hs list                # 列出所有工具")
    return '\n'.join(lines)


def print_tools():
    print("🌀 HurricaneSoft 工具列表:")
    print()
    for name, (module, desc) in sorted(TOOLS.items()):
        # Check if available
        try:
            __import__(module.split('.')[0])
            status = '✅'
        except ImportError:
            status = '❌'
        print(f"  {status} {name:<12} {desc}")


def handle_config(args):
    """Handle hs config subcommands."""
    from hurricanesoft_cli import config

    if not args or args[0] == 'show':
        config.show_config()
    elif args[0] == 'init':
        config.init_config(interactive=True)
    elif args[0] == 'get' and len(args) >= 2:
        val = config.get(args[1])
        if val is not None:
            print(val)
        else:
            print(f"❌ Key not found: {args[1]}")
    elif args[0] == 'set' and len(args) >= 3:
        val = config.set_value(args[1], ' '.join(args[2:]))
        print(f"✅ {args[1]} = {val}")
    else:
        print("用法:")
        print("  hs config show           顯示設定")
        print("  hs config init           設定精靈")
        print("  hs config get <key>      取得設定值")
        print("  hs config set <key> <v>  設定值")
        print("  key 格式: database.pg_host, lids.use_lids, etc.")


if __name__ == '__main__':
    main()
