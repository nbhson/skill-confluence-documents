#!/usr/bin/env python3
"""validate_skills.py - repository contract for skill-confluence-documents.

Checks the structure that makes this repository usable as an agent skill:

1. Twelve guide folders with the standard 10-section anatomy.
2. Frontmatter metadata and resolvable `related` references.
3. `skills/data.json` coverage, metadata and symmetric combination matrix.
4. Anti-pattern, definition, principle and token parity between guides and JSON.
5. The 12x12 README combination matrix matches `data.json`.
6. Every template converts to well-formed Confluence storage XHTML.
7. The completed Vietnamese example passes the publication lint at >= 85.
8. The format showcase converts and lints clean at profile `generic --publish`.
9. Root router, references, glossary, plan, CI, environment example and licence exist.
10. Host adapters exist for Claude Code, GitHub Copilot, Cline and generic agents,
    point back to `SKILL.md`, and their routing tables carry the same
    (template, lint profile) pairs as the router's Step 0 table.
11. No secrets, generated storage, backups or cache directories in the tree.

Usage:
    python3 scripts/validate_skills.py
    python3 scripts/validate_skills.py --verbose

Exit codes: 0 pass, 1 contract violation, 2 runtime error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from md2storage import ConversionError, convert  # noqa: E402
from validate_document import Linter  # noqa: E402

EXPECTED_SECTIONS = [
    "Definition",
    "Core Principles",
    "Spec Tokens",
    "Composition",
    "Signature Patterns",
    "Real-World Use Cases",
    "Combination Notes",
    "Anti-Patterns",
    "Code Examples",
    "Implementation Checklist",
]
SECTION_RE = re.compile(r"^## (\d{1,2})\. (.+)$")
SHORT_NAMES = {
    "document-architecture": "Architecture",
    "fds-requirements": "FDS",
    "visual-hierarchy": "Hierarchy",
    "storage-format": "Storage",
    "tables-matrices": "Tables",
    "diagrams": "Diagrams",
    "jira-traceability": "Jira",
    "update-versioning": "Versioning",
    "api-contracts": "API",
    "review-governance": "Review",
    "readability-accessibility": "Readability",
    "automation-quality": "Automation",
}
FORBIDDEN_DIRS = {".work", ".confluence-backups"}
SECRET_PATTERNS = [
    re.compile(r"\bATATT[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]

failures: list[str] = []
passes: list[str] = []


def ok(message: str) -> None:
    passes.append(message)


def fail(message: str) -> None:
    failures.append(message)


def check(condition: bool, message: str) -> None:
    if condition:
        ok(message)
    else:
        fail(message)


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #


def visible_text(text: str) -> list[str]:
    """Return lines outside fenced code blocks, preserving line count."""
    lines: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^(`{3,}|~{3,})", stripped)
        if match:
            char, size = match.group(1)[0], len(match.group(1))
            if fence is None:
                fence = (char, size)
                lines.append("")
                continue
            if char == fence[0] and size >= fence[1] and stripped == match.group(1):
                fence = None
                lines.append("")
                continue
        lines.append("" if fence else line)
    return lines


def split_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def section_map(text: str) -> dict[int, str]:
    lines = visible_text(text)
    heads: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = SECTION_RE.match(line)
        if match:
            heads.append((index, int(match.group(1)), match.group(2).strip()))
    sections: dict[int, str] = {}
    for position, (index, number, _title) in enumerate(heads):
        end = heads[position + 1][0] if position + 1 < len(heads) else len(lines)
        sections[number] = "\n".join(lines[index + 1 : end]).strip()
    return sections


def section_titles(text: str) -> dict[int, str]:
    titles: dict[int, str] = {}
    for line in visible_text(text):
        match = SECTION_RE.match(line)
        if match:
            titles[int(match.group(1))] = match.group(2).strip()
    return titles


def bullets(body: str, stop_at: str | None = None) -> list[str]:
    if stop_at and stop_at in body:
        body = body.split(stop_at, 1)[0]
    return [match.group(1).strip() for line in body.splitlines() if (match := re.match(r"^- (.+)$", line))]


def paragraphs(body: str) -> str:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", body) if chunk.strip()]
    return " ".join(chunks)


def tokens_from(body: str) -> list[dict[str, str]]:
    tokens: list[dict[str, str]] = []
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip().replace("`", "").strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "Role" or set(cells[0]) <= set("-: "):
            continue
        if set(cells[1]) <= set("-: "):
            continue
        tokens.append({"role": cells[0], "token": cells[1], "value": cells[2], "notes": cells[3]})
    return tokens


def guide_data(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    sections = section_map(text)
    description = split_frontmatter(text).get("description", "")
    name = ""
    title = re.search(r"^# (.+)$", text, re.M)
    if title:
        name = title.group(1).split(": ", 1)[-1].strip()
    accessibility = sections.get(8, "").split("### Accessibility Notes", 1)
    return {
        "name": name,
        "summary": description,
        "definition": paragraphs(sections.get(1, "")),
        "principles": bullets(sections.get(2, "")),
        "tokens": tokens_from(sections.get(3, "")),
        "composition": bullets(sections.get(4, "")),
        "patterns": bullets(sections.get(5, "")),
        "useCases": bullets(sections.get(6, "")),
        "antiPatterns": bullets(sections.get(8, ""), "### Accessibility Notes"),
        "accessibilityNotes": accessibility[1].strip() if len(accessibility) == 2 else "",
    }


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #


def check_guides() -> list[Path]:
    skills_dir = ROOT / "skills"
    guides = sorted(path for path in skills_dir.glob("*/SKILL.md") if path.parent.name[:2].isdigit())
    check(len(guides) == 12, f"12 guide folders present (found {len(guides)})")
    expected_numbers = [f"{number:02d}" for number in range(1, 13)]
    actual_numbers = [guide.parent.name[:2] for guide in guides]
    check(actual_numbers == expected_numbers, "guide folders are numbered 01 through 12 in order")

    for guide in guides:
        rel = guide.relative_to(ROOT)
        text = guide.read_text(encoding="utf-8")
        frontmatter = split_frontmatter(text)
        check(bool(frontmatter.get("name")), f"{rel}: frontmatter name")
        check(bool(frontmatter.get("description")), f"{rel}: frontmatter description")
        check(frontmatter.get("tags", "").startswith("["), f"{rel}: frontmatter tags")
        related = re.findall(r"[a-z0-9-]+", frontmatter.get("related", "").replace("[", "").replace("]", ""))
        check(bool(related), f"{rel}: frontmatter related")
        sections = section_map(text)
        titles = section_titles(text)
        check(sorted(sections) == list(range(1, 11)), f"{rel}: exactly ten numbered H2 sections")
        for number, expected in enumerate(EXPECTED_SECTIONS, 1):
            actual = titles.get(number, "")
            check(actual == expected, f"{rel}: section {number} is '{expected}' (found '{actual}')")
        data = guide_data(guide)
        check(len(data["definition"]) > 120, f"{rel}: definition is substantive")
        check(len(data["principles"]) >= 6, f"{rel}: at least six principles")
        check(len(data["tokens"]) >= 6, f"{rel}: at least six spec tokens")
        check(len(data["antiPatterns"]) >= 5, f"{rel}: at least five anti-patterns")
        check("Accessibility Notes" in text, f"{rel}: accessibility notes")
        check(len(data["patterns"]) >= 3, f"{rel}: at least three signature patterns")
        check(len(data["useCases"]) >= 3, f"{rel}: at least three use cases")
    return guides


def check_related(guides: list[Path]) -> None:
    ids = {guide.parent.name.split("-", 1)[1] for guide in guides}
    for guide in guides:
        frontmatter = split_frontmatter(guide.read_text(encoding="utf-8"))
        raw = frontmatter.get("related", "").replace("[", "").replace("]", "")
        related = [item.strip() for item in raw.split(",") if item.strip()]
        missing = [item for item in related if item not in ids]
        check(not missing, f"{guide.relative_to(ROOT)}: related ids resolve ({', '.join(missing) or 'ok'})")


def check_data(guides: list[Path]) -> dict:
    path = ROOT / "skills" / "data.json"
    if not path.exists():
        fail("skills/data.json exists")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"skills/data.json parses: {exc}")
        return {}
    ok("skills/data.json parses")
    meta = data.get("meta", {})
    check(meta.get("totalSkills") == 12, "data.json meta.totalSkills is 12")
    check(meta.get("version") == "1.0", "data.json meta.version is 1.0")
    skills = data.get("skills", [])
    check(len(skills) == 12, f"data.json contains 12 skills (found {len(skills)})")
    ids = [skill.get("id") for skill in skills]
    check(len(set(ids)) == len(ids), "data.json skill ids are unique")
    expected = [guide.parent.name.split("-", 1)[1] for guide in guides]
    check(ids == expected, "data.json skill order matches the guide folders")

    by_id = {skill.get("id"): skill for skill in skills}
    for guide in guides:
        sid = guide.parent.name.split("-", 1)[1]
        skill = by_id.get(sid)
        if not skill:
            fail(f"{sid}: present in data.json")
            continue
        check(skill.get("folder") == guide.parent.name, f"{sid}: data.json folder matches")
        check(skill.get("number") == int(guide.parent.name[:2]), f"{sid}: data.json number matches")
        data_sections = skill.get("sections", {})
        for key in ("definition", "principles", "tokens", "composition", "patterns", "useCases", "antiPatterns", "combinations", "accessibility"):
            check(key in data_sections, f"{sid}: data.json section '{key}'")

        parsed = guide_data(guide)
        check(skill.get("name") == parsed["name"], f"{sid}: data.json name mirrors the guide")
        check(skill.get("summary") == parsed["summary"], f"{sid}: data.json summary mirrors the guide")
        for key in ("definition", "principles", "tokens", "composition", "patterns", "useCases", "antiPatterns"):
            check(
                data_sections.get(key) == parsed[key],
                f"{sid}: data.json {key} mirrors the guide",
            )

        accessibility = data_sections.get("accessibility", {})
        check(accessibility.get("required") is True, f"{sid}: accessibility is required")
        check(bool(accessibility.get("fallback")), f"{sid}: accessibility fallback exists")
        check(accessibility.get("notes") == parsed["accessibilityNotes"], f"{sid}: accessibility notes mirror the guide")

    # Symmetric combination matrix
    all_ids = set(ids)
    for skill in skills:
        sid = skill.get("id")
        combos = skill.get("sections", {}).get("combinations", {})
        good = combos.get("good", [])
        caution = combos.get("caution", [])
        avoid = combos.get("avoid", [])
        union = set(good) | set(caution) | set(avoid)
        check(union == all_ids - {sid}, f"{sid}: combinations cover every other skill exactly once")
        check(not (set(good) & set(caution)), f"{sid}: good and caution are disjoint")
        check(sid not in union, f"{sid}: no self-combination")
        for other in caution:
            reverse = by_id.get(other, {}).get("sections", {}).get("combinations", {}).get("caution", [])
            check(sid in reverse, f"{sid} <-> {other}: caution is symmetric")
        for other in good:
            reverse = by_id.get(other, {}).get("sections", {}).get("combinations", {}).get("good", [])
            check(sid in reverse, f"{sid} <-> {other}: good is symmetric")
    return data


def check_readme_matrix(data: dict) -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        fail("README.md exists")
        return
    text = readme.read_text(encoding="utf-8")
    check("<!-- MATRIX -->" not in text, "README combination matrix is generated")
    skills = data.get("skills", [])
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.startswith("| **"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(skills) + 1:
            continue
        name = cells[0].strip("* ")
        rows[name] = cells[1:]
    check(len(rows) == 12, f"README matrix has 12 rows (found {len(rows)})")
    for skill in skills:
        name = skill.get("name")
        row = rows.get(name)
        if row is None:
            fail(f"README matrix row for {name}")
            continue
        expected: list[str] = []
        caution = skill.get("sections", {}).get("combinations", {}).get("caution", [])
        for other in skills:
            if other.get("id") == skill.get("id"):
                expected.append("—")
            elif other.get("id") in caution:
                expected.append("⚠️")
            else:
                expected.append("✅")
        check(row == expected, f"README matrix row for {name} matches data.json")


def check_templates() -> None:
    templates = sorted((ROOT / "assets" / "templates").glob("*.md"))
    check(len(templates) >= 8, f"at least eight templates present (found {len(templates)})")
    for template in templates:
        try:
            result = convert(template.read_text(encoding="utf-8"))
        except ConversionError as exc:
            fail(f"{template.relative_to(ROOT)}: converts to storage ({exc})")
            continue
        storage = result["storage"]
        check(len(storage) > 500, f"{template.relative_to(ROOT)}: storage is substantive")
        check("ac:structured-macro" in storage, f"{template.relative_to(ROOT)}: contains macros")
        ok(f"{template.relative_to(ROOT)}: converts to well-formed storage")


def check_example() -> None:
    example = ROOT / "assets" / "examples" / "fds-payment-refund.vi.md"
    if not example.exists():
        fail("completed Vietnamese example exists")
        return
    text = example.read_text(encoding="utf-8")
    try:
        result = convert(text)
        check(len(result["storage"]) > 5_000, "example converts to substantive storage XHTML")
    except ConversionError as exc:
        fail(f"example converts to storage ({exc})")
    linter = Linter(example, text, "fds-vi", publish=True, allow_placeholders=False, config={})
    findings = linter.run()
    score, grade = linter.score()
    errors = [finding for finding in findings if finding.level == "error"]
    check(not errors, f"example has no publication errors (found {len(errors)})")
    check(score >= 85, f"example scores >= 85 with --profile fds-vi --publish (score {score}, {grade})")
    ok(f"example score: {score}/100 ({grade})")


def routing_pairs(text: str) -> set[tuple[str, str]]:
    """Collect (template cell, following cell) pairs from Markdown routing tables."""
    pairs: set[tuple[str, str]] = set()
    for line in text.splitlines():
        if "assets/templates/" not in line or "|" not in line:
            continue
        cells = [
            cell.strip().replace("`", "").strip()
            for cell in line.strip().strip("|").split("|")
        ]
        for position, cell in enumerate(cells):
            if cell.startswith("assets/templates/") and position + 1 < len(cells):
                pairs.add((cell, cells[position + 1]))
                break
    return pairs


def check_adapters_routing() -> None:
    """Adapter routing tables must carry exactly the router's (template, profile) pairs."""
    router = ROOT / "SKILL.md"
    if not router.exists():
        fail("SKILL.md present for routing parity check")
        return
    expected = routing_pairs(router.read_text(encoding="utf-8"))
    check(len(expected) >= 8, f"router Step 0 table has >= 8 template rows (found {len(expected)})")
    adapters = [
        ROOT / "AGENTS.md",
        ROOT / ".github" / "copilot-instructions.md",
        ROOT / ".clinerules" / "confluence-documents.md",
    ]
    for adapter in adapters:
        if not adapter.exists():
            fail(f"{adapter.relative_to(ROOT)} present for routing parity check")
            continue
        actual = routing_pairs(adapter.read_text(encoding="utf-8"))
        drift = expected ^ actual
        check(
            actual == expected,
            f"{adapter.relative_to(ROOT)}: routing table matches SKILL.md "
            f"({'ok' if not drift else 'drift: ' + repr(sorted(drift))})",
        )


