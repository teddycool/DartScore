"""The restart helper only targets exact user-owned DartScore processes."""

import importlib.util
import io
import signal
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("manage_process", ROOT / "deploy/manage_process.py")
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class ProcessTests(unittest.TestCase):
    def test_missing_game_database_leaves_old_process_running(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(manager, "DEPLOY", Path(temp)), patch.object(manager, "stop_old") as stop:
                with patch("sys.argv", ["manage_process.py", "engine", "--bind", "engine.example",
                                        "--database", str(Path(temp) / "missing.db")]):
                    with self.assertRaisesRegex(RuntimeError, "database missing"):
                        manager.main()
                stop.assert_not_called()

    def test_stop_sends_term_only_to_discovered_processes(self):
        with patch.object(manager, "owned_processes", side_effect=[[42, 43], [], []]), \
                patch.object(manager.os, "kill") as kill, patch("sys.stdout", new_callable=io.StringIO):
            manager.stop_old("engine")
        self.assertEqual(kill.call_count, 2)
        kill.assert_any_call(42, signal.SIGTERM)
        kill.assert_any_call(43, signal.SIGTERM)


if __name__ == "__main__":
    unittest.main()
