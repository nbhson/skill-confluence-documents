#!/usr/bin/env python3
"""confluence.py - safe, idempotent command line client for Confluence Cloud.

Designed for agent use: every write supports --dry-run, captures a local backup,
bumps the page version with a required message, verifies the result, and refuses
to publish malformed storage XHTML.

Credentials (Atlassian Cloud):
    CONFLUENCE_BASE_URL=https://your-site.atlassian.net/wiki
    CONFLUENCE_EMAIL=you@company.com
    CONFLUENCE_API_TOKEN=...        # https://id.atlassian.com/manage-profile/security/api-tokens

Quick start:
    python3 confluence.py whoami
    python3 confluence.py get --page-id 12345 --out page.storage.html
    python3 confluence.py create --from-md fds.md --parent-id 98765
    python3 confluence.py upsert --from-md fds.md --message "Clarify refund approval"
    python3 confluence.py diff --page-id 12345 --from-md fds.md
    python3 confluence.py update --page-id 12345 --from-md fds.md --message "Add BR-004"
"""

from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request

sys.path.insert(0, str(Path(__file__).resolve().parent))

from md2storage import ConversionError, convert, is_well_formed  # noqa: E402


class ConfigError(RuntimeError):
    pass


class ApiError(RuntimeError):
    def __init__(self, method: str, url: str, status: int, body: str) -> None:
        super().__init__(f"{method} {url} -> HTTP {status}")
        self.method = method
        self.url = url
        self.status = status
        self.body = body

    def hint(self) -> str:
        if self.status == 401:
            return (
                "Authentication failed. Check CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN. "
                "Create a token at https://id.atlassian.com/manage-profile/security/api-tokens"
            )
        if self.status == 403:
            return (
                "Permission denied. The account must be able to edit this page/space, and scoped "
                "tokens need read/write:confluence scopes."
            )
        if self.status == 404:
            return (
                "Not found. Verify CONFLUENCE_BASE_URL (https://site.atlassian.net/wiki), the page ID, "
                "or the space key. Run 'whoami' to test the connection."
            )
        if self.status == 409:
            return (
                "Version conflict: someone edited the page after you fetched it. Re-run 'get', "
                "re-apply the change, and publish again. Never overwrite blindly."
            )
        if self.status == 429:
            return "Rate limited by Atlassian. Wait and retry; the client already retried 429 responses."
        if self.status >= 500:
            return "Atlassian server error. Retry later; your local backup is intact."
        return "Inspect the response body above; no page was written unless the command reported success."


