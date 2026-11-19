#!/usr/bin/env python3
"""test_confluence.py - offline regression tests for scripts/confluence.py.

No network is used. The suite covers the safety-critical pure functions
(credentials, env files, version messages, backups, hashing, error hints)
and the two CLI paths that must work against an unreachable tenant:
'create --dry-run' must build and report the payload without a request,
and every command must fail closed when credentials are missing.

Usage:
    python3 scripts/test_confluence.py        # summary
    python3 scripts/test_confluence.py -v     # verbose

Exit codes: 0 all green, 1 failures.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from confluence import (  # noqa: E402
    ApiError,
    Config,
    ConfigError,
    backup_page,
    load_env_file,
    page_body,
    page_version,
    sha256,
    unified_diff,
    version_message,
)

CRED_VARS = (
    "CONFLUENCE_BASE_URL",
    "CONFLUENCE_EMAIL",
    "CONFLUENCE_API_TOKEN",
    "ATLASSIAN_BASE_URL",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_API_TOKEN",
)

SAMPLE_PAGE = {
    "id": "12345",
    "title": "Payment refund — Functional Design Specification",
    "version": {"number": 3},
    "body": {"storage": {"value": "<p>refund</p>"}},
    "_links": {"webui": "/spaces/PAY/pages/viewpage.action?pageId=12345"},
}


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.saved = {name: os.environ.get(name) for name in CRED_VARS}
        for name in CRED_VARS:
            os.environ.pop(name, None)

    def tearDown(self) -> None:
        for name, value in self.saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_missing_credentials_are_enumerated(self) -> None:
        with self.assertRaises(ConfigError) as caught:
            Config.from_env()
        message = str(caught.exception)
        for name in ("CONFLUENCE_BASE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"):
            self.assertIn(name, message)

    def test_primary_names_are_read(self) -> None:
        os.environ.update(
            {
                "CONFLUENCE_BASE_URL": "https://test.atlassian.net/wiki",
                "CONFLUENCE_EMAIL": "dev@example.com",
                "CONFLUENCE_API_TOKEN": " token ",
            }
        )
        config = Config.from_env()
        self.assertEqual(config.site, "https://test.atlassian.net")
        self.assertEqual(config.token, "token")

    def test_atlassian_aliases_are_accepted(self) -> None:
        os.environ.update(
            {
                "ATLASSIAN_BASE_URL": "https://alt.atlassian.net/wiki",
                "ATLASSIAN_EMAIL": "alt@example.com",
                "ATLASSIAN_API_TOKEN": "alttoken",
            }
        )
        config = Config.from_env()
        self.assertEqual(config.email, "alt@example.com")
        self.assertEqual(config.base, "https://alt.atlassian.net/wiki")

    def test_env_file_parsing(self) -> None:
        for name in CRED_VARS:
            os.environ.pop(name, None)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dotenv"
            path.write_text(
                "# comment\nexport CONFLUENCE_BASE_URL=\"https://file.atlassian.net/wiki\"\n"
                "CONFLUENCE_EMAIL='a@b.co'\nCONFLUENCE_API_TOKEN=filetoken\nNOT_A_KEY\n",
                encoding="utf-8",
            )
            load_env_file(path)
        self.assertEqual(os.environ.get("CONFLUENCE_BASE_URL"), "https://file.atlassian.net/wiki")
        self.assertEqual(os.environ.get("CONFLUENCE_EMAIL"), "a@b.co")
        self.assertEqual(os.environ.get("CONFLUENCE_API_TOKEN"), "filetoken")


class HintTests(unittest.TestCase):
    def test_conflict_hint_demands_rebase(self) -> None:
        error = ApiError("PUT", "https://x/page", 409, "conflict")
        self.assertIn("conflict", error.hint().lower())
        self.assertIn("Never overwrite blindly", error.hint())

    def test_auth_and_rate_hints(self) -> None:
        self.assertIn("api-tokens", ApiError("GET", "u", 401, "").hint())
        self.assertIn("Rate limited", ApiError("GET", "u", 429, "").hint())
        self.assertIn("backup", ApiError("PUT", "u", 500, "").hint())


class PageHelperTests(unittest.TestCase):
    def test_page_version_and_body_defaults(self) -> None:
        self.assertEqual(page_version({}), 1)
        self.assertEqual(page_version(SAMPLE_PAGE), 3)
        self.assertEqual(page_body({}), "")
        self.assertEqual(page_body(SAMPLE_PAGE), "<p>refund</p>")

    def test_version_message_prefix_and_cap(self) -> None:
        self.assertEqual(version_message(1, "Add BR-004"), "v2 - Add BR-004")
        self.assertEqual(version_message(1, "v2 — BR-004: threshold"), "v2 — BR-004: threshold")
        with self.assertRaises(ConfigError):
            version_message(1, "   ")
        capped = version_message(2, "x" * 400)
        self.assertTrue(capped.startswith("v3 - "))
        self.assertEqual(len(capped), 255)
        self.assertTrue(capped.endswith("..."))

    def test_sha256_and_diff(self) -> None:
        self.assertEqual(
            sha256("abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )
        diff = unified_diff("<p>old</p>", "<p>new</p>", "a", "b")
        self.assertIn("-<p>old</p>", diff)
        self.assertIn("+<p>new</p>", diff)

    def test_backup_page_writes_storage_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "backups"
            storage_path = backup_page(SAMPLE_PAGE, directory)
            self.assertTrue(storage_path.exists())
            self.assertEqual(storage_path.read_text(encoding="utf-8"), "<p>refund</p>")
            sidecar = directory / storage_path.name.replace(".storage.html", ".json")
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual(metadata["version"], 3)
            self.assertEqual(metadata["id"], "12345")
            self.assertIn("pageId=12345", str(metadata["url"]))


def run_cli(args: list[str], env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess[str]:
    safe_env = {key: value for key, value in os.environ.items() if key not in CRED_VARS}
    safe_env.update(env)
    safe_env["PYTHONPATH"] = str(ROOT / "scripts")
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "confluence.py"), *args],
        capture_output=True,
        text=True,
        env=safe_env,
        cwd=cwd,
        timeout=60,
    )


class CliTests(unittest.TestCase):
    """Subprocess paths that must never touch the network."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.doc = self.dir / "page.md"
        self.doc.write_text(
            "---\ntitle: Demo page — FDS\nspace: DEMO\nversion: 1.0\nstatus: Draft\n---\n\n"
            "## 1. Purpose\n\nOne paragraph to make the file substantive for conversion.\n",
            encoding="utf-8",
        )
        self.fake = {
            "CONFLUENCE_BASE_URL": "https://unreachable.invalid/wiki",
            "CONFLUENCE_EMAIL": "ci@example.com",
            "CONFLUENCE_API_TOKEN": "not-a-secret",
        }

    def test_missing_credentials_fail_closed(self) -> None:
        for command in (["whoami"], ["get", "--page-id", "1"], ["create", "--from-md", str(self.doc)]):
            result = run_cli(command, {}, self.dir)
            self.assertEqual(result.returncode, 2, msg=f"{command}: {result.stderr}")
            self.assertIn("Missing credentials", result.stderr)

    def test_create_dry_run_builds_payload_without_network(self) -> None:
        result = run_cli(["create", "--from-md", str(self.doc), "--dry-run"], self.fake, self.dir)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("DRY RUN: create 'Demo page — FDS' in space DEMO", result.stdout)

    def test_space_is_required_even_for_dry_run(self) -> None:
        doc = self.dir / "nospace.md"
        doc.write_text("---\ntitle: No space\n---\n\nbody text\n", encoding="utf-8")
        result = run_cli(["create", "--from-md", str(doc), "--dry-run"], self.fake, self.dir)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Space is required", result.stderr)

    def test_credentials_are_never_echoed(self) -> None:
        result = run_cli(["create", "--from-md", str(self.doc), "--dry-run"], self.fake, self.dir)
        self.assertNotIn("not-a-secret", result.stdout + result.stderr)


if __name__ == "__main__":
    if "-v" in sys.argv:
        sys.argv.remove("-v")
        verbosity = 2
    else:
        verbosity = 1
    unittest.main(module=__name__, argv=[sys.argv[0]], verbosity=verbosity)
