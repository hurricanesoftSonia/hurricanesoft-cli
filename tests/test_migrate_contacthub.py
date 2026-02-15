#!/usr/bin/env python3
"""測試 migrate.py 的 table mapping 修復和 ContactHub 整合。"""
import unittest
import sys
import os

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from migrate import TOOL_TABLES
from main import TOOLS


class TestMigrateContactHub(unittest.TestCase):
    """測試 migrate table mapping + ContactHub 整合修復。"""

    def test_tools_registry_has_contacthub(self):
        """測試 main.py TOOLS registry 包含 contacthub。"""
        self.assertIn('contacthub', TOOLS)
        module, desc = TOOLS['contacthub']
        self.assertEqual(module, 'contacthub.cli')
        self.assertEqual(desc, '📞 聯絡人管理')

    def test_contacthub_table_mapping(self):
        """測試 ContactHub 的 table mapping 設定。"""
        self.assertIn('contacthub', TOOL_TABLES)
        
        contacthub_config = TOOL_TABLES['contacthub']
        self.assertEqual(contacthub_config['module'], 'contacthub')
        self.assertEqual(contacthub_config['prefix'], 'contact')
        self.assertEqual(contacthub_config['db_file'], 'contacts.db')
        
        # 檢查 table mapping
        expected_tables = {
            'users': 'contact_users',
            'contacts': 'contact_contacts',
            'groups': 'contact_groups',
            'group_members': 'contact_group_members',
            'import_logs': 'contact_import_logs',
        }
        self.assertEqual(contacthub_config['table_map'], expected_tables)

    def test_todo_table_mapping_fixed(self):
        """測試 todo table mapping 修復 (audit_log vs todo_history)。"""
        todo_config = TOOL_TABLES['todo']
        table_map = todo_config['table_map']
        
        # 確認使用 audit_log，不是 todo_history
        self.assertIn('audit_log', table_map)
        self.assertEqual(table_map['audit_log'], 'todo_audit_log')
        self.assertNotIn('todo_history', table_map)

    def test_account_table_mapping_fixed(self):
        """測試 account table mapping 修復 (entries vs transactions)。"""
        account_config = TOOL_TABLES['account']
        table_map = account_config['table_map']
        
        # 確認使用 entries，不是 transactions
        self.assertIn('entries', table_map)
        self.assertEqual(table_map['entries'], 'acct_entries')
        self.assertNotIn('transactions', table_map)
        
        # 確認 reminders 有正確的 prefix
        self.assertEqual(table_map['reminders'], 'acct_reminders')

    def test_announce_table_mapping_fixed(self):
        """測試 announce table mapping 修復 (recipients prefix)。"""
        announce_config = TOOL_TABLES['announce']
        table_map = announce_config['table_map']
        
        # 確認 recipients 有正確的 prefix
        self.assertEqual(table_map['recipients'], 'ann_recipients')

    def test_all_tools_have_consistent_prefixes(self):
        """測試所有工具的 table prefix 一致性。"""
        for tool_name, config in TOOL_TABLES.items():
            prefix = config['prefix']
            for pg_table in config['table_map'].values():
                if not pg_table.startswith(prefix + '_'):
                    self.fail(f"{tool_name} 工具的表 {pg_table} 沒有使用正確的 prefix {prefix}_")

    def test_module_consistency(self):
        """測試 TOOLS registry 和 TOOL_TABLES 的模組一致性。"""
        # 檢查所有在 TOOL_TABLES 中有對應 migrate 設定的工具
        for tool_name in TOOL_TABLES:
            if tool_name in TOOLS:
                tool_module = TOOLS[tool_name][0]  # 'contacthub.cli'
                migrate_module = TOOL_TABLES[tool_name]['module']  # 'contacthub'
                
                # 確認模組名稱一致（去掉 .cli 後綴）
                expected_module = tool_module.replace('.cli', '')
                self.assertEqual(migrate_module, expected_module,
                               f"{tool_name}: TOOLS 有 {tool_module}, TOOL_TABLES 有 {migrate_module}")


if __name__ == '__main__':
    unittest.main()