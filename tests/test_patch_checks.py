"""Three-way contracts; released artifact tests run via upstream-refresh.py."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SECURITY = Path(__file__).resolve().parents[1]/'image/security'
sys.path.insert(0, str(SECURITY))
import patch_checks as checks


class PatchChecks(unittest.TestCase):
    def test_settingregistry_reviewed_affected_fixed_drift(self):
        checks.setting_registry((SECURITY/'settingregistry-source.ts').read_bytes())
        with self.assertRaisesRegex(RuntimeError, 'RETIRE.*settingregistry.patch'):
            checks.setting_registry((SECURITY/'settingregistry-patched.ts').read_bytes())
        with self.assertRaisesRegex(RuntimeError, 'RETIRE'):
            checks.setting_registry(b'new upstream implementation', behavior_fixed=True)
        with self.assertRaisesRegex(RuntimeError, 'REVIEW'):
            checks.setting_registry(b'new unsupported implementation')

    def test_fast_uri_resolution(self):
        checks.fast_uri_lock('"fast-uri@npm:^3.0.1":\n  version: 3.1.8\n')
        with self.assertRaisesRegex(RuntimeError, 'RETIRE.*fast-uri'):
            checks.fast_uri_lock('"fast-uri@npm:^3.0.1":\n  version: 3.1.9\n')
        with self.assertRaisesRegex(RuntimeError, 'REVIEW'):
            checks.fast_uri_lock('"fast-uri@npm:^4.0.0":\n  version: 4.2.3\n')

    def test_solver_release_contract_and_snapshot(self):
        checks.solver_snapshot((SECURITY/'solver-source.tar.gz').read_bytes())
        checks.solver_release(['py-rattler<0.27.0a0,>=0.26.0'])
        with self.assertRaisesRegex(RuntimeError, 'RETIRE.*solver dev snapshot'):
            checks.solver_release(['py-rattler>=0.28.1,<0.29'])
        with self.assertRaisesRegex(RuntimeError, 'REVIEW'):
            checks.solver_release(['unfamiliar-solver>=1'])
        with self.assertRaisesRegex(RuntimeError, 'REVIEW'):
            checks.solver_snapshot(b'unsupported source')

    def test_editor_actual_bytes_not_only_version(self):
        r=checks.reviewed()['editor_dependencies']['shell-quote']
        checks.editor_dependency('shell-quote',r['version'],r['sha256'],'fixed-code')
        with self.assertRaisesRegex(RuntimeError, 'RETIRE.*shell-quote'):
            checks.editor_dependency('shell-quote','1.12.0','fixed-code','fixed-code')
        with self.assertRaisesRegex(RuntimeError, 'REVIEW'):
            checks.editor_dependency('shell-quote',r['version'],'different-code','fixed-code')

    def test_global_npm_actual_code(self):
        r=checks.reviewed()['global_npm']
        checks.global_npm(r['version'],r['sha256'],'fixed')
        with self.assertRaisesRegex(RuntimeError,'RETIRE.*npm'):
            checks.global_npm('12.2.1','fixed','fixed')
        with self.assertRaisesRegex(RuntimeError,'REVIEW.*npm'):
            checks.global_npm(r['version'],'unknown','fixed')

    def test_editor_native_node(self):
        checks.editor_node('v22.21.1','127',False)
        with self.assertRaisesRegex(RuntimeError, 'RETIRE.*Node'):
            checks.editor_node('v22.23.4','127',True)
        with self.assertRaisesRegex(RuntimeError, 'REVIEW'):
            checks.editor_node('v22.23.4','127',False)
        with self.assertRaisesRegex(RuntimeError, 'REVIEW'):
            checks.editor_node('v24.0.0','137',True)

    def test_nbclassic_partial_and_complete_retirement(self):
        for standalone,bundle in [(True,False),(False,True),(True,True)]:
            with self.assertRaisesRegex(RuntimeError,'RETIRE'):
                checks.nbclassic(Path('/unused'),standalone,bundle)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError,'REVIEW'):
                checks.nbclassic(Path(d))

    def test_pip_code_tree_states(self):
        # Small fixtures exercise failure-before-mutation; the actual released
        # trees are checked by upstream-refresh and the real image build.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); expected={}
            for name in ['msgpack','urllib3']:
                (root/name).mkdir();(root/name/'__init__.py').write_text('old = True\n')
                expected['pip_'+name]=checks.python_tree(root/name)
                expected['pip_'+name+'_fixed']='fixed'
            with patch.object(checks,'reviewed',return_value=expected):
                checks.pip_vendor(root)
                expected['pip_msgpack_fixed']=expected['pip_msgpack']
                with self.assertRaisesRegex(RuntimeError,'RETIRE.*msgpack'):
                    checks.pip_vendor(root)
                expected['pip_msgpack_fixed']='fixed'
                (root/'msgpack/__init__.py').write_text('changed = True\n')
                with self.assertRaisesRegex(RuntimeError,'REVIEW.*msgpack'):
                    checks.pip_vendor(root)


if __name__ == '__main__':
    unittest.main()
