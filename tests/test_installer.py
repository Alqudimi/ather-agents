import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ather_installer", ROOT / "scripts" / "install-opencode-v2.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerSafetyTests(unittest.TestCase):
    def test_manifest_and_agent_checksums_are_valid(self):
        agents = installer.validate_package()
        self.assertEqual(len(agents), 621)

    def test_install_refuses_when_v2_cli_is_missing_without_project_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            home = root / "home"
            project.mkdir()
            home.mkdir()
            with patch.dict(os.environ, {"HOME": str(home)}), patch.object(installer.shutil, "which", return_value=None):
                args = type("Args", (), {"project": str(project), "no_depth_2": False})()
                with self.assertRaisesRegex(RuntimeError, "Install OpenCode v2 yourself first"):
                    installer.install(args)
            self.assertFalse((project / ".opencode").exists())
            self.assertFalse((project / "opencode.json").exists())
            self.assertFalse((home / ".local" / "state").exists())

    def test_uninstall_restores_project_and_never_removes_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            home = root / "home"
            cli = home / ".opencode" / "bin" / "opencode"
            project.mkdir()
            cli.parent.mkdir(parents=True)
            cli.write_text("#!/bin/sh\n[ \"$1\" = \"--version\" ] && echo 2.0.32\n", encoding="utf-8")
            cli.chmod(0o755)
            with patch.dict(os.environ, {"HOME": str(home)}):
                args = type("Args", (), {"project": str(project), "no_depth_2": False})()
                installer.install(args)
                self.assertTrue((project / ".opencode" / "agents" / "orchestrator.md").is_file())
                installer.uninstall(args)
            self.assertTrue(cli.is_file())
            self.assertFalse((project / ".opencode" / "agents" / "orchestrator.md").exists())
            self.assertFalse((project / "opencode.json").exists())


if __name__ == "__main__":
    unittest.main()