def check_showcase() -> None:
    showcase = ROOT / "assets" / "examples" / "confluence-format-showcase.md"
    if not showcase.exists():
        fail("format showcase example exists")
        return
    text = showcase.read_text(encoding="utf-8")
    try:
        result = convert(text)
        check(len(result["storage"]) > 5_000, "showcase converts to substantive storage XHTML")
    except ConversionError as exc:
        fail(f"showcase converts to storage ({exc})")
    linter = Linter(showcase, text, "generic", publish=True, allow_placeholders=False, config={})
    findings = linter.run()
    score, grade = linter.score()
    errors = [finding for finding in findings if finding.level == "error"]
    check(not errors, f"showcase has no publication errors (found {len(errors)})")
    check(score >= 90, f"showcase scores >= 90 with --profile generic --publish (score {score}, {grade})")
    ok(f"showcase score: {score}/100 ({grade})")


def check_assets() -> None:
    required = [
        ROOT / "SKILL.md",
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "CLAUDE.md",
        ROOT / ".github" / "copilot-instructions.md",
        ROOT / ".clinerules" / "confluence-documents.md",
        ROOT / "plan" / "readme.md",
        ROOT / "skills" / "assets" / "references.md",
        ROOT / "assets" / "terminology" / "vi-en-glossary.md",
        ROOT / "assets" / "examples" / "confluence-format-showcase.md",
        ROOT / ".env.example",
        ROOT / ".gitignore",
        ROOT / "LICENSE",
        ROOT / ".github" / "workflows" / "validate.yml",
        ROOT / "scripts" / "md2storage.py",
        ROOT / "scripts" / "confluence.py",
        ROOT / "scripts" / "validate_document.py",
        ROOT / "scripts" / "test_confluence.py",
    ]
    for path in required:
        check(path.exists(), f"{path.relative_to(ROOT)} exists")

    adapters = [
        ROOT / "AGENTS.md",
        ROOT / "CLAUDE.md",
        ROOT / ".github" / "copilot-instructions.md",
        ROOT / ".clinerules" / "confluence-documents.md",
    ]
    for path in adapters:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            check("SKILL.md" in text, f"{path.relative_to(ROOT)} points to SKILL.md")

    for name in ("new-document", "publish-page", "audit-document"):
        path = ROOT / ".clinerules" / "workflows" / f"{name}.md"
        check(path.exists(), f"{path.relative_to(ROOT)} exists")

    router = ROOT / "SKILL.md"
    if router.exists():
        text = router.read_text(encoding="utf-8")
        frontmatter = split_frontmatter(text)
        check(frontmatter.get("name") == "confluence-documents", "root SKILL.md name is confluence-documents")
        check("No-Credential Fallback" in text, "root SKILL.md documents the no-credential fallback")
        check("Create Protocol" in text and "Update Protocol" in text, "root SKILL.md documents create and update protocols")
        for number in range(1, 13):
            check(f"skills/{number:02d}-" in text, f"root SKILL.md routes guide {number:02d}")


