import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from scripts.diagnose_resolve import PROBE, diagnose, positive_timeout


class ProbeTests(unittest.TestCase):
    def test_only_expected_read_calls(self):
        calls = []

        class Resolve:
            def GetProjectManager(self):
                calls.append('manager')
                return object()

            def GetProductName(self):
                calls.append('product')
                return 'DaVinci Resolve Studio'

            def GetVersion(self):
                calls.append('version')
                return [21, 1, 2, 10, '']

            def GetVersionString(self):
                calls.append('version_string')
                return '21.1.2.10'

        from types import SimpleNamespace
        from io import StringIO
        for instance, expected in [(Resolve(), 'ok'), (None, 'unreachable')]:
            output = StringIO()
            api = SimpleNamespace(scriptapp=lambda name: instance if name == 'Resolve' else None)
            with patch.dict('sys.modules', DaVinciResolveScript=api), patch('sys.stdout', output):
                with self.assertRaises(SystemExit) as exit_info:
                    exec(PROBE, {})
            self.assertEqual(json.loads(output.getvalue())['status'], expected)
            self.assertEqual(exit_info.exception.code, 0 if expected == 'ok' else 1)
        self.assertEqual(calls, ['manager', 'product', 'version', 'version_string'])

    @patch('scripts.diagnose_resolve.sys.platform', 'darwin')
    @patch('scripts.diagnose_resolve.plistlib.load', return_value={'CFBundleShortVersionString': '21.1.2'})
    @patch.object(Path, 'open')
    @patch.object(Path, 'is_file', return_value=True)
    def test_runtime_failures(self, *_):
        cases = [
            (subprocess.TimeoutExpired('probe', 1), None, 'timeout'),
            (PermissionError(), None, 'runtime_failed'),
            (None, subprocess.CompletedProcess([], -11, '', 'private data'), 'invalid_response'),
            (None, subprocess.CompletedProcess([], 0, '[]', ''), 'invalid_response'),
        ]
        for error, response, expected in cases:
            with self.subTest(expected=expected), patch('scripts.diagnose_resolve.subprocess.run', side_effect=error, return_value=response):
                result = diagnose(Path('/fake.app'), 1)
                self.assertEqual(result['status'], expected)
                self.assertNotIn('private data', json.dumps(result))

    def test_timeout_validation(self):
        import argparse
        for value in ['0', '-1', '61', 'nan', 'inf']:
            with self.assertRaises(argparse.ArgumentTypeError):
                positive_timeout(value)
        self.assertEqual(positive_timeout('0.1'), 0.1)


if __name__ == '__main__':
    unittest.main()
