import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('runtime_cache_cleanup', Path(__file__).parents[1] / 'scripts/runtime_cache_cleanup.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CleanupTests(unittest.TestCase):
    def test_only_old_metadata_json_is_removed_and_dry_run_preserves_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);home=root/'workspace/task/codex-home';home.mkdir(parents=True)
            (home/'config.toml').write_text('synthetic=true')
            old=home/'cache/remote_plugin_catalog/catalog.json';old.parent.mkdir(parents=True);old.write_text('{}');os.utime(old,(1,1))
            young=old.with_name('recent.json');young.write_text('{}')
            record=home/'state_5.sqlite';record.write_text('retain')
            history=home/'sessions/turn.jsonl';history.parent.mkdir();history.write_text('retain')
            credential=home/'auth.json';credential.write_text('synthetic-retain')
            other=home/'cache/customer-data.json';other.write_text('retain');os.utime(other,(1,1))
            self.assertEqual(module.clean(root,now=172800)['eligible_files'],1);self.assertTrue(old.exists())
            self.assertEqual(module.clean(root,execute=True,now=172800)['removed_files'],1)
            self.assertFalse(old.exists())
            for path in (young,record,history,credential,other):self.assertTrue(path.exists())

    def test_symlinked_cache_and_unmanaged_directories_are_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);outside=root/'outside';outside.mkdir();file=outside/'catalog.json';file.write_text('{}');os.utime(file,(1,1))
            home=root/'workspace/task/codex-home';home.mkdir(parents=True);(home/'config.toml').write_text('synthetic=true')
            (home/'cache').symlink_to(outside,target_is_directory=True)
            self.assertEqual(module.clean(root,execute=True,now=172800)['removed_files'],0)
            self.assertTrue(file.exists())
