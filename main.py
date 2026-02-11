#!/usr/bin/env python3
"""HurricaneSoft Unified CLI — hs command."""
import argparse
import sys
import os
import subprocess

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


if __name__ == '__main__':
    main()
