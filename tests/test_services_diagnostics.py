"""Exercise service generation and bounded redacted reports without Pi hardware."""

import importlib.util
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deploy"))

import collect_diagnostics as diagnostics
import install_service as installer
import manage_process as manager


class ServicesDiagnosticsTests(unittest.TestCase):
    def test_unit_content_uses_existing_database_and_engine_url(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(installer, "DEPLOY", Path(temp)):
                engine = installer.unit_text("engine", "192.168.1.64", "", "/home/psk/DartScore/runtime/game.sqlite3")
                presentation = installer.unit_text("presentation", "", "http://192.168.1.64:8765", "")
        self.assertIn("--host 192.168.1.64", engine)
        self.assertIn("--db /home/psk/DartScore/runtime/game.sqlite3", engine)
        self.assertIn("--engine-url http://192.168.1.64:8765", presentation)
        for unit in (engine, presentation):
            self.assertIn("Restart=on-failure", unit)
            self.assertIn("WantedBy=default.target", unit)

    def test_installer_refuses_missing_linger_without_stopping_old_process(self):
        with tempfile.TemporaryDirectory() as temp:
            deploy = Path(temp)
            program = deploy / "SW/serve_presentation.py"
            program.parent.mkdir(parents=True)
            program.write_text("# stub")
            completed = types.SimpleNamespace(stdout="no\n", returncode=0)
            with patch.object(installer, "DEPLOY", deploy), \
                    patch.object(installer, "run", return_value=completed), \
                    patch.object(installer, "stop_old") as stopped:
                with self.assertRaisesRegex(RuntimeError, "enable-linger"):
                    installer.install("presentation", "", "http://192.168.1.64:8765", "")
                stopped.assert_not_called()

    def test_manager_uses_service_restart_instead_of_unmanaged_process(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            unit = home / ".config/systemd/user/dartscore-engine.service"
            unit.parent.mkdir(parents=True)
            unit.write_text("[Service]\n")
            with patch.object(manager, "HOME", home), patch.object(manager, "stop_old") as stop, \
                    patch.object(manager.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)) as run, \
                    patch("sys.argv", ["manage_process.py", "engine"]), patch("sys.stdout", new_callable=io.StringIO):
                manager.main()
                stop.assert_not_called()
                self.assertEqual(run.call_args.args[0], ("systemctl", "--user", "restart", "dartscore-engine.service"))

    def test_diagnostics_bounds_output_and_masks_credentials(self):
        content = b"password=secret token: abc\n" + b"x" * (diagnostics.MAX_BYTES + 30)
        stdout = io.BytesIO(content)
        stdout.channel = types.SimpleNamespace(recv_exit_status=lambda: 0)
        stderr = io.BytesIO(b"")
        ssh = types.SimpleNamespace(exec_command=lambda *_args, **_kwargs: (None, stdout, stderr))
        result = diagnostics.remote(ssh, ["journalctl", "--user"])
        self.assertNotIn("secret", result["output"])
        self.assertNotIn("abc", result["output"])
        self.assertIn("[truncated]", result["output"])


if __name__ == "__main__":
    unittest.main()