@dataclass
class Config:
    base: str
    email: str
    token: str
    timeout: int = 60

    @property
    def site(self) -> str:
        return self.base[: -len("/wiki")] if self.base.endswith("/wiki") else self.base

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "Config":
        if env_file is not None:
            load_env_file(env_file)
        elif Path(".env").exists():
            load_env_file(Path(".env"))

        raw_base = os.environ.get("CONFLUENCE_BASE_URL") or os.environ.get("ATLASSIAN_BASE_URL")
        email = os.environ.get("CONFLUENCE_EMAIL") or os.environ.get("ATLASSIAN_EMAIL")
        token = os.environ.get("CONFLUENCE_API_TOKEN") or os.environ.get("ATLASSIAN_API_TOKEN")

        missing = [
            name
            for name, value in (
                ("CONFLUENCE_BASE_URL", raw_base),
                ("CONFLUENCE_EMAIL", email),
                ("CONFLUENCE_API_TOKEN", token),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "Missing credentials: "
                + ", ".join(missing)
                + ". Add them to .env (see .env.example) or export them."
            )

        parsed = parse.urlparse(raw_base.strip())
        if parsed.scheme not in ("https", "http") or not parsed.netloc:
            raise ConfigError(
                f"CONFLUENCE_BASE_URL must be an absolute URL, got {raw_base!r}. "
                "Example: https://acme.atlassian.net/wiki"
            )
        base = f"{parsed.scheme}://{parsed.netloc}/wiki"
        return cls(base=base, email=email.strip(), token=token.strip())


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise ConfigError(f"env file not found: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, separator, value = line.partition("=")
        if not separator:
            continue
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


class Api:
    def __init__(self, config: Config) -> None:
        self.config = config
        credentials = f"{config.email}:{config.token}".encode("utf-8")
        self.auth = "Basic " + base64.b64encode(credentials).decode("ascii")

    # -- transport --------------------------------------------------------- #

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        raw_body: bytes | None = None,
        content_type: str | None = None,
        extra_headers: dict[str, str] | None = None,
        expect_json: bool = True,
    ) -> Any:
        url = self.config.base + path
        headers = {
            "Authorization": self.auth,
            "Accept": "application/json",
        }
        if payload is not None:
            raw_body = json.dumps(payload).encode("utf-8")
            content_type = "application/json"
        if content_type:
            headers["Content-Type"] = content_type
        if extra_headers:
            headers.update(extra_headers)

        last_error: Exception | None = None
        for attempt in range(3):
            req = request.Request(url, data=raw_body, headers=headers, method=method)
            try:
                with request.urlopen(req, timeout=self.config.timeout) as response:
                    body = response.read()
                    if not body:
                        return None
                    if not expect_json:
                        return body
                    return json.loads(body.decode("utf-8"))
            except error.HTTPError as exc:
                body_text = exc.read().decode("utf-8", errors="replace")
                if exc.code == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After", "2")
                    try:
                        delay = min(10.0, max(1.0, float(retry_after)))
                    except ValueError:
                        delay = 2.0
                    time.sleep(delay)
                    last_error = exc
                    continue
                raise ApiError(method, url, exc.code, body_text) from exc
            except error.URLError as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise RuntimeError(f"Network error calling {url}: {exc.reason}") from exc
        raise RuntimeError(f"Request failed after retries: {last_error}")

    def _get(self, path: str) -> Any:
        return self._request("GET", path)

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        return self._request("POST", path, payload)

    def _put(self, path: str, payload: dict[str, Any]) -> Any:
        return self._request("PUT", path, payload)

    def _delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    # -- pages ------------------------------------------------------------- #

    def current_user(self) -> dict[str, Any]:
        return self._get("/rest/api/user/current")

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self._get(f"/api/v2/pages/{parse.quote(str(page_id))}?body-format=storage")

    def get_page_by_title(self, space_id: str, title: str) -> dict[str, Any] | None:
        query = parse.urlencode(
            {
                "space-id": space_id,
                "title": title,
                "body-format": "storage",
                "limit": 1,
            }
        )
        data = self._get(f"/api/v2/pages?{query}")
        results = data.get("results", []) if data else []
        return results[0] if results else None

    def create_page(
        self,
        space_id: str,
        title: str,
        storage: str,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "spaceId": str(space_id),
            "status": "current",
            "title": title,
            "body": {"representation": "storage", "value": storage},
        }
        if parent_id:
            payload["parentId"] = str(parent_id)
        return self._post("/api/v2/pages", payload)

    def update_page(
        self,
        page_id: str,
        title: str,
        storage: str,
        version: int,
        message: str,
    ) -> dict[str, Any]:
        payload = {
            "id": str(page_id),
            "status": "current",
            "title": title,
            "body": {"representation": "storage", "value": storage},
            "version": {"number": version, "message": message},
        }
        return self._put(f"/api/v2/pages/{parse.quote(str(page_id))}", payload)

    def page_versions(self, page_id: str, limit: int = 10) -> list[dict[str, Any]]:
        data = self._get(
            f"/api/v2/pages/{parse.quote(str(page_id))}/versions?limit={int(limit)}"
        )
        return data.get("results", []) if data else []

    def children(self, page_id: str, limit: int = 100) -> list[dict[str, Any]]:
        data = self._get(f"/api/v2/pages/{parse.quote(str(page_id))}/children?limit={int(limit)}")
        return data.get("results", []) if data else []

    # -- spaces ------------------------------------------------------------ #

    def get_space_id(self, key: str) -> str:
        data = self._get(f"/api/v2/spaces?keys={parse.quote(key)}&limit=1")
        results = data.get("results", []) if data else []
        if not results:
            raise ConfigError(f"Space key {key!r} was not found or is not visible to this account.")
        return str(results[0]["id"])

    def list_spaces(self, limit: int = 25, keys: str | None = None) -> list[dict[str, Any]]:
        query = f"?limit={int(limit)}"
        if keys:
            query += f"&keys={parse.quote(keys)}"
        data = self._get(f"/api/v2/spaces{query}")
        return data.get("results", []) if data else []

    # -- labels ------------------------------------------------------------ #

    def labels(self, page_id: str) -> list[dict[str, Any]]:
        data = self._get(f"/api/v2/pages/{parse.quote(str(page_id))}/labels?limit=200")
        return data.get("results", []) if data else []

    def add_label(self, page_id: str, name: str) -> None:
        try:
            self._post(f"/api/v2/pages/{parse.quote(str(page_id))}/labels", {"name": name})
        except ApiError as exc:
            if exc.status not in (400, 409):
                raise
            # v1 fallback: some tenants still reject the v2 single-label body.
            try:
                self._post(
                    f"/rest/api/content/{parse.quote(str(page_id))}/label",
                    [{"prefix": "global", "name": name}],
                )
            except ApiError as fallback:
                if fallback.status not in (400, 409):
                    raise

    def remove_label(self, page_id: str, label_id: str) -> None:
        self._delete(
            f"/api/v2/pages/{parse.quote(str(page_id))}/labels/{parse.quote(str(label_id))}"
        )

    # -- attachments ------------------------------------------------------- #

    def attachments(self, page_id: str) -> list[dict[str, Any]]:
        data = self._get(
            f"/api/v2/pages/{parse.quote(str(page_id))}/attachments?limit=100"
        )
        return data.get("results", []) if data else []

    def upload_attachment(self, page_id: str, file_path: Path) -> dict[str, Any]:
        if not file_path.exists():
            raise ConfigError(f"attachment not found: {file_path}")
        filename = file_path.name
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        content = file_path.read_bytes()

        boundary = "----ConfluenceSkill" + uuid.uuid4().hex
        head = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8")
        tail = (
            f"\r\n--{boundary}\r\n"
            'Content-Disposition: form-data; name="minorEdit"\r\n\r\n'
            "true"
            f"\r\n--{boundary}--\r\n"
        ).encode("utf-8")
        body = head + content + tail

        existing = next(
            (item for item in self.attachments(page_id) if item.get("title") == filename),
            None,
        )
        if existing:
            path = (
                f"/rest/api/content/{parse.quote(str(page_id))}/child/attachment/"
                f"{parse.quote(str(existing['id']))}/data"
            )
        else:
            path = f"/rest/api/content/{parse.quote(str(page_id))}/child/attachment"

        result = self._request(
            "POST",
            path,
            raw_body=body,
            content_type=f"multipart/form-data; boundary={boundary}",
            extra_headers={"X-Atlassian-Token": "nocheck"},
        )
        if isinstance(result, dict):
            results = result.get("results", [])
            return results[0] if results else result
        return {}

    # -- search / links ---------------------------------------------------- #

    def search(self, cql: str, limit: int = 15) -> list[dict[str, Any]]:
        query = parse.urlencode({"cql": cql, "limit": int(limit), "expand": "content.version"})
        data = self._get(f"/rest/api/search?{query}")
        return data.get("results", []) if data else []

    def remote_links(self, page_id: str) -> list[dict[str, Any]]:
        data = self._get(f"/rest/api/content/{parse.quote(str(page_id))}/remotelink")
        return data if isinstance(data, list) else []

    def add_jira_link(
        self,
        page_id: str,
        issue_key: str,
        relationship: str = "implements",
        title: str | None = None,
    ) -> dict[str, Any]:
        for link in self.remote_links(page_id):
            if link.get("globalId") == f"jira-{issue_key}":
                return link
        issue_url = f"{self.config.site}/browse/{parse.quote(issue_key)}"
        payload = {
            "globalId": f"jira-{issue_key}",
            "application": {"type": "com.atlassian.jira", "name": "Jira"},
            "relationship": relationship,
            "object": {"url": issue_url, "title": title or issue_key},
        }
        return self._post(
            f"/rest/api/content/{parse.quote(str(page_id))}/remotelink", payload
        )

    def remove_remote_link(self, page_id: str, link_id: str) -> None:
        self._delete(
            f"/rest/api/content/{parse.quote(str(page_id))}/remotelink/{parse.quote(str(link_id))}"
        )

    # -- convenience ------------------------------------------------------- #

    def page_url(self, page: dict[str, Any]) -> str:
        webui = (page.get("_links") or {}).get("webui")
        if webui:
            return self.config.site + webui
        return f"{self.config.base}/pages/{page.get('id', '')}"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def eprint(*values: Any) -> None:
    print(*values, file=sys.stderr)


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def page_version(page: dict[str, Any]) -> int:
    return int(((page.get("version") or {}).get("number")) or 1)


def page_body(page: dict[str, Any]) -> str:
    body = page.get("body") or {}
    storage = body.get("storage") or {}
    return storage.get("value") or ""


def read_source(args: argparse.Namespace) -> dict[str, Any]:
    if args.from_md:
        text = Path(args.from_md).read_text(encoding="utf-8")
        result = convert(text, lenient=getattr(args, "lenient", False))
        result["source"] = str(args.from_md)
        result["markdown"] = text
        return result
    if args.file:
        storage = Path(args.file).read_text(encoding="utf-8")
        well_formed, error = is_well_formed(storage)
        if not well_formed:
            raise ConversionError(f"{args.file} is not well-formed storage XHTML: {error}")
        return {
            "storage": storage,
            "frontmatter": {},
            "title": "",
            "space": "",
            "labels": [],
            "source": str(args.file),
        }
    raise ConfigError("Provide --from-md (Markdown) or --file (storage XHTML).")


def lint_markdown(path: str, profile: str, publish: bool) -> tuple[int, list[Any]]:
    from validate_document import Linter

    source = Path(path)
    linter = Linter(source, source.read_text(encoding="utf-8"), profile, publish=publish)
    findings = linter.run()
    linter.findings = findings
    score, _ = linter.score()
    return score, findings


def maybe_lint(args: argparse.Namespace) -> None:
    if not getattr(args, "lint", False) or not getattr(args, "from_md", None):
        return
    profile = getattr(args, "profile", "fds")
    publish = bool(getattr(args, "publish", False))
    score, findings = lint_markdown(args.from_md, profile, publish)
    errors = [item for item in findings if item.level == "error"]
    if errors or score < getattr(args, "min_score", 85):
        eprint(f"Lint failed: score {score}/100, {len(errors)} error(s).")
        for finding in errors[:10]:
            location = f"line {finding.line}" if finding.line else "document"
            eprint(f"  ERROR {finding.rule} ({location}): {finding.message}")
        raise SystemExit(1)
    eprint(f"Lint passed: score {score}/100.")


def resolve_space_id(api: Api, space: str) -> str:
    if space.isdigit():
        return space
    return api.get_space_id(space)


def collect_labels(args: argparse.Namespace, result: dict[str, Any]) -> list[str]:
    if getattr(args, "labels", None):
        return [item.strip() for item in args.labels.split(",") if item.strip()]
    return list(result.get("labels") or [])


def ensure_labels(api: Api, page_id: str, labels: list[str]) -> list[str]:
    if not labels:
        return []
    existing = {item.get("name") for item in api.labels(page_id)}
    added: list[str] = []
    for label in labels:
        if label not in existing:
            api.add_label(page_id, label)
            added.append(label)
    return added


def version_message(current_version: int, message: str) -> str:
    cleaned = " ".join(message.split())
    if not cleaned:
        raise ConfigError("--message is required: describe the change in the version history.")
    if not re.match(rf"^v{current_version + 1}\b", cleaned, re.IGNORECASE):
        cleaned = f"v{current_version + 1} - {cleaned}"
    if len(cleaned) > 255:
        cleaned = cleaned[:252] + "..."
    return cleaned


def backup_page(page: dict[str, Any], directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    stem = f"page-{page.get('id')}-v{page_version(page)}-{stamp}"
    storage_path = directory / f"{stem}.storage.html"
    storage_path.write_text(page_body(page), encoding="utf-8")
    metadata = {
        "id": page.get("id"),
        "title": page.get("title"),
        "version": page_version(page),
        "url": (page.get("_links") or {}).get("webui"),
        "backed_up_at": stamp,
    }
    (directory / f"{stem}.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return storage_path


def print_page(page: dict[str, Any], api: Api, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(page, ensure_ascii=False, indent=2))
        return
    print(f"id:      {page.get('id')}")
    print(f"title:   {page.get('title')}")
    print(f"version: {page_version(page)}")
    print(f"status:  {page.get('status')}")
    print(f"url:     {api.page_url(page)}")


def unified_diff(old: str, new: str, label_old: str, label_new: str) -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(old_lines, new_lines, fromfile=label_old, tofile=label_new, n=3)
    )


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def cmd_whoami(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    user = api.current_user()
    if args.json:
        print(json.dumps(user, ensure_ascii=False, indent=2))
    else:
        print(f"account: {user.get('displayName')}")
        print(f"email:   {user.get('email')}")
        print(f"accountId: {user.get('accountId')}")
        print(f"base:    {config.base}")
    return 0


def cmd_get(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    page = api.get_page(args.page_id)
    storage = page_body(page)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(storage + "\n", encoding="utf-8")
        eprint(f"saved {len(storage):,} chars to {args.out}")
        eprint(f"page {page.get('id')} v{page_version(page)}: {page.get('title')}")
        eprint(f"url: {api.page_url(page)}")
        if args.json:
            print(json.dumps(page, ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(page, ensure_ascii=False, indent=2))
    else:
        eprint(f"page {page.get('id')} v{page_version(page)}: {page.get('title')}")
        print(storage)
    return 0


def cmd_create(args: argparse.Namespace, config: Config) -> int:
    maybe_lint(args)
    api = Api(config)
    result = read_source(args)
    title = args.title or result.get("title", "")
    space = args.space or result.get("space", "")
    if not title:
        raise ConfigError("Page title is required: add 'title' to frontmatter or pass --title.")
    if not space:
        raise ConfigError("Space is required: add 'space' to frontmatter or pass --space KEY.")
    labels = collect_labels(args, result)
    if args.dry_run:
        print(f"DRY RUN: create '{title}' in space {space}, {len(result['storage']):,} chars")
        print(f"labels: {', '.join(labels) if labels else '(none)'}")
        return 0
    space_id = resolve_space_id(api, space)
    page = api.create_page(space_id, title, result["storage"], args.parent_id)
    page_id = str(page["id"])
    added = ensure_labels(api, page_id, labels)
    if args.json:
        print(json.dumps({**page, "labels_added": added}, ensure_ascii=False, indent=2))
    else:
        print(f"created page {page_id}: {title}")
        print(f"url: {api.page_url(page)}")
        if added:
            print(f"labels added: {', '.join(added)}")
    return 0


def cmd_update(args: argparse.Namespace, config: Config) -> int:
    maybe_lint(args)
    api = Api(config)
    current = api.get_page(args.page_id)
    result = read_source(args)
    storage = result["storage"]
    current_storage = page_body(current)

    if sha256(storage) == sha256(current_storage) and not args.force:
        print(f"No changes: page {args.page_id} is already at v{page_version(current)}.")
        return 0

    title = args.title or current.get("title") or result.get("title")
    if not title:
        raise ConfigError("Page title is required.")
    new_version = page_version(current) + 1
    message = version_message(page_version(current), args.message)

    diff = unified_diff(
        current_storage,
        storage,
        f"page-{args.page_id}-v{page_version(current)}",
        f"page-{args.page_id}-v{new_version}",
    )
    if args.dry_run:
        print(f"DRY RUN: update page {args.page_id} v{page_version(current)} -> v{new_version}")
        print(f"title: {title}")
        print(f"message: {message}")
        print(f"changed lines: {sum(1 for line in diff.splitlines() if line.startswith(('+', '-')))}")
        if diff:
            print("")
            print(diff[: args.diff_lines])
        return 0

    backup_dir = Path(args.backup_dir)
    backup = backup_page(current, backup_dir)
    eprint(f"backup: {backup}")

    updated = api.update_page(args.page_id, title, storage, new_version, message)
    if args.verify:
        verified = api.get_page(args.page_id)
        if sha256(page_body(verified)) != sha256(storage):
            eprint(
                "WARNING: Confluence normalised the storage after publish; "
                "re-fetch and inspect the page before closing the task."
            )
        else:
            eprint("verified: remote storage matches the pushed document")
        updated = verified

    labels = collect_labels(args, result) if (args.update_labels or args.labels) else []
    added = ensure_labels(api, args.page_id, labels)

    if args.json:
        print(json.dumps({**updated, "labels_added": added, "backup": str(backup)}, ensure_ascii=False, indent=2))
    else:
        print(f"updated page {args.page_id} to v{page_version(updated)}: {title}")
        print(f"url: {api.page_url(updated)}")
        print(f"message: {message}")
        print(f"backup: {backup}")
        if added:
            print(f"labels added: {', '.join(added)}")
    return 0


def cmd_upsert(args: argparse.Namespace, config: Config) -> int:
    if not args.from_md:
        raise ConfigError("upsert requires --from-md so the title and space come from frontmatter.")
    maybe_lint(args)
    api = Api(config)
    result = read_source(args)
    title = args.title or result.get("title", "")
    space = args.space or result.get("space", "")
    if not title or not space:
        raise ConfigError("upsert requires title and space in frontmatter (or --title / --space).")
    space_id = resolve_space_id(api, space)
    existing = api.get_page_by_title(space_id, title)
    labels = collect_labels(args, result)

    if existing:
        page_id = str(existing["id"])
        current_storage = page_body(existing)
        if sha256(result["storage"]) == sha256(current_storage) and not args.force:
            print(f"Unchanged: '{title}' (page {page_id}, v{page_version(existing)})")
            if args.dry_run:
                print("DRY RUN: would skip the update.")
            return 0
        new_version = page_version(existing) + 1
        message = version_message(page_version(existing), args.message)
        if args.dry_run:
            print(f"DRY RUN: update '{title}' (page {page_id}) v{page_version(existing)} -> v{new_version}")
            print(f"message: {message}")
            return 0
        backup = backup_page(existing, Path(args.backup_dir))
        eprint(f"backup: {backup}")
        updated = api.update_page(page_id, title, result["storage"], new_version, message)
        added = ensure_labels(api, page_id, labels)
        if args.verify:
            verified = api.get_page(page_id)
            if sha256(page_body(verified)) == sha256(result["storage"]):
                updated = verified
            else:
                eprint("WARNING: remote storage differs after publish; inspect the page.")
        if args.json:
            print(json.dumps({**updated, "labels_added": added}, ensure_ascii=False, indent=2))
        else:
            print(f"updated '{title}' (page {page_id}) to v{page_version(updated)}")
            print(f"url: {api.page_url(updated)}")
            print(f"backup: {backup}")
        return 0

    if args.dry_run:
        print(f"DRY RUN: create '{title}' in space {space} (no page with this title exists)")
        return 0
    page = api.create_page(space_id, title, result["storage"], args.parent_id)
    page_id = str(page["id"])
    added = ensure_labels(api, page_id, labels)
    if args.json:
        print(json.dumps({**page, "labels_added": added}, ensure_ascii=False, indent=2))
    else:
        print(f"created '{title}' (page {page_id})")
        print(f"url: {api.page_url(page)}")
        if added:
            print(f"labels added: {', '.join(added)}")
    return 0


def cmd_diff(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    current = api.get_page(args.page_id)
    result = read_source(args)
    diff = unified_diff(
        page_body(current),
        result["storage"],
        f"page-{args.page_id}-v{page_version(current)}",
        "candidate",
    )
    if not diff:
        print("No differences.")
        return 0
    print(diff)
    return 0


def cmd_labels(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    if args.add or args.remove:
        existing = {item.get("name"): item for item in api.labels(args.page_id)}
        if args.add:
            for label in [item.strip() for item in args.add.split(",") if item.strip()]:
                if label not in existing:
                    api.add_label(args.page_id, label)
                    print(f"added label: {label}")
        if args.remove:
            for label in [item.strip() for item in args.remove.split(",") if item.strip()]:
                item = existing.get(label)
                if item:
                    api.remove_label(args.page_id, str(item["id"]))
                    print(f"removed label: {label}")
    labels = api.labels(args.page_id)
    if args.json:
        print(json.dumps(labels, ensure_ascii=False, indent=2))
    else:
        print("labels: " + (", ".join(item.get("name", "") for item in labels) if labels else "(none)"))
    return 0


def cmd_attach(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    if args.dry_run:
        print(f"DRY RUN: upload {args.file} to page {args.page_id}")
        return 0
    attachment = api.upload_attachment(args.page_id, Path(args.file))
    print(f"attached {args.file} to page {args.page_id}")
    if attachment.get("id"):
        print(f"attachment id: {attachment['id']}")
    return 0


def cmd_search(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    if args.cql:
        cql = args.cql
    elif args.title:
        cql = f'title ~ "{args.title}"'
        if args.space:
            cql += f' and space = "{args.space}"'
    else:
        raise ConfigError("search needs --cql or --title (optionally with --space).")
    results = api.search(cql, args.limit)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    if not results:
        print("No results.")
        return 0
    for item in results:
        content = item.get("content") or {}
        print(
            f"{content.get('id')}\t{content.get('title')}\t"
            f"v{((content.get('version') or {}).get('number', '?'))}\t"
            f"{content.get('type', '')}"
        )
    return 0


def cmd_children(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    results = api.children(args.page_id, args.limit)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    for page in results:
        print(f"{page.get('id')}\t{page.get('title')}")
    return 0


def cmd_versions(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    results = api.page_versions(args.page_id, args.limit)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    for version in results:
        print(
            f"v{version.get('number')}\t{version.get('createdAt', '')}\t"
            f"{version.get('message') or ''}"
        )
    return 0


def cmd_spaces(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    results = api.list_spaces(args.limit, args.keys)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    for space in results:
        print(f"{space.get('key')}\t{space.get('id')}\t{space.get('name')}")
    return 0


def cmd_jira_link(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    if args.action == "list":
        links = api.remote_links(args.page_id)
        if args.json:
            print(json.dumps(links, ensure_ascii=False, indent=2))
        else:
            for link in links:
                obj = link.get("object") or {}
                print(
                    f"{link.get('id')}\t{link.get('relationship', '')}\t"
                    f"{obj.get('title', '')}\t{obj.get('url', '')}"
                )
        return 0
    if args.action == "remove":
        if not args.link_id:
            raise ConfigError("remove needs --link-id (see 'jira-link list').")
        api.remove_remote_link(args.page_id, args.link_id)
        print(f"removed remote link {args.link_id}")
        return 0
    if not args.issue:
        raise ConfigError("add needs --issue PAY-123.")
    if args.dry_run:
        print(f"DRY RUN: link page {args.page_id} to {args.issue} ({args.relationship})")
        return 0
    link = api.add_jira_link(args.page_id, args.issue, args.relationship, args.title)
    print(f"linked page {args.page_id} to {args.issue} ({args.relationship})")
    if args.json:
        print(json.dumps(link, ensure_ascii=False, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace, config: Config) -> int:
    api = Api(config)
    page = api.get_page(args.page_id)
    ok = True
    if args.file:
        expected = Path(args.file).read_text(encoding="utf-8")
        if sha256(expected) != sha256(page_body(page)):
            ok = False
            print("MISMATCH: remote storage differs from the local file.")
        else:
            print("OK: remote storage matches the local file.")
    wells, error = is_well_formed(page_body(page))
    if not wells:
        ok = False
        print(f"INVALID: remote storage is not well-formed: {error}")
    print(f"page {page.get('id')} v{page_version(page)}: {page.get('title')}")
    print(f"url: {api.page_url(page)}")
    return 0 if ok else 1


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def add_source_options(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--from-md", help="Markdown source to convert")
    source.add_argument("--file", help="raw Confluence storage XHTML")
    parser.add_argument("--lint", action="store_true", help="lint Markdown before writing")
    parser.add_argument("--profile", default="fds", help="lint profile (fds, api, rfc, runbook...)")
    parser.add_argument("--min-score", type=int, default=85, help="minimum lint score (default: 85)")
    parser.add_argument("--publish", action="store_true", help="treat placeholders/labels as lint errors")
    parser.add_argument("--lenient", action="store_true", help="keep unknown macros literal")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safe Confluence Cloud client for enterprise documents."
    )
    parser.add_argument("--env-file", type=Path, help="load credentials from this .env file")
    subparsers = parser.add_subparsers(dest="command", required=True)

    whoami = subparsers.add_parser("whoami", help="verify credentials and print the current user")
    whoami.add_argument("--json", action="store_true")
    whoami.set_defaults(func=cmd_whoami)

    get = subparsers.add_parser("get", help="fetch a page's storage XHTML")
    get.add_argument("--page-id", required=True)
    get.add_argument("--out", help="write storage to this file")
    get.add_argument("--json", action="store_true", help="print the full API response")
    get.set_defaults(func=cmd_get)

    create = subparsers.add_parser("create", help="create a new page")
    add_source_options(create)
    create.add_argument("--title", help="override the frontmatter title")
    create.add_argument("--space", help="space key (defaults to frontmatter 'space')")
    create.add_argument("--parent-id", help="parent page ID")
    create.add_argument("--labels", help="comma-separated labels (defaults to frontmatter)")
    create.add_argument("--dry-run", action="store_true")
    create.add_argument("--json", action="store_true")
    create.set_defaults(func=cmd_create)

    update = subparsers.add_parser("update", help="update a page, bump version and change log")
    add_source_options(update)
    update.add_argument("--page-id", required=True)
    update.add_argument("--title", help="new title (default: unchanged)")
    update.add_argument("--message", required=True, help="version history message")
    update.add_argument("--labels", help="comma-separated labels to add")
    update.add_argument("--update-labels", action="store_true", help="add frontmatter/--labels labels")
    update.add_argument("--backup-dir", default=".confluence-backups")
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--force", action="store_true", help="write even when the content hash is identical")
    update.add_argument("--verify", action="store_true", default=True)
    update.add_argument("--no-verify", dest="verify", action="store_false")
    update.add_argument("--diff-lines", type=int, default=4000)
    update.add_argument("--json", action="store_true")
    update.set_defaults(func=cmd_update)

    upsert = subparsers.add_parser("upsert", help="create or update by title (idempotent publish)")
    add_source_options(upsert)
    upsert.add_argument("--title", help="override the frontmatter title")
    upsert.add_argument("--space", help="space key (defaults to frontmatter 'space')")
    upsert.add_argument("--parent-id", help="parent page ID when creating")
    upsert.add_argument("--message", default="Synchronised document from source")
    upsert.add_argument("--labels", help="comma-separated labels (defaults to frontmatter)")
    upsert.add_argument("--backup-dir", default=".confluence-backups")
    upsert.add_argument("--dry-run", action="store_true")
    upsert.add_argument("--force", action="store_true")
    upsert.add_argument("--verify", action="store_true", default=True)
    upsert.add_argument("--no-verify", dest="verify", action="store_false")
    upsert.add_argument("--json", action="store_true")
    upsert.set_defaults(func=cmd_upsert)

    diff = subparsers.add_parser("diff", help="show the storage diff before publishing")
    add_source_options(diff)
    diff.add_argument("--page-id", required=True)
    diff.set_defaults(func=cmd_diff)

    labels = subparsers.add_parser("labels", help="list, add or remove page labels")
    labels.add_argument("--page-id", required=True)
    labels.add_argument("--add", help="comma-separated labels to add")
    labels.add_argument("--remove", help="comma-separated labels to remove")
    labels.add_argument("--json", action="store_true")
    labels.set_defaults(func=cmd_labels)

    attach = subparsers.add_parser("attach", help="upload or replace an attachment")
    attach.add_argument("--page-id", required=True)
    attach.add_argument("--file", required=True)
    attach.add_argument("--dry-run", action="store_true")
    attach.set_defaults(func=cmd_attach)

    search = subparsers.add_parser("search", help="search pages with CQL")
    search.add_argument("--cql")
    search.add_argument("--title")
    search.add_argument("--space")
    search.add_argument("--limit", type=int, default=15)
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=cmd_search)

    children = subparsers.add_parser("children", help="list child pages")
    children.add_argument("--page-id", required=True)
    children.add_argument("--limit", type=int, default=100)
    children.add_argument("--json", action="store_true")
    children.set_defaults(func=cmd_children)

    versions = subparsers.add_parser("versions", help="list page versions")
    versions.add_argument("--page-id", required=True)
    versions.add_argument("--limit", type=int, default=10)
    versions.add_argument("--json", action="store_true")
    versions.set_defaults(func=cmd_versions)

    spaces = subparsers.add_parser("spaces", help="list spaces or resolve a key")
    spaces.add_argument("--keys", help="comma-separated space keys")
    spaces.add_argument("--limit", type=int, default=25)
    spaces.add_argument("--json", action="store_true")
    spaces.set_defaults(func=cmd_spaces)

    jira_link = subparsers.add_parser("jira-link", help="manage Jira remote links on a page")
    jira_link.add_argument("action", choices=["add", "list", "remove"])
    jira_link.add_argument("--page-id", required=True)
    jira_link.add_argument("--issue", help="Jira issue key, for example PAY-123")
    jira_link.add_argument("--relationship", default="implements")
    jira_link.add_argument("--title", help="remote link title (default: issue key)")
    jira_link.add_argument("--link-id", help="remote link ID for remove")
    jira_link.add_argument("--dry-run", action="store_true")
    jira_link.add_argument("--json", action="store_true")
    jira_link.set_defaults(func=cmd_jira_link)

    verify = subparsers.add_parser("verify", help="verify remote storage and page version")
    verify.add_argument("--page-id", required=True)
    verify.add_argument("--file", help="local storage file to compare")
    verify.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = Config.from_env(args.env_file)
        return args.func(args, config)
    except ConfigError as exc:
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2
    except ApiError as exc:
        print(f"API ERROR [{exc.status}] {exc.method} {exc.url}", file=sys.stderr)
        print(exc.body[:2000], file=sys.stderr)
        print(f"HINT: {exc.hint()}", file=sys.stderr)
        return 1
    except ConversionError as exc:
        print(f"DOCUMENT ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
