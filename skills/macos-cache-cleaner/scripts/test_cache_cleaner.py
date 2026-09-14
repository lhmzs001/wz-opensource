#!/usr/bin/env python3
"""Tests for macos-cache-cleaner using an isolated fake home."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("cache_cleaner.py")
CONFIRM_TOKEN = "DELETE-CACHE-ONLY"


class CacheCleanerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name)
        self.environment = {**os.environ, "CACHE_CLEANER_HOME": str(self.home), "PATH": "/usr/bin:/bin"}

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_file(self, relative_path: str, content: bytes = b"cache") -> Path:
        path = self.home / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ("/usr/bin/python3", str(SCRIPT), *arguments),
            check=False,
            capture_output=True,
            text=True,
            env=self.environment,
        )

    def test_scan_reports_candidates_without_deleting(self) -> None:
        cache_file = self.create_file(".cache/tool/cache.bin", b"x" * 1024)
        result = self.run_script("--mode", "scan", "--categories", "dev-caches", "--json")
        self.assertEqual(result.returncode, 0)
        self.assertIn(str(self.home / ".cache"), result.stdout)
        self.assertTrue(cache_file.exists())

    def test_clean_requires_exact_confirmation_token(self) -> None:
        cache_file = self.create_file(".npm/_cacache/index", b"cache")
        result = self.run_script("--mode", "clean", "--categories", "dev-caches")
        self.assertEqual(result.returncode, 2)
        self.assertTrue(cache_file.exists())

    def test_clean_removes_cache_contents_but_keeps_root(self) -> None:
        cache_root = self.home / "Library/Caches/go-build"
        self.create_file("Library/Caches/go-build/aa/object", b"cache")
        result = self.run_script(
            "--mode",
            "clean",
            "--categories",
            "dev-caches",
            "--confirm",
            CONFIRM_TOKEN,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(cache_root.exists())
        self.assertEqual(list(cache_root.iterdir()), [])

    def test_log_clean_removes_rotated_log_and_preserves_active_log(self) -> None:
        rotated = self.create_file("Library/Logs/JetBrains/idea.log.1", b"old")
        active = self.create_file("Library/Logs/JetBrains/idea.log", b"active")
        result = self.run_script(
            "--mode",
            "clean",
            "--categories",
            "user-logs",
            "--confirm",
            CONFIRM_TOKEN,
        )
        self.assertEqual(result.returncode, 0)
        self.assertFalse(rotated.exists())
        self.assertTrue(active.exists())

    def test_protected_documents_are_never_candidates(self) -> None:
        protected = self.create_file("Documents/project/build.log.1", b"important")
        result = self.run_script("--mode", "scan", "--categories", "user-logs", "--json")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(str(protected), result.stdout)
        self.assertTrue(protected.exists())


if __name__ == "__main__":
    unittest.main()