def check_hygiene() -> None:
    for path in ROOT.rglob("*"):
        if any(part in FORBIDDEN_DIRS for part in path.parts):
            if path.is_dir():
                fail(f"generated directory present: {path.relative_to(ROOT)}")
            continue
        if path.name == ".env":
            fail("no .env file is present")
        if path.suffix == ".html" and "storage" in path.name:
            fail(f"generated storage present outside .work: {path.relative_to(ROOT)}")
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".example", ""}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"possible secret in {path.relative_to(ROOT)}")
    if not failures:
        ok("hygiene: no secrets, generated storage, backups or cache directories")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the skill-confluence-documents repository contract.")
    parser.add_argument("--verbose", action="store_true", help="print every passing check")
    args = parser.parse_args(argv)

    try:
        guides = check_guides()
        check_related(guides)
        data = check_data(guides)
        if data:
            check_readme_matrix(data)
        check_templates()
        check_example()
        check_showcase()
        check_assets()
        check_adapters_routing()
        check_hygiene()
    except Exception as exc:  # noqa: BLE001 - the contract check must not crash silently
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.verbose:
        for message in passes:
            print(f"PASS  {message}")
    for message in failures:
        print(f"FAIL  {message}")
    print()
    print(f"{len(passes)} checks passed, {len(failures)} failed")
    if failures:
        return 1
    print("Repository contract satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
