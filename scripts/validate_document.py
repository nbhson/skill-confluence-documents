#!/usr/bin/env python3
"""validate_document.py - enterprise-format quality gate for Confluence documents.

Lints the Markdown source before it is converted or published. It enforces the
formatting contract this skill exists for: document control metadata, numbered
structure, tables over bullet walls, synced change logs, traceable requirement
IDs, accessible links/images, and readable paragraphs.

Usage:
    python3 validate_document.py docs/fds.md --profile fds
    python3 validate_document.py docs/fds.md --profile fds --min-score 90 --strict
    python3 validate_document.py docs/fds.md --json

Exit codes: 0 pass, 1 quality gate failed, 2 input/config error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from md2storage import (  # noqa: E402
    DIRECTIVE_RE,
    FENCE_RE,
    HEADING_RE,
    LIST_RE,
    TABLE_SEP_RE,
    TABLE_SINGLE_SEP_RE,
    frontmatter_list,
    parse_frontmatter,
    split_table_row,
)

# --------------------------------------------------------------------------- #
# Policy
# --------------------------------------------------------------------------- #

PROFILES: dict[str, list[str]] = {
    "fds": [
        "Purpose and Scope",
        "Stakeholders",
        "Functional Requirements",
        "Non-Functional Requirements",
        "Business Rules",
        "Data Model",
        "Integrations",
        "User Flows",
        "Acceptance Criteria",
        "Risks and Open Questions",
        "Change Log",
    ],
    "api": [
        "Overview",
        "Authentication",
        "Endpoints",
        "Data Models",
        "Error Handling",
        "Rate Limits",
        "Versioning",
        "Examples",
        "Change Log",
    ],
    "rfc": [
        "Summary",
        "Motivation",
        "Proposal",
        "Alternatives",
        "Risks",
        "Rollout",
        "Open Questions",
        "Change Log",
    ],
    "runbook": [
        "Overview",
        "Prerequisites",
        "Procedure",
        "Rollback",
        "Troubleshooting",
        "Escalation",
        "Change Log",
    ],
    "release": [
        "Summary",
        "Highlights",
        "Breaking Changes",
        "Migration",
        "Known Issues",
        "Change Log",
    ],
    "postmortem": [
        "Summary",
        "Impact",
        "Timeline",
        "Root Cause",
        "Resolution",
        "Action Items",
        "Lessons Learned",
        "Change Log",
    ],
    "adr": [
        "Summary",
        "Context",
        "Decision",
        "Consequences",
        "Alternatives",
        "Change Log",
    ],
    "fds-vi": [
        "Mục đích và phạm vi",
        "Các bên liên quan",
        "Yêu cầu chức năng",
        "Yêu cầu phi chức năng",
        "Quy tắc nghiệp vụ",
        "Mô hình dữ liệu",
        "Tích hợp",
        "Luồng người dùng",
        "Tiêu chí chấp nhận",
        "Rủi ro và câu hỏi mở",
        "Lịch sử thay đổi",
    ],
    "generic": [],
}

STATUS_VOCAB = {"draft", "in review", "approved", "deprecated", "superseded", "archived"}
CLASSIFICATION_VOCAB = {"public", "internal", "confidential", "restricted"}
BANNED_LINK_TEXT = {
    "here",
    "click here",
    "this link",
    "link",
    "this",
    "read more",
    "tại đây",
    "nhấn vào đây",
    "xem tại đây",
}
PLACEHOLDER_RE = re.compile(
    r"\b(TODO|TBD|FIXME|XXX)\b"
    r"|\bLorem ipsum\b"
    r"|(?<!/)\{[A-Za-z][A-Za-z0-9 _./-]{1,40}\}",
    re.IGNORECASE,
)
REQ_ID_RE = re.compile(r"\b(FR|NFR|BR|AC|DEC|RSK|OQ|INT|API|UX)-\d{3,4}\b")
DOC_ID_RE = re.compile(r"^[A-Z][A-Z0-9]{1,9}-[A-Z0-9]{2,12}-\d{3,4}$")
VERSION_RE = re.compile(r"^\d+\.\d+(\.\d+)?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

FILLER_PHRASES = [
    (r"\bin order to\b", "use 'to'"),
    (r"\bplease note that\b", "state the note directly"),
    (r"\bit should be noted\b", "state the note directly"),
    (r"\bas we all know\b", "remove"),
    (r"\bdue to the fact that\b", "use 'because'"),
    (r"\bat this point in time\b", "use 'now'"),
    (r"\bin the event that\b", "use 'if'"),
    (r"\bnhư đã biết\b", "bỏ cụm từ này"),
    (r"\bcó thể nói rằng\b", "bỏ cụm từ này"),
    (r"\bnhằm mục đích\b", "dùng 'để'"),
    (r"\bvà vân vân\b", "liệt kê đủ hoặc bỏ"),
    (r"\bvv\.", "liệt kê đủ hoặc bỏ"),
]

SEVERITY_POINTS = {"error": 10, "warn": 3, "info": 1}


@dataclass
class Finding:
    level: str
    rule: str
    line: int | None
    message: str
    hint: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Table:
    start: int
    end: int
    header: list[str]
    rows: list[tuple[int, list[str]]] = field(default_factory=list)


@dataclass
class Section:
    heading: "Heading"
    start: int
    end: int


@dataclass
class Heading:
    index: int
    level: int
    text: str
    anchor: str


@dataclass
class Model:
    lines: list[str]
    frontmatter: dict[str, Any]
    offset: int
    mask: list[bool]
    headings: list[Heading]
    tables: list[Table]
    sections: list[Section]

    def line_no(self, index: int) -> int:
        return index + 1 + self.offset


class Linter:
    def __init__(
        self,
        path: Path,
        text: str,
        profile: str,
        *,
        publish: bool = False,
        allow_placeholders: bool = False,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.path = path
        self.text = text
        self.profile = profile
        self.publish = publish
        self.allow_placeholders = allow_placeholders
        self.config = config or {}
        self.findings: list[Finding] = []
        self.model = self._build_model()
        self.metrics: dict[str, Any] = {}

    # -- model ------------------------------------------------------------- #

    def _build_model(self) -> Model:
        frontmatter, body, offset = parse_frontmatter(self.text)
        mask = fence_mask(body)
        headings: list[Heading] = []
        for index, line in enumerate(body):
            if mask[index]:
                continue
            match = HEADING_RE.match(line)
            if match:
                headings.append(
                    Heading(
                        index=index,
                        level=len(match.group(1)),
                        text=match.group(2).strip(),
                        anchor=match.group(3) or "",
                    )
                )
        tables = find_tables(body, mask)
        sections: list[Section] = []
        for position, heading in enumerate(headings):
            if heading.level != 2:
                continue
            end = len(body)
            for later in headings[position + 1 :]:
                if later.level <= 2:
                    end = later.index
                    break
            sections.append(Section(heading=heading, start=heading.index + 1, end=end))
        return Model(
            lines=body,
            frontmatter=frontmatter,
            offset=offset,
            mask=mask,
            headings=headings,
            tables=tables,
            sections=sections,
        )

    def add(self, level: str, rule: str, line: int | None, message: str, hint: str = "") -> None:
        self.findings.append(Finding(level, rule, line, message, hint))

    # -- helpers ----------------------------------------------------------- #

    def visible_lines(self) -> list[tuple[int, str]]:
        return [
            (index, line)
            for index, line in enumerate(self.model.lines)
            if not self.model.mask[index]
        ]

    def section_text(self, section: Section) -> str:
        return "\n".join(self.model.lines[section.start : section.end])

    def find_section(self, name: str) -> Section | None:
        wanted = normalize_heading(name)
        return next(
            (section for section in self.model.sections if normalize_heading(section.heading.text) == wanted),
            None,
        )

    from_text = staticmethod(lambda value: value)

    # -- rules ------------------------------------------------------------- #

    def run(self) -> list[Finding]:
        self.check_metadata()
        self.check_structure()
        self.check_required_sections()
        self.check_change_log()
        self.check_formatting()
        self.check_tables()
        self.check_content()
        self.check_links_and_images()
        self.check_accessibility()
        self.check_language()
        self.check_config()
        return self.findings

    def check_metadata(self) -> None:
        fm = self.model.frontmatter
        if not fm:
            self.add(
                "error",
                "meta.missing",
                1,
                "No document control frontmatter. Enterprise pages need doc_id, version, status, owner and updated.",
                "Add the YAML block from assets/templates/fds.md.",
            )
            return

        core = ["title", "doc_id", "version", "status", "owner", "updated"]
        for key in core:
            if not str(fm.get(key, "")).strip():
                self.add("error", f"meta.{key}", 1, f"Frontmatter is missing required field '{key}'.")

        if self.profile in ("fds", "fds-vi"):
            for key in ("jira", "reviewers", "space"):
                if not str(fm.get(key, "")).strip():
                    self.add(
                        "warn",
                        f"meta.{key}",
                        1,
                        f"FDS documents should declare '{key}' for traceability and publishing.",
                    )

        status = str(fm.get("status", "")).strip().lower()
        if status and status not in STATUS_VOCAB:
            self.add(
                "error",
                "meta.status",
                1,
                f"Status '{fm.get('status')}' is outside the controlled vocabulary ({', '.join(sorted(STATUS_VOCAB))}).",
            )

        def is_placeholder(value: str) -> bool:
            return bool(re.search(r"\{[^}]+\}", value)) and self.allow_placeholders

        version = str(fm.get("version", "")).strip()
        if version and not is_placeholder(version) and not VERSION_RE.match(version):
            self.add("error", "meta.version", 1, f"Version '{version}' must look like 1.0 or 1.0.0.")

        updated = str(fm.get("updated", "")).strip()
        if updated and not is_placeholder(updated) and not DATE_RE.match(updated):
            self.add("error", "meta.updated", 1, f"Updated date '{updated}' must be ISO YYYY-MM-DD.")

        doc_id = str(fm.get("doc_id", "")).strip()
        if doc_id and not is_placeholder(doc_id) and not DOC_ID_RE.match(doc_id):
            self.add(
                "warn",
                "meta.doc_id",
                1,
                f"Document ID '{doc_id}' does not follow PREFIX-DOMAIN-NNN (for example FDS-PAY-014).",
            )

        classification = str(fm.get("classification", "")).strip().lower()
        if classification and classification not in CLASSIFICATION_VOCAB:
            self.add(
                "warn",
                "meta.classification",
                1,
                f"Classification '{fm.get('classification')}' is outside {sorted(CLASSIFICATION_VOCAB)}.",
            )

        if self.publish:
            for key in ("space", "labels"):
                value = fm.get(key)
                if not value:
                    self.add("error", f"meta.{key}", 1, f"Publishing requires '{key}' in frontmatter.")
            if not frontmatter_list(fm, "labels"):
                self.add("warn", "meta.labels", 1, "Add at least the document type label (fds, api, rfc...).")

    def check_structure(self) -> None:
        headings = self.model.headings
        if not headings:
            self.add("error", "structure.headings", 1, "Document has no headings.")
            return

        h1 = [heading for heading in headings if heading.level == 1]
        if len(h1) > 1:
            self.add(
                "error",
                "structure.multiple-h1",
                self.model.line_no(h1[1].index),
                f"Found {len(h1)} H1 headings. Confluence renders the page title as H1; use one or none.",
            )
        title = str(self.model.frontmatter.get("title", "")).strip()
        if h1 and title and normalize_heading(h1[0].text) != normalize_heading(title):
            self.add(
                "warn",
                "structure.h1-title",
                self.model.line_no(h1[0].index),
                "H1 does not match the frontmatter title; the page title is already rendered by Confluence.",
            )

        previous: Heading | None = None
        for heading in headings:
            if previous and heading.level > previous.level + 1:
                self.add(
                    "error",
                    "structure.heading-skip",
                    self.model.line_no(heading.index),
                    f"Heading level jumps from H{previous.level} to H{heading.level} ('{heading.text}').",
                    "Use the next level down; never skip a level for visual size.",
                )
            previous = heading

        seen: dict[str, int] = {}
        for heading in headings:
            if heading.level != 2:
                continue
            key = normalize_heading(heading.text)
            if key in seen:
                self.add(
                    "error",
                    "structure.duplicate-section",
                    self.model.line_no(heading.index),
                    f"Section '{heading.text}' appears more than once (first at line {seen[key]}).",
                )
            else:
                seen[key] = self.model.line_no(heading.index)

        h2_count = len(self.model.sections)
        if h2_count < 3 and self.profile != "generic":
            self.add(
                "warn",
                "structure.too-few-sections",
                None,
                f"Only {h2_count} H2 sections; a professional specification usually has 6-12.",
            )
        if h2_count > 15:
            self.add(
                "warn",
                "structure.too-many-sections",
                None,
                f"{h2_count} H2 sections. Group related content or move detail into appendices.",
            )

        has_toc = any(
            re.match(r"^\s*\{\{toc(?::\d+)?\}\}\s*$", line)
            or re.match(r"^\s*:::\s*toc\b", line, re.IGNORECASE)
            for _, line in self.visible_lines()
        )
        if h2_count >= 6 and not has_toc:
            self.add(
                "warn",
                "structure.toc",
                None,
                f"{h2_count} H2 sections but no table of contents.",
                "Add {{toc}} after the document control table.",
            )

        if self.profile in ("fds", "fds-vi", "api", "rfc", "runbook", "release", "postmortem", "adr"):
            unnumbered = [
                section.heading.text
                for section in self.model.sections
                if not re.match(r"^\d+(\.\d+)*[.)]?\s+", section.heading.text)
                and not section.heading.text.lower().startswith(("appendix", "phụ lục", "phu luc"))
            ]
            if unnumbered:
                self.add(
                    "warn",
                    "structure.numbering",
                    None,
                    f"{len(unnumbered)} H2 section(s) are not numbered: {', '.join(unnumbered[:4])}.",
                    "Number H2 as '1. Purpose and Scope' so reviews can cite sections precisely.",
                )
            numbers = [
                int(re.match(r"^(\d+)", section.heading.text).group(1))
                for section in self.model.sections
                if re.match(r"^\d+", section.heading.text)
            ]
            if numbers and numbers != list(range(1, len(numbers) + 1)):
                self.add(
                    "warn",
                    "structure.numbering-sequence",
                    None,
                    f"Section numbers are not sequential: {numbers}.",
                )

    def check_required_sections(self) -> None:
        required = PROFILES.get(self.profile, [])
        if not required:
            return
        present = [normalize_heading(section.heading.text) for section in self.model.sections]
        for name in required:
            wanted = normalize_heading(name)
            if not any(wanted in heading or heading in wanted for heading in present):
                self.add(
                    "error",
                    "structure.required-section",
                    None,
                    f"Profile '{self.profile}' requires a '{name}' section.",
                    f"Copy the section structure from assets/templates/{self.profile}.md.",
                )

    def check_change_log(self) -> None:
        section = None
        for candidate in self.model.sections:
            normalized = normalize_heading(candidate.heading.text)
            if normalized in (
                "change log",
                "revision history",
                "document history",
                "lich su thay doi",
                "lich su phien ban",
            ):
                section = candidate
                break
        if section is None:
            self.add(
                "error" if self.profile != "generic" else "warn",
                "changelog.missing",
                None,
                "No Change Log (or Revision History) section.",
                "Every published revision needs a row: Version, Date, Author, Change, Jira.",
            )
            return

        tables = [
            table
            for table in self.model.tables
            if table.start >= section.start and table.end <= section.end
        ]
        if not tables:
            self.add(
                "error",
                "changelog.table",
                self.model.line_no(section.heading.index),
                "Change Log has no table.",
            )
            return

        table = tables[0]
        header = [normalize_heading(cell) for cell in table.header]
        if len(table.header) < 4:
            self.add(
                "warn",
                "changelog.columns",
                self.model.line_no(table.start),
                f"Change Log has {len(table.header)} columns; use at least Version, Date, Author, Change, Jira.",
            )
        required_groups = {
            "version": ("version", "phien ban"),
            "date": ("date", "ngay"),
            "author": ("author", "nguoi cap nhat", "tac gia"),
        }
        missing = [
            label
            for label, words in required_groups.items()
            if not any(word in cell for cell in header for word in words)
        ]
        if missing:
            self.add(
                "warn",
                "changelog.columns",
                self.model.line_no(table.start),
                f"Change Log header is missing: {', '.join(missing)}.",
            )
        if not table.rows:
            self.add("error", "changelog.empty", self.model.line_no(table.start), "Change Log has no entries.")

        version = str(self.model.frontmatter.get("version", "")).strip()
        if version and table.rows:
            first = table.rows[0][1]
            if first and first[0].strip().lower().lstrip("v") != version.lower().lstrip("v"):
                self.add(
                    "warn",
                    "changelog.version-drift",
                    self.model.line_no(table.rows[0][0]),
                    f"Latest change log version '{first[0]}' does not match frontmatter version '{version}'.",
                )

    def check_formatting(self) -> None:
        bullets = 0
        ordered_items = 0
        paragraphs = 0
        max_run = 0
        current_run = 0
        max_depth = 0

        table_lines = {index for table in self.model.tables for index in range(table.start, table.end + 1)}
        for index, line in enumerate(self.model.lines):
            if self.model.mask[index] or index in table_lines or not line.strip():
                current_run = 0
                continue
            if HEADING_RE.match(line):
                current_run = 0
                continue
            list_match = LIST_RE.match(line)
            if list_match:
                if list_match.group(2)[0].isdigit():
                    ordered_items += 1
                    current_run = 0
                    continue
                bullets += 1
                current_run += 1
                max_run = max(max_run, current_run)
                depth = len(list_match.group(1).replace("\t", "    ")) // 2
                max_depth = max(max_depth, depth)
                continue
            current_run = 0
            if (
                line.lstrip().startswith(">")
                or DIRECTIVE_RE.match(line)
                or line.strip() == ":::"
                or line.strip().startswith("{{")
            ):
                continue
            paragraphs += 1

        total = bullets + paragraphs
        ratio = bullets / total if total else 0.0
        self.metrics["bullet_ratio"] = round(ratio, 3)
        self.metrics["bullets"] = bullets
        self.metrics["ordered_items"] = ordered_items
        if ratio > 0.55:
            self.add(
                "error",
                "format.bullet-ratio",
                None,
                f"{ratio:.0%} of prose lines are bullets. This is a bullet wall, not a specification.",
                "Convert parallel facts into tables and keep bullets for sequences of three or fewer.",
            )
        elif ratio > 0.38:
            self.add(
                "warn",
                "format.bullet-ratio",
                None,
                f"{ratio:.0%} of prose lines are bullets; the budget is 35%.",
                "Prefer tables for requirements, decisions, risks and comparisons.",
            )
        if max_run > 8:
            self.add(
                "warn",
                "format.bullet-run",
                None,
                f"{max_run} consecutive bullet lines. Split into a table or add explanatory paragraphs.",
            )
        if max_depth > 2:
            self.add(
                "warn",
                "format.bullet-depth",
                None,
                f"Bullet nesting reaches level {max_depth + 1}; keep nesting to two levels.",
            )

        for section in self.model.sections:
            stats = self.section_stats(section)
            if (
                stats["bullets"] >= 3
                and stats["paragraphs"] == 0
                and not stats["has_table"]
                and not stats["has_callout"]
                and not stats["has_code"]
                and not stats["has_quote"]
            ):
                self.add(
                    "error",
                    "format.bullet-wall",
                    self.model.line_no(section.heading.index),
                    f"Section '{section.heading.text}' is a bullet-only list ({stats['bullets']} bullets, no prose or table).",
                    "Add an answer-first paragraph and convert parallel items into a table.",
                )

        self._check_paragraphs()
        self._check_heading_case()

    def section_stats(self, section: Section) -> dict[str, Any]:
        table_lines = {
            index
            for table in self.model.tables
            if table.start >= section.start and table.end <= section.end
            for index in range(table.start, table.end + 1)
        }
        bullets = paragraphs = 0
        has_callout = has_quote = has_code = False
        for index in range(section.start, section.end):
            line = self.model.lines[index]
            if table_lines and index in table_lines:
                continue
            if self.model.mask[index]:
                has_code = True
                continue
            if not line.strip() or HEADING_RE.match(line):
                continue
            if DIRECTIVE_RE.match(line) or line.strip() == ":::":
                has_callout = True
                continue
            if line.lstrip().startswith(">"):
                has_quote = True
                continue
            list_match = LIST_RE.match(line)
            if list_match:
                if not list_match.group(2)[0].isdigit():
                    bullets += 1
                continue
            if line.strip().startswith("{{"):
                continue
            paragraphs += 1
        return {
            "bullets": bullets,
            "paragraphs": paragraphs,
            "has_table": any(
                table.start >= section.start and table.end <= section.end
                for table in self.model.tables
            ),
            "has_callout": has_callout,
            "has_quote": has_quote,
            "has_code": has_code,
        }

    def _check_paragraphs(self) -> None:
        table_lines = {index for table in self.model.tables for index in range(table.start, table.end + 1)}
        batch: list[int] = []
        batches: list[list[int]] = []

        def flush() -> None:
            if batch:
                batches.append(batch.copy())
                batch.clear()

        for index, line in enumerate(self.model.lines):
            if (
                not line.strip()
                or self.model.mask[index]
                or index in table_lines
                or HEADING_RE.match(line)
                or LIST_RE.match(line)
                or DIRECTIVE_RE.match(line)
                or line.strip() == ":::"
                or line.lstrip().startswith(">")
                or line.strip().startswith("{{")
                or line.lstrip().startswith("<!--")
            ):
                flush()
                continue
            batch.append(index)
        flush()

        for group in batches:
            words = sum(len(self.model.lines[index].split()) for index in group)
            start = group[0]
            if words > 260:
                self.add(
                    "error",
                    "format.paragraph-length",
                    self.model.line_no(start),
                    f"Paragraph has {words} words. Split it into an answer-first paragraph plus a table or sub-sections.",
                )
            elif words > 180:
                self.add(
                    "warn",
                    "format.paragraph-length",
                    self.model.line_no(start),
                    f"Paragraph has {words} words; the budget is 180.",
                )

    def _check_heading_case(self) -> None:
        for heading in self.model.headings:
            text = heading.text
            if len(text) > 60:
                self.add(
                    "warn",
                    "format.heading-length",
                    self.model.line_no(heading.index),
                    f"Heading is {len(text)} characters; keep it under 60.",
                )
            words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
            if len(words) >= 4:
                capitalized = sum(1 for word in words if word[0].isupper() and not word.isupper())
                if capitalized / len(words) > 0.7:
                    self.add(
                        "warn",
                        "format.heading-case",
                        self.model.line_no(heading.index),
                        f"Heading '{text}' is title case; use sentence case.",
                    )
            if len(text) > 6 and text.isupper():
                self.add(
                    "warn",
                    "format.heading-caps",
                    self.model.line_no(heading.index),
                    f"Heading '{text}' is all caps; use sentence case.",
                )

    def check_tables(self) -> None:
        for table in self.model.tables:
            line = self.model.line_no(table.start)
            width = len(table.header)
            if width < 2:
                self.add("warn", "table.single-column", line, "Single-column table; use a paragraph or list instead.")
            if width > 10:
                self.add("warn", "table.wide", line, f"{width} columns; split the table or move detail into an appendix.")
            if any(not cell.strip() for cell in table.header):
                self.add("warn", "table.empty-header", line, "Table has an empty header cell.")
            duplicate_headers = {
                normalize_heading(cell)
                for cell in table.header
                if table.header.count(cell) > 1 and normalize_heading(cell)
            }
            if duplicate_headers:
                self.add(
                    "warn",
                    "table.duplicate-header",
                    line,
                    f"Duplicate column names: {', '.join(sorted(duplicate_headers))}.",
                )
            if not table.rows:
                self.add("warn", "table.empty", line, "Table has a header but no data rows.")

            empty_cells = 0
            total_cells = 0
            for row_line, cells in table.rows:
                if len(cells) != width:
                    self.add(
                        "error",
                        "table.column-mismatch",
                        self.model.line_no(row_line),
                        f"Row has {len(cells)} cells but the header has {width}.",
                    )
                for cell in cells:
                    total_cells += 1
                    if not cell.strip():
                        empty_cells += 1
                    elif len(cell.split()) > 80:
                        self.add(
                            "warn",
                            "table.cell-length",
                            self.model.line_no(row_line),
                            f"Table cell has {len(cell.split())} words; move prose out of the table.",
                        )
            if total_cells and empty_cells / total_cells > 0.25:
                self.add(
                    "warn",
                    "table.empty-cells",
                    line,
                    f"{empty_cells}/{total_cells} cells are empty; use an explicit em dash.",
                )

    def check_content(self) -> None:
        visible = [(index, line) for index, line in self.visible_lines()]
        text = "\n".join(line for _, line in visible)

        text_without_macros = re.sub(r"\{\{[^{}\n]+\}\}", "", text)
        if PLACEHOLDER_RE.search(text_without_macros):
            level = "info" if self.allow_placeholders else ("error" if self.publish else "warn")
            for index, line in visible:
                line_without_macros = re.sub(r"\{\{[^{}\n]+\}\}", "", line)
                match = PLACEHOLDER_RE.search(line_without_macros)
                if match:
                    self.add(
                        level,
                        "content.placeholder",
                        self.model.line_no(index),
                        f"Placeholder '{match.group(0)}' left in the document.",
                        "Resolve it before publishing; templates may keep placeholders during drafting.",
                    )
                    break

        ids: dict[str, list[int]] = {}
        for index, line in visible:
            for match in REQ_ID_RE.finditer(line):
                ids.setdefault(match.group(0), []).append(index)

        # Reusing an ID as a cross-reference is expected. Duplicates are only a
        # defect when two definitions claim the same ID: the first column of a
        # table, or two headings that both define a requirement.
        definition_duplicates: dict[str, list[int]] = {}
        for table in self.model.tables:
            seen_in_table: dict[str, int] = {}
            for row_line, cells in table.rows:
                if not cells:
                    continue
                candidate = cells[0].strip()
                if REQ_ID_RE.fullmatch(candidate):
                    if candidate in seen_in_table:
                        definition_duplicates.setdefault(candidate, []).append(row_line)
                    else:
                        seen_in_table[candidate] = row_line
        heading_definitions: dict[str, int] = {}
        for heading in self.model.headings:
            match = re.match(r"^((?:FR|NFR|BR|AC|DEC|RSK|OQ|INT|API|UX)-\d{3,4})\b", heading.text)
            if match:
                req_id = match.group(1)
                if req_id in heading_definitions:
                    definition_duplicates.setdefault(req_id, []).append(heading.index)
                else:
                    heading_definitions[req_id] = heading.index

        for req_id, occurrences in definition_duplicates.items():
            self.add(
                "error",
                "content.duplicate-id",
                self.model.line_no(occurrences[0]),
                f"Requirement ID '{req_id}' is defined more than once.",
                "IDs are immutable and unique; reference the existing item instead of redefining it.",
            )

        all_ids = set(ids)
        fr_ids = {req_id for req_id in all_ids if req_id.startswith("FR-")}
        ac_ids = {req_id for req_id in all_ids if req_id.startswith("AC-")}
        if fr_ids and not ac_ids:
            self.add(
                "warn",
                "content.no-acceptance-criteria",
                None,
                f"{len(fr_ids)} FR IDs but no AC IDs; every functional requirement needs testable acceptance criteria.",
            )
        if fr_ids and ac_ids:
            ac_section = self.find_section("Acceptance Criteria") or self.find_section(
                "Tiêu chí chấp nhận"
            )
            ac_text = self.section_text(ac_section) if ac_section else text
            uncovered = sorted(req_id for req_id in fr_ids if req_id not in ac_text)
            if uncovered:
                self.add(
                    "warn",
                    "content.traceability",
                    None,
                    f"{len(uncovered)} FR ID(s) are not referenced by an acceptance criterion: {', '.join(uncovered[:5])}.",
                )

        if self.profile in ("fds", "fds-vi"):
            fr_section = self.find_section("Functional Requirements")
            if fr_section and fr_ids:
                tables = [
                    table
                    for table in self.model.tables
                    if table.start >= fr_section.start and table.end <= fr_section.end
                ]
                if tables:
                    header = [normalize_heading(cell) for cell in tables[0].header]
                    if not any("jira" in cell or "ticket" in cell for cell in header):
                        self.add(
                            "warn",
                            "content.jira-column",
                            self.model.line_no(tables[0].start),
                            "Functional Requirements table has no Jira column; add the source issue key per requirement.",
                        )
                else:
                    self.add(
                        "warn",
                        "content.requirement-table",
                        self.model.line_no(fr_section.heading.index),
                        "Functional Requirements should open with a summary table (ID, Requirement, Priority, Jira, Status).",
                    )

        for index, line in visible:
            for pattern, hint in FILLER_PHRASES:
                if re.search(pattern, line, re.IGNORECASE):
                    self.add(
                        "info",
                        "content.filler",
                        self.model.line_no(index),
                        f"Filler phrase found: '{re.search(pattern, line, re.IGNORECASE).group(0)}'.",
                        hint,
                    )
                    break

        spaces_before_punctuation = [
            (index, line)
            for index, line in visible
            if re.search(r"\S\s+[,;:!?](?:\s|$)", line)
        ]
        if spaces_before_punctuation:
            index, _ = spaces_before_punctuation[0]
            self.add(
                "info",
                "content.punctuation-spacing",
                self.model.line_no(index),
                f"{len(spaces_before_punctuation)} line(s) have a space before punctuation.",
            )

        self.metrics["requirement_ids"] = len(all_ids)
        self.metrics["h2_sections"] = len(self.model.sections)
        self.metrics["headings"] = len(self.model.headings)
        self.metrics["tables"] = len(self.model.tables)
        self.metrics["words"] = len(re.findall(r"\b\w+\b", text))

    def check_links_and_images(self) -> None:
        for index, line in self.visible_lines():
            if self.model.mask[index]:
                continue
            for match in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", line):
                alt = match.group(1).strip()
                if not alt:
                    self.add(
                        "error",
                        "a11y.image-alt",
                        self.model.line_no(index),
                        "Image has no alt text.",
                        "Describe what the image shows and the conclusion a reader should draw.",
                    )
                elif len(alt.split()) < 3 or alt.lower() in {"image", "screenshot", "diagram", "picture"}:
                    self.add(
                        "warn",
                        "a11y.image-alt",
                        self.model.line_no(index),
                        f"Alt text '{alt}' is not descriptive.",
                    )
            for match in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)]*)\)", line):
                label = match.group(1).strip()
                href = match.group(2).strip()
                if label.lower() in BANNED_LINK_TEXT:
                    self.add(
                        "warn",
                        "a11y.link-text",
                        self.model.line_no(index),
                        f"Link text '{label}' is not descriptive; name the destination.",
                    )
                if not href:
                    self.add("error", "link.empty", self.model.line_no(index), f"Link '{label}' has no target.")
                elif href.startswith("http://"):
                    self.add("info", "link.http", self.model.line_no(index), "Prefer HTTPS for external links.")
                if len(label.split()) > 12:
                    self.add(
                        "info",
                        "a11y.link-length",
                        self.model.line_no(index),
                        "Link text is longer than 12 words; keep it to the destination name.",
                    )

    def check_accessibility(self) -> None:
        for index, line in self.visible_lines():
            if re.search(r"[✅❌⚠️🔥👍👎]", line):
                self.add(
                    "info",
                    "a11y.emoji-status",
                    self.model.line_no(index),
                    "Emoji used as status; use {{status:colour|Label}} so the meaning is text, not color.",
                )
                break
            if re.fullmatch(r"\s*\*\*[^*]{4,}\*\*\s*", line):
                self.add(
                    "info",
                    "a11y.bold-heading",
                    self.model.line_no(index),
                    "Bold line looks like a heading; use a real heading level for navigation.",
                )
                break

    def check_language(self) -> None:
        text = "\n".join(line for _, line in self.visible_lines())
        vietnamese = bool(re.search(r"[ăâđêôơưĂÂĐÊÔƠƯ]", text))
        self.metrics["language"] = "vi" if vietnamese else "en"
        if not vietnamese:
            return

        for index, line in self.visible_lines():
            if re.search(r"\s+[,;:!?](?:\s|$)", line):
                self.add(
                    "info",
                    "vi.punctuation",
                    self.model.line_no(index),
                    "Vietnamese typography has no space before punctuation.",
                )
                break
        ampersands = [
            (index, line)
            for index, line in self.visible_lines()
            if "&" in line and not re.search(r"https?://\S*&", line) and not line.strip().startswith("|")
        ]
        if ampersands:
            self.add(
                "info",
                "vi.ampersand",
                self.model.line_no(ampersands[0][0]),
                f"{len(ampersands)} line(s) use '&' in prose; write 'và' in Vietnamese sentences.",
            )

    def check_config(self) -> None:
        banned = self.config.get("bannedPhrases", [])
        for phrase in banned:
            if not isinstance(phrase, str) or not phrase.strip():
                continue
            for index, line in self.visible_lines():
                if phrase.lower() in line.lower():
                    self.add(
                        "warn",
                        "config.banned-phrase",
                        self.model.line_no(index),
                        f"Banned phrase from project config: '{phrase}'.",
                    )
                    break

        terminology = self.config.get("terminology", [])
        for entry in terminology:
            if not isinstance(entry, dict):
                continue
            use = str(entry.get("use", "")).strip()
            avoid = entry.get("avoid", [])
            if isinstance(avoid, str):
                avoid = [avoid]
            for variant in avoid:
                if not str(variant).strip():
                    continue
                for index, line in self.visible_lines():
                    if str(variant).lower() in line.lower():
                        self.add(
                            "warn",
                            "config.terminology",
                            self.model.line_no(index),
                            f"Use '{use}' instead of '{variant}'.",
                        )
                        break

    # -- result ------------------------------------------------------------ #

    def score(self) -> tuple[int, str]:
        deductions = sum(
            SEVERITY_POINTS.get(finding.level, 1) for finding in self.findings
        )
        score = max(0, 100 - deductions)
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        return score, grade


# --------------------------------------------------------------------------- #
# Model helpers
# --------------------------------------------------------------------------- #


def normalize_heading(text: str) -> str:
    value = re.sub(r"^\s*\d+(\.\d+)*[.)]?\s+", "", text)
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("&", " and ")
    value = re.sub(r"\(.*?\)", " ", value)
    value = re.sub(r"[^A-Za-z0-9 ]+", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def fence_mask(lines: list[str]) -> list[bool]:
    mask = [False] * len(lines)
    index = 0
    while index < len(lines):
        match = FENCE_RE.match(lines[index])
        if not match:
            index += 1
            continue
        marker = match.group(2)
        mask[index] = True
        index += 1
        while index < len(lines):
            mask[index] = True
            if lines[index].strip().startswith(marker):
                index += 1
                break
            index += 1
    return mask


def is_table_start(lines: list[str], index: int) -> bool:
    if "|" not in lines[index] or index + 1 >= len(lines):
        return False
    separator = lines[index + 1]
    return bool(TABLE_SEP_RE.match(separator) or TABLE_SINGLE_SEP_RE.match(separator))


def find_tables(lines: list[str], mask: list[bool]) -> list[Table]:
    tables: list[Table] = []
    index = 0
    while index < len(lines) - 1:
        if mask[index] or not is_table_start(lines, index):
            index += 1
            continue
        header = split_table_row(lines[index])
        rows: list[tuple[int, list[str]]] = []
        cursor = index + 2
        while (
            cursor < len(lines)
            and not mask[cursor]
            and lines[cursor].strip()
            and "|" in lines[cursor]
        ):
            rows.append((cursor, split_table_row(lines[cursor])))
            cursor += 1
        tables.append(Table(start=index, end=cursor - 1, header=header, rows=rows))
        index = cursor
    return tables


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        candidate = Path(".confluence-doc.json")
        if candidate.exists():
            path = candidate
    if path is None:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read config {path}: {exc}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def format_human(
    path: Path, profile: str, score: int, grade: str, findings: list[Finding], metrics: dict[str, Any]
) -> str:
    counts = {
        level: sum(1 for finding in findings if finding.level == level)
        for level in ("error", "warn", "info")
    }
    lines = [
        f"Confluence document review - {path}",
        f"Profile: {profile}    Score: {score}/100 ({grade})    "
        f"Errors: {counts['error']}    Warnings: {counts['warn']}    Info: {counts['info']}",
        "",
    ]
    if findings:
        lines.append(f"{'LEVEL':<6} {'LINE':>5}  {'RULE':<30} MESSAGE")
        lines.append("-" * 110)
        for finding in sorted(
            findings,
            key=lambda item: (
                {"error": 0, "warn": 1, "info": 2}[item.level],
                item.line or 0,
            ),
        ):
            location = str(finding.line) if finding.line else "-"
            lines.append(
                f"{finding.level.upper():<6} {location:>5}  {finding.rule:<30} {finding.message}"
            )
            if finding.hint:
                lines.append(f"{'':<6} {'':>5}  {'':<30} -> {finding.hint}")
        lines.append("")
    else:
        lines.append("No findings. The document meets the formatting contract.")
        lines.append("")
    lines.append(
        "Metrics: "
        + ", ".join(
            [
                f"words={metrics.get('words', 0)}",
                f"h2={metrics.get('h2_sections', 0)}",
                f"tables={metrics.get('tables', 0)}",
                f"bullets={metrics.get('bullets', 0)}",
                f"bullet_ratio={metrics.get('bullet_ratio', 0):.0%}",
                f"requirements={metrics.get('requirement_ids', 0)}",
                f"language={metrics.get('language', 'en')}",
            ]
        )
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint Confluence Markdown against the enterprise document contract."
    )
    parser.add_argument("path", type=Path, help="Markdown document to review")
    parser.add_argument(
        "--profile",
        default="fds",
        choices=sorted(PROFILES),
        help="Document type contract to enforce (default: fds)",
    )
    parser.add_argument("--min-score", type=int, default=80, help="fail below this score (default: 80)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--publish", action="store_true", help="publication gate: placeholders and labels are errors")
    parser.add_argument("--allow-placeholders", action="store_true", help="allow {Owner}/TODO while drafting")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--config", type=Path, help="project config (default: .confluence-doc.json)")
    parser.add_argument("--ignore", default="", help="comma-separated rule IDs to ignore")
    parser.add_argument("--fail-on-warnings", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"ERROR: file not found: {args.path}", file=sys.stderr)
        return 2
    try:
        text = args.path.read_text(encoding="utf-8")
        config = load_config(args.config)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    ignore = {rule.strip() for rule in args.ignore.split(",") if rule.strip()}
    linter = Linter(
        args.path,
        text,
        args.profile,
        publish=args.publish,
        allow_placeholders=args.allow_placeholders,
        config=config,
    )
    findings = linter.run()
    if ignore:
        findings = [finding for finding in findings if finding.rule not in ignore]
    linter.findings = findings
    score, grade = linter.score()
    counts = {level: sum(1 for finding in findings if finding.level == level) for level in ("error", "warn", "info")}

    if args.json:
        print(
            json.dumps(
                {
                    "file": str(args.path),
                    "profile": args.profile,
                    "score": score,
                    "grade": grade,
                    "counts": counts,
                    "metrics": linter.metrics,
                    "findings": [finding.as_dict() for finding in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(format_human(args.path, args.profile, score, grade, findings, linter.metrics))

    failed = (
        counts["error"] > 0
        or score < args.min_score
        or ((args.strict or args.fail_on_warnings) and counts["warn"] > 0)
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
