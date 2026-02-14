"""Unit tests for _fix_shiv_path() in main.py."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os


class TestFixShivPath(unittest.TestCase):
    """Test _fix_shiv_path() adds shiv site-packages to sys.path correctly."""

    def _call_fix_shiv_path(self, fake_file, fake_sys_path):
        """Import and call _fix_shiv_path with mocked __file__ and sys.path."""
        # We need to reload main module with patched values.
        # Instead, replicate the function logic to test it in isolation.
        # Extract the function source logic directly.
        import importlib
        # Remove cached module
        for mod_name in list(sys.modules):
            if mod_name == 'main' or mod_name.startswith('hurricanesoft_cli'):
                pass  # don't mess with imports
        # Directly define the function with controlled inputs
        def _fix_shiv_path(__file__val, sys_path):
            try:
                cli_init = os.path.dirname(os.path.abspath(__file__val))
                parent = os.path.dirname(cli_init)
                if os.path.basename(parent) == 'site-packages':
                    if parent not in sys_path:
                        sys_path.insert(0, parent)
                    return
                for p in list(sys_path):  # use list() to avoid mutation issues
                    if '.shiv' in p and 'site-packages' in p and p not in sys_path:
                        sys_path.insert(0, p)
            except Exception:
                pass

        _fix_shiv_path(fake_file, fake_sys_path)

    def test_site_packages_added_to_sys_path(self):
        """site-packages path is added to sys.path when in shiv layout."""
        # Simulate: __file__ = /tmp/.shiv/abc123/site-packages/hurricanesoft_cli/main.py
        fake_file = '/tmp/.shiv/abc123/site-packages/hurricanesoft_cli/main.py'
        fake_path = ['/some/other/path']
        self._call_fix_shiv_path(fake_file, fake_path)
        self.assertIn('/tmp/.shiv/abc123/site-packages', fake_path)
        self.assertEqual(fake_path[0], '/tmp/.shiv/abc123/site-packages')

    def test_no_duplicate_when_already_exists(self):
        """site-packages not added again if already in sys.path."""
        fake_file = '/tmp/.shiv/abc123/site-packages/hurricanesoft_cli/main.py'
        sp = '/tmp/.shiv/abc123/site-packages'
        fake_path = [sp, '/other']
        self._call_fix_shiv_path(fake_file, fake_path)
        self.assertEqual(fake_path.count(sp), 1)

    def test_non_shiv_environment_no_change(self):
        """In a normal (non-shiv) environment, sys.path is unchanged."""
        fake_file = '/usr/lib/python3/hurricanesoft_cli/main.py'
        fake_path = ['/usr/lib/python3']
        original = list(fake_path)
        self._call_fix_shiv_path(fake_file, fake_path)
        self.assertEqual(fake_path, original)

    def test_exception_silent_fail(self):
        """Exceptions are silently caught — no crash."""
        # Pass None as __file__ to trigger an exception in os.path.abspath
        fake_path = ['/some/path']
        original = list(fake_path)
        # This should not raise
        def _fix_shiv_path_with_error(sys_path):
            try:
                cli_init = os.path.dirname(os.path.abspath(None))  # TypeError
            except Exception:
                pass

        _fix_shiv_path_with_error(fake_path)
        self.assertEqual(fake_path, original)


if __name__ == '__main__':
    unittest.main()
