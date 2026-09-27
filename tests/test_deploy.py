"""Check role isolation, config fallback and incremental SFTP copy."""

import importlib.util
import io
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("two_pi_deploy", ROOT / "deploy/deploy_two_pis.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class FakeSFTP:
    def __init__(self, home):
        self.home = Path(home)
        self.writes = []

    def __enter__(self): return self
    def __exit__(self, *_): pass
    def normalize(self, path): return str(self.home)
    def stat(self, path): return Path(path).stat()
    def mkdir(self, path): Path(path).mkdir()
    def open(self, path, mode): return Path(path).open(mode)
    def put(self, source, destination, confirm=True):
        shutil.copyfile(source, destination)
        self.writes.append(Path(destination))


class FakeSSH:
    def __init__(self, sftp): self.sftp = sftp; self.commands = []
    def __enter__(self): return self
    def __exit__(self, *_): pass
    def load_system_host_keys(self): pass
    def set_missing_host_key_policy(self, policy): pass
    def connect(self, host, **kwargs):
        assert host == "192.168.1.64"
        assert kwargs["username"] == "psk"
    def open_sftp(self): return self.sftp
    def exec_command(self, command, timeout):
        self.commands.append(command)
        output = io.BytesIO(b"started engine process 123\n")
        output.channel = types.SimpleNamespace(recv_exit_status=lambda: 0)
        return None, output, io.BytesIO()


class DeployTests(unittest.TestCase):
    def test_manifest_has_no_cross_pi_components(self):
        engine = {str(path) for path in script.manifest("engine")}
        presentation = {str(path) for path in script.manifest("presentation")}
        self.assertEqual(engine & presentation, {"SW/__init__.py", "deploy/manage_process.py", "deploy/install_service.py"})
        self.assertIn("SW/serve_engine.py", engine)
        self.assertIn("SW/serve_presentation.py", presentation)
        self.assertTrue(any(path.endswith("static/app.js") for path in presentation))
        self.assertFalse(any("FrontEnd" in path or "Vision" in path for path in engine))

    def test_missing_config_prompts_once_and_yaml_ip_overrides_host(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing.yaml"
            self.assertEqual(script.load_config(missing), {})
            session = {}
            with patch("builtins.input", side_effect=["192.168.1.64", "psk"]) as prompted, \
                    patch.object(script.getpass, "getpass", return_value="secret") as passwords:
                first = script.connection_info("engine", {}, session=session)
                self.assertEqual(first, ("192.168.1.64", 22, "psk", "secret"))
                self.assertEqual(script.connection_info("engine", {}, session=session), first)
                self.assertEqual(script.resolve_address("engine", {}, session=session), "192.168.1.64")
                self.assertEqual(prompted.call_count, 2)
                passwords.assert_called_once()
            self.assertEqual(script.connection_info("presentation", {}, dry_run=True)[0],
                             "<IP required for presentation>")
            config = Path(temp) / "config.yaml"
            config.write_text("engine: {}")
            fake_yaml = types.SimpleNamespace(safe_load=lambda _: {"engine": {
                "host": "named-engine", "ip": "192.168.1.64", "user": "psk", "password": "secret"}})
            with patch.dict(sys.modules, {"yaml": fake_yaml}):
                self.assertEqual(script.connection_info("engine", script.load_config(config)),
                                 ("192.168.1.64", 22, "psk", "secret"))

    def test_sftp_copy_is_incremental_and_keeps_unrelated_data(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            sftp = FakeSFTP(home)
            ssh = FakeSSH(sftp)
            fake_paramiko = types.SimpleNamespace(SSHClient=lambda: ssh, RejectPolicy=object)
            files = script.manifest("engine")
            data_dir = home / "dartscore-deploy/runtime"
            data_dir.mkdir(parents=True)
            (data_dir / "game.sqlite3").write_bytes(b"keep this game")
            with patch.dict(sys.modules, {"paramiko": fake_paramiko}), patch("sys.stdout", new_callable=io.StringIO):
                script.deploy("engine", ("192.168.1.64", 22, "psk", "secret"), files,
                              database_path="~/DartScore/runtime/game.sqlite3")
                self.assertEqual(len(sftp.writes), len(files))
                self.assertIn("manage_process.py", ssh.commands[0])
                self.assertIn("--bind 192.168.1.64", ssh.commands[0])
                self.assertNotIn("secret", ssh.commands[0])
                script.deploy("engine", ("192.168.1.64", 22, "psk", "secret"), files,
                              restart=False)
                self.assertEqual(len(sftp.writes), len(files))
                self.assertEqual(len(ssh.commands), 1)
            self.assertEqual((data_dir / "game.sqlite3").read_bytes(), b"keep this game")
            self.assertFalse((home / "dartscore-deploy/SW/Presentation").exists())

    def test_presentation_only_without_yaml_reuses_prompted_engine_address(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing.yaml"
            with patch("builtins.input", side_effect=["192.168.1.64", "192.168.1.51", ""]) as prompted, \
                    patch.object(script.getpass, "getpass", return_value="secret") as passwords, \
                    patch.object(script, "deploy") as deploy, patch("sys.stdout", new_callable=io.StringIO):
                script.main(["--config", str(missing), "--only", "presentation"])
            self.assertEqual(prompted.call_count, 3)
            passwords.assert_called_once()
            self.assertEqual(deploy.call_args.args[1], ("192.168.1.51", 22, "pi", "secret"))
            self.assertEqual(deploy.call_args.kwargs["engine_address"], "192.168.1.64")


if __name__ == "__main__":
    unittest.main()
