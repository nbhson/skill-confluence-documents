#!/usr/bin/env python3
"""md2storage.py - convert enterprise Markdown into Confluence Cloud storage XHTML.

The dialect is intentionally small and reviewable. It covers the containers a
professional specification needs (panels, status lozenges, Jira links, tables,
code, task lists, expandable detail) and refuses unknown macros so a typo never
publishes as literal text.

Usage:
    python3 md2storage.py input.md -o page.storage.html --check
    python3 md2storage.py input.md --manifest page.json
    python3 md2storage.py --help

Exit codes: 0 success, 1 conversion/validation error, 2 usage error.
"""

from __future__ import annotations

import argparse
import html
import html.entities
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

AC_NS = "http://atlassian.com/content"
RI_NS = "http://atlassian.com/resource/identifier"

STATUS_COLOURS = {
    "grey": "Grey",
    "gray": "Grey",
    "red": "Red",
    "yellow": "Yellow",
    "green": "Green",
    "blue": "Blue",
    "purple": "Purple",
}

STATUS_BY_DOC_STATUS = {
    "draft": "Grey",
    "in review": "Yellow",
    "in-review": "Yellow",
    "review": "Yellow",
    "approved": "Green",
    "deprecated": "Red",
    "superseded": "Purple",
    "archived": "Grey",
}

CALLOUT_MACROS = {
    "info": "info",
    "note": "note",
    "tip": "tip",
    "warning": "warning",
    "caution": "warning",
    "panel": "panel",
    "expand": "expand",
    "details": "expand",
    "quote": "quote",
}

HEADING_RE = re.compile(
    r"^(#{1,6})\s+(.*?)(?:\s+\{#([A-Za-z0-9][A-Za-z0-9_-]*)\})?\s*$"
)
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^\s`]*)?\s*(.*)$")
DIRECTIVE_RE = re.compile(r"^:::\s*([A-Za-z][A-Za-z0-9_-]*)(?:\s+(.*))?$")
DIRECTIVE_END_RE = re.compile(r"^:::\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
TABLE_SINGLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*\|?\s*$")
TASK_RE = re.compile(r"^\[( |x|X)\]\s+(.*)$")
LINK_RE = re.compile(
    r"""
    (?P<macro>\{\{[^{}\n]+\}\})
  | (?P<code>(?P<ticks>`+)(?P<codetext>.+?)(?P=ticks))
  | (?P<image>!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+"(?P<imgtitle>[^"]*)")?\))
  | (?P<link>\[(?P<ltext>[^\]]+)\]\((?P<href>[^)\s]+)(?:\s+"(?P<linktitle>[^"]*)")?\))
    """,
    re.VERBOSE,
)


class ConversionError(ValueError):
    """Raised when the Markdown cannot be converted safely."""


# --------------------------------------------------------------------------- #
# Escaping and frontmatter
# --------------------------------------------------------------------------- #


def esc_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_attr(value: str) -> str:
    return html.escape(value, quote=True)


def cdata(value: str) -> str:
    # A CDATA section cannot contain "]]>"; split it across two sections.
    return "<![CDATA[" + value.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_only = re.sub(r"[^\w\s-]", "", ascii_only).strip().lower()
    return re.sub(r"[\s_]+", "-", ascii_only)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], list[str], int]:
    """Parse the small YAML subset used by document templates.

    Supported values: scalars, inline lists ("[a, b]") and block lists
    ("key:" followed by "  - item"). Nested objects are deliberately rejected.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines, 0

    end: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() in ("---", "..."):
            end = index
            break
    if end is None:
        raise ConversionError("frontmatter opened with '---' but is never closed")

    data: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        stripped = raw.strip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current_list_key is None:
                raise ConversionError(f"frontmatter list item without a key: {stripped!r}")
            data.setdefault(current_list_key, [])
            if not isinstance(data[current_list_key], list):
                raise ConversionError(f"frontmatter key {current_list_key!r} mixes scalar and list")
            data[current_list_key].append(_unquote(stripped[2:].strip()))
            continue
        if ":" not in stripped:
            raise ConversionError(f"frontmatter line is not 'key: value': {stripped!r}")
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            raise ConversionError(f"frontmatter line has an empty key: {stripped!r}")
        current_list_key = None
        if not value:
            current_list_key = key
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            data[key] = [
                _unquote(item.strip())
                for item in value[1:-1].split(",")
                if item.strip()
            ]
        else:
            data[key] = _unquote(value)

    return data, lines[end + 1 :], end + 1


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        if value[0] == '"':
            return value[1:-1].replace('\\"', '"').replace("\\n", "\n")
        return value[1:-1].replace("''", "'")
    return value


def frontmatter_list(fm: dict[str, Any], key: str) -> list[str]:
    value = fm.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value.strip():
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


# --------------------------------------------------------------------------- #
# Inline rendering
# --------------------------------------------------------------------------- #


class InlineRenderer:
    def __init__(
        self,
        frontmatter: dict[str, Any],
        *,
        lenient: bool = False,
        mermaid_macro: str = "mermaid",
    ) -> None:
        self.fm = frontmatter
        self.lenient = lenient
        self.mermaid_macro = mermaid_macro

    def render(self, text: str) -> str:
        if "\x00" in text or "\x01" in text:
            raise ConversionError("input contains reserved control characters (NUL / SOH)")

        tokens: list[str] = []

        def stash(fragment: str) -> str:
            tokens.append(fragment)
            return f"\x00{len(tokens) - 1}\x00"

        pieces: list[str] = []
        position = 0
        for match in LINK_RE.finditer(text):
            pieces.append(esc_text(text[position : match.start()]))
            if match.group("macro"):
                pieces.append(stash(self._macro(match.group("macro"))))
            elif match.group("code"):
                code = match.group("codetext").strip()
                pieces.append(stash(f"<code>{esc_text(code)}</code>"))
            elif match.group("image"):
                pieces.append(
                    stash(
                        self._image(
                            match.group("alt"),
                            match.group("src"),
                            match.group("imgtitle") or "",
                        )
                    )
                )
            elif match.group("link"):
                pieces.append(
                    stash(
                        self._link(
                            match.group("ltext"),
                            match.group("href"),
                            match.group("linktitle") or "",
                        )
                    )
                )
            position = match.end()
        pieces.append(esc_text(text[position:]))
        rendered = "".join(pieces)

        rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered, flags=re.S)
        rendered = re.sub(r"~~(.+?)~~", r"<del>\1</del>", rendered, flags=re.S)
        rendered = re.sub(
            r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])",
            r"<em>\1</em>",
            rendered,
            flags=re.S,
        )
        rendered = rendered.replace("\x01", "<br />")

        def restore(match: re.Match[str]) -> str:
            return tokens[int(match.group(1))]

        while "\x00" in rendered:
            rendered = re.sub(r"\x00(\d+)\x00", restore, rendered)
        return rendered

    # -- links and images -------------------------------------------------- #

    def _link(self, label: str, href: str, title: str) -> str:
        label_html = self.render(label)
        title_attr = f' title="{esc_attr(title)}"' if title else ""
        if href.startswith("#"):
            anchor = href[1:]
            return (
                f'<ac:link ac:anchor="{esc_attr(anchor)}">'
                f"<ac:plain-text-link-body>{cdata(label)}</ac:plain-text-link-body>"
                f"</ac:link>"
            )
        return f'<a href="{esc_attr(href)}"{title_attr}>{label_html}</a>'

    def _image(self, alt: str, src: str, title: str) -> str:
        if src.startswith("attachment:"):
            filename = src[len("attachment:") :]
            resource = f'<ri:attachment ri:filename="{esc_attr(filename)}" />'
        elif re.match(r"^https?://", src):
            resource = f'<ri:url ri:value="{esc_attr(src)}" />'
        else:
            resource = f'<ri:attachment ri:filename="{esc_attr(src)}" />'
        title_attr = f' ac:title="{esc_attr(title)}"' if title else ""
        return f'<ac:image ac:alt="{esc_attr(alt)}"{title_attr}>{resource}</ac:image>'

    # -- macros ------------------------------------------------------------ #

    def _macro(self, raw: str) -> str:
        expression = raw[2:-2].strip()
        if not expression:
            raise ConversionError("empty macro '{{}}'")
        name, separator, argument = expression.partition(":")
        name = name.strip().lower()
        argument = argument.strip() if separator else ""

        if name == "status":
            colour, _, label = argument.partition("|")
            if not label.strip():
                raise ConversionError(
                    "status macro needs a colour and a label: {{status:green|Approved}}"
                )
            return self._status(colour.strip(), label.strip())
        if name == "jira":
            return self._jira(argument)
        if name == "toc":
            max_level = argument or "3"
            if not max_level.isdigit() or not 2 <= int(max_level) <= 6:
                raise ConversionError("toc max level must be a number between 2 and 6")
            return (
                '<ac:structured-macro ac:name="toc">'
                '<ac:parameter ac:name="minLevel">2</ac:parameter>'
                f'<ac:parameter ac:name="maxLevel">{max_level}</ac:parameter>'
                '<ac:parameter ac:name="type">flat</ac:parameter>'
                "</ac:structured-macro>"
            )
        if name == "children":
            return '<ac:structured-macro ac:name="children"></ac:structured-macro>'
        if name == "include":
            space, title = "", argument
            if ":" in argument:
                space, title = (part.strip() for part in argument.split(":", 1))
            if not title:
                raise ConversionError("include macro needs a page title: {{include:PAGE}}")
            page = f'<ri:page ri:content-title="{esc_attr(title)}"'
            if space:
                page += f' ri:space-key="{esc_attr(space)}"'
            page += " />"
            return (
                '<ac:structured-macro ac:name="include">'
                f'<ac:parameter ac:name="">{page}</ac:parameter>'
                "</ac:structured-macro>"
            )
        if name == "anchor":
            if not argument:
                raise ConversionError("anchor macro needs a name: {{anchor:section-id}}")
            return (
                '<ac:structured-macro ac:name="anchor">'
                f'<ac:parameter ac:name="">{esc_text(argument)}</ac:parameter>'
                "</ac:structured-macro>"
            )
        if name == "meta":
            return self.render_meta()
        if name == "mermaid":
            if not argument:
                raise ConversionError("mermaid macro needs a diagram body, use a fenced block")
            return self._mermaid(argument)
        if self.lenient:
            return esc_text(raw)
        raise ConversionError(
            f"unknown macro '{{{{{expression}}}}}'. "
            "Use a fenced 'storage' block for raw XHTML or --lenient to keep it literal."
        )

    def _status(self, colour: str, label: str) -> str:
        mapped = STATUS_COLOURS.get(colour.lower())
        if mapped is None:
            raise ConversionError(
                f"unknown status colour {colour!r}; use grey, red, yellow, green, blue or purple"
            )
        return (
            '<ac:structured-macro ac:name="status">'
            f'<ac:parameter ac:name="colour">{mapped}</ac:parameter>'
            f'<ac:parameter ac:name="title">{esc_text(label)}</ac:parameter>'
            "</ac:structured-macro>"
        )

    def _jira(self, argument: str) -> str:
        parts = [part.strip() for part in argument.split("|")]
        key = parts[0] if parts else ""
        if not key:
            raise ConversionError("jira macro needs an issue key: {{jira:PAY-123}}")
        parameters = f'<ac:parameter ac:name="key">{esc_text(key)}</ac:parameter>'
        if len(parts) > 1 and parts[1]:
            parameters += f'<ac:parameter ac:name="serverId">{esc_text(parts[1])}</ac:parameter>'
        return f'<ac:structured-macro ac:name="jira">{parameters}</ac:structured-macro>'

    def _mermaid(self, body: str) -> str:
        return (
            f'<ac:structured-macro ac:name="{esc_attr(self.mermaid_macro)}">'
            f"<ac:plain-text-body>{cdata(body)}</ac:plain-text-body>"
            "</ac:structured-macro>"
        )

    # -- document control table ------------------------------------------- #

    def render_meta(self) -> str:
        fm = self.fm

        def value(key: str) -> str:
            raw = fm.get(key, "")
            if isinstance(raw, list):
                return ", ".join(str(item) for item in raw)
            return str(raw).strip()

        status = value("status")
        status_html = (
            self._status(
                str(fm.get("status_color") or STATUS_BY_DOC_STATUS.get(status.lower(), "Grey")),
                status,
            )
            if status
            else "&mdash;"
        )
        jira = value("jira")
        jira_html = self._jira(jira) if jira else "&mdash;"

        rows = [
            ("Document ID", esc_text(value("doc_id") or "&mdash;")),
            ("Version", esc_text(value("version") or "&mdash;")),
            ("Status", status_html),
            ("Classification", esc_text(value("classification") or "Internal")),
            ("Owner", esc_text(value("owner") or "&mdash;")),
            ("Reviewers", esc_text(value("reviewers") or "&mdash;")),
            ("Jira epic", jira_html),
            ("Last updated", esc_text(value("updated") or "&mdash;")),
        ]

        cells: list[str] = []
        for index in range(0, len(rows), 2):
            left_label, left_value = rows[index]
            right_label, right_value = rows[index + 1]
            cells.append(
                f"<tr><th>{left_label}</th><td>{left_value}</td>"
                f"<th>{right_label}</th><td>{right_value}</td></tr>"
            )
        return "<table><tbody>" + "".join(cells) + "</tbody></table>"


# --------------------------------------------------------------------------- #
# Block rendering
# --------------------------------------------------------------------------- #


def split_table_row(line: str) -> list[str]:
    """Split a table row on pipes that are not escaped, in code, or in a macro."""
    stripped = line.strip()
    cells: list[str] = []
    buffer: list[str] = []
    index = 0
    brace_depth = 0
    in_code = False
    while index < len(stripped):
        char = stripped[index]
        if char == "\\" and index + 1 < len(stripped) and stripped[index + 1] == "|":
            buffer.append("|")
            index += 2
            continue
        if stripped.startswith("{{", index):
            brace_depth += 1
            buffer.append("{{")
            index += 2
            continue
        if stripped.startswith("}}", index):
            brace_depth = max(0, brace_depth - 1)
            buffer.append("}}")
            index += 2
            continue
        if char == "`":
            in_code = not in_code
        if char == "|" and brace_depth == 0 and not in_code:
            cells.append("".join(buffer).strip())
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1
    cells.append("".join(buffer).strip())
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


class Converter:
    def __init__(
        self,
        frontmatter: dict[str, Any],
        *,
        lenient: bool = False,
        mermaid_macro: str = "mermaid",
        auto_meta: bool = True,
        fragment: bool = False,
    ) -> None:
        self.fm = frontmatter
        self.inline = InlineRenderer(
            frontmatter, lenient=lenient, mermaid_macro=mermaid_macro
        )
        self.auto_meta = auto_meta
        self.fragment = fragment
        self.task_id = 0

    def render(self, lines: list[str], *, nested: bool = False) -> str:
        blocks: list[str] = []
        index = 0
        has_meta_source = any(
            re.fullmatch(r"\s*\{\{meta\}\}\s*", line)
            or re.fullmatch(r"\s*:::\s*meta\s*", line, re.IGNORECASE)
            for line in lines
        )
        while index < len(lines):
            line = lines[index]

            if not line.strip():
                index += 1
                continue

            if line.lstrip().startswith("<!--"):
                raw, index = self._consume_comment(lines, index)
                blocks.append(raw)
                continue

            heading = HEADING_RE.match(line)
            if heading:
                level = len(heading.group(1))
                heading_text = heading.group(2).strip()
                anchor = heading.group(3)
                anchor_html = (
                    '<ac:structured-macro ac:name="anchor">'
                    f'<ac:parameter ac:name="">{esc_text(anchor)}</ac:parameter>'
                    "</ac:structured-macro>"
                    if anchor
                    else ""
                )
                blocks.append(
                    f"<h{level}>{anchor_html}{self.inline.render(heading_text)}</h{level}>"
                )
                index += 1
                continue

            fence = FENCE_RE.match(line)
            if fence:
                block, index = self._consume_fence(lines, index, fence)
                blocks.append(block)
                continue

            directive = DIRECTIVE_RE.match(line)
            if directive:
                block, index = self._consume_directive(
                    lines, index, directive.group(1).lower(), (directive.group(2) or "").strip()
                )
                blocks.append(block)
                continue

            standalone_macro = re.fullmatch(r"\s*\{\{[^{}\n]+\}\}\s*", line)
            if standalone_macro:
                blocks.append(self.inline.render(line.strip()))
                index += 1
                continue

            if self._is_table_start(lines, index):
                block, index = self._consume_table(lines, index)
                blocks.append(block)
                continue

            if re.match(r"^\s*(---+|\*\*\*+|___+)\s*$", line):
                blocks.append("<hr />")
                index += 1
                continue

            if line.lstrip().startswith(">"):
                block, index = self._consume_blockquote(lines, index)
                blocks.append(block)
                continue

            if LIST_RE.match(line):
                block, index = self._consume_list(lines, index)
                blocks.append(block)
                continue

            block, index = self._consume_paragraph(lines, index)
            blocks.append(block)

        document = "\n".join(blocks)
        if (
            self.auto_meta
            and not nested
            and not self.fragment
            and not has_meta_source
            and self.fm
            and "<th>Document ID</th>" not in document
        ):
            document = self.inline.render_meta() + "\n" + document
        if not document.strip():
            raise ConversionError("document is empty after conversion")
        return document

    # -- block consumers --------------------------------------------------- #

    @staticmethod
    def _consume_comment(lines: list[str], index: int) -> tuple[str, int]:
        buffer: list[str] = []
        while index < len(lines):
            buffer.append(lines[index])
            if "-->" in lines[index]:
                index += 1
                break
            index += 1
        else:
            raise ConversionError("unterminated HTML comment")
        return "\n".join(buffer), index

    def _consume_fence(
        self, lines: list[str], index: int, fence: re.Match[str]
    ) -> tuple[str, int]:
        marker = fence.group(2)
        info = (fence.group(3) or "").strip().lower()
        remainder = (fence.group(4) or "").strip()
        attributes = dict(re.findall(r'(\w+)="([^"]*)"', remainder))
        start = index + 1
        body: list[str] = []
        index = start
        while index < len(lines):
            if lines[index].strip().startswith(marker):
                index += 1
                break
            body.append(lines[index])
            index += 1
        else:
            raise ConversionError(f"unterminated fenced block starting with {marker}")

        content = "\n".join(body)
        if info in ("storage", "confluence", "xhtml"):
            return content, index
        if info == "mermaid":
            return self.inline._mermaid(content), index
        if info == "plantuml":
            return (
                '<ac:structured-macro ac:name="plantuml">'
                f"<ac:plain-text-body>{cdata(content)}</ac:plain-text-body>"
                "</ac:structured-macro>"
            ), index

        parameters = ""
        language = info or attributes.get("language", "")
        if language:
            parameters += (
                f'<ac:parameter ac:name="language">{esc_text(language)}</ac:parameter>'
            )
        title = attributes.get("title", "")
        if title:
            parameters += f'<ac:parameter ac:name="title">{esc_text(title)}</ac:parameter>'
        return (
            f'<ac:structured-macro ac:name="code">{parameters}'
            f"<ac:plain-text-body>{cdata(content)}</ac:plain-text-body>"
            "</ac:structured-macro>"
        ), index

    def _consume_directive(
        self, lines: list[str], index: int, name: str, argument: str
    ) -> tuple[str, int]:
        if name not in CALLOUT_MACROS:
            raise ConversionError(
                f"unknown directive ':::{name}'. Supported: {', '.join(sorted(CALLOUT_MACROS))}"
            )

        depth = 1
        inner: list[str] = []
        index += 1
        while index < len(lines):
            if DIRECTIVE_END_RE.match(lines[index]):
                depth -= 1
                if depth == 0:
                    index += 1
                    break
                inner.append(lines[index])
            elif DIRECTIVE_RE.match(lines[index]):
                depth += 1
                inner.append(lines[index])
            else:
                inner.append(lines[index])
            index += 1
        else:
            raise ConversionError(f"unterminated directive ':::{name}'")

        body = self.render(inner, nested=True)
        macro = CALLOUT_MACROS[name]
        if macro == "quote":
            return f"<blockquote>{body}</blockquote>", index
        if macro == "panel":
            title = (
                f'<ac:parameter ac:name="title">{esc_text(argument)}</ac:parameter>'
                if argument
                else ""
            )
            return (
                f'<ac:structured-macro ac:name="panel">{title}'
                f"<ac:rich-text-body>{body}</ac:rich-text-body>"
                "</ac:structured-macro>"
            ), index
        if macro == "expand":
            title = (
                f'<ac:parameter ac:name="title">{esc_text(argument)}</ac:parameter>'
                if argument
                else ""
            )
            return (
                f'<ac:structured-macro ac:name="expand">{title}'
                f"<ac:rich-text-body>{body}</ac:rich-text-body>"
                "</ac:structured-macro>"
            ), index
        return (
            f'<ac:structured-macro ac:name="{macro}">'
            f"<ac:rich-text-body>{body}</ac:rich-text-body>"
            "</ac:structured-macro>"
        ), index

    @staticmethod
    def _is_table_start(lines: list[str], index: int) -> bool:
        if "|" not in lines[index]:
            return False
        if index + 1 >= len(lines):
            return False
        separator = lines[index + 1]
        return bool(TABLE_SEP_RE.match(separator) or TABLE_SINGLE_SEP_RE.match(separator))

    def _consume_table(self, lines: list[str], index: int) -> tuple[str, int]:
        header = self._split_row(lines[index])
        index += 2  # header + separator
        rows: list[list[str]] = []
        while index < len(lines):
            line = lines[index]
            if not line.strip() or "|" not in line:
                break
            if DIRECTIVE_END_RE.match(line):
                break
            rows.append(self._split_row(line))
            index += 1

        width = len(header)
        body: list[str] = []
        body.append("<tr>" + "".join(f"<th>{self.inline.render(cell)}</th>" for cell in header) + "</tr>")
        for row in rows:
            if len(row) < width:
                row = row + [""] * (width - len(row))
            elif len(row) > width:
                row = row[:width]
            body.append(
                "<tr>" + "".join(f"<td>{self.inline.render(cell)}</td>" for cell in row) + "</tr>"
            )
        return "<table><tbody>" + "".join(body) + "</tbody></table>", index

    @staticmethod
    def _split_row(line: str) -> list[str]:
        return split_table_row(line)

    def _consume_blockquote(self, lines: list[str], index: int) -> tuple[str, int]:
        inner: list[str] = []
        while index < len(lines) and lines[index].lstrip().startswith(">"):
            line = lines[index].lstrip()[1:]
            if line.startswith(" "):
                line = line[1:]
            inner.append(line)
            index += 1
        return f"<blockquote>{self.render(inner, nested=True)}</blockquote>", index

    def _consume_paragraph(self, lines: list[str], index: int) -> tuple[str, int]:
        buffer: list[str] = []
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                break
            if buffer and self._starts_block(lines, index):
                break
            buffer.append(line.rstrip())
            index += 1

        text = ""
        for part in buffer:
            hard_break = part.endswith("  ")
            text += part.strip()
            text += "\x01" if hard_break else " "
        return f"<p>{self.inline.render(text.strip())}</p>", index

    def _starts_block(self, lines: list[str], index: int) -> bool:
        line = lines[index]
        if (
            HEADING_RE.match(line)
            or FENCE_RE.match(line)
            or DIRECTIVE_RE.match(line)
            or LIST_RE.match(line)
            or re.match(r"^\s*(---+|\*\*\*+|___+)\s*$", line)
            or line.lstrip().startswith(">")
            or line.lstrip().startswith("<!--")
        ):
            return True
        return self._is_table_start(lines, index)

    def _consume_list(self, lines: list[str], index: int) -> tuple[str, int]:
        html_block, index = self._render_list(lines, index)
        return html_block, index

    def _render_list(self, lines: list[str], index: int) -> tuple[str, int]:
        first = LIST_RE.match(lines[index])
        assert first is not None
        base_indent = len(first.group(1).replace("\t", "    "))
        items: list[dict[str, Any]] = []

        while index < len(lines):
            if not lines[index].strip():
                lookahead = index + 1
                while lookahead < len(lines) and not lines[lookahead].strip():
                    lookahead += 1
                if lookahead >= len(lines):
                    break
                next_match = LIST_RE.match(lines[lookahead])
                if not next_match:
                    break
                if len(next_match.group(1).replace("\t", "    ")) < base_indent:
                    break
                index = lookahead
                continue

            match = LIST_RE.match(lines[index])
            if not match:
                break
            indent = len(match.group(1).replace("\t", "    "))
            if indent < base_indent:
                break
            if indent > base_indent:
                child, index = self._render_list(lines, index)
                if items:
                    items[-1]["children"].append(child)
                else:
                    break
                continue

            marker = match.group(2)
            text = match.group(3).strip()
            ordered = marker[0].isdigit()
            index += 1

            continuation: list[str] = []
            while index < len(lines):
                if not lines[index].strip():
                    break
                if LIST_RE.match(lines[index]):
                    break
                if len(lines[index]) - len(lines[index].lstrip()) <= base_indent:
                    break
                continuation.append(lines[index].strip())
                index += 1
            if continuation:
                text += " " + " ".join(continuation)

            items.append(
                {
                    "text": text,
                    "ordered": ordered,
                    "children": [],
                }
            )

        return self._render_list_items(items), index

    def _render_list_items(self, items: list[dict[str, Any]]) -> str:
        output: list[str] = []
        position = 0
        while position < len(items):
            group = [items[position]]
            position += 1
            while position < len(items) and items[position]["ordered"] == group[0]["ordered"]:
                group.append(items[position])
                position += 1

            task_mode = bool(TASK_RE.match(group[0]["text"]))
            if task_mode:
                output.append("<ac:task-list>")
                for item in group:
                    task = TASK_RE.match(item["text"])
                    if task:
                        checked, body = task.group(1), task.group(2)
                    else:
                        checked, body = " ", item["text"]
                    self.task_id += 1
                    status = "complete" if checked.lower() == "x" else "incomplete"
                    output.append(
                        f"<ac:task><ac:task-id>{self.task_id}</ac:task-id>"
                        f"<ac:task-status>{status}</ac:task-status>"
                        f"<ac:task-body>{self.inline.render(body)}"
                        f"{''.join(item['children'])}</ac:task-body></ac:task>"
                    )
                output.append("</ac:task-list>")
            else:
                tag = "ol" if group[0]["ordered"] else "ul"
                output.append(f"<{tag}>")
                for item in group:
                    output.append(
                        f"<li>{self.inline.render(item['text'])}"
                        f"{''.join(item['children'])}</li>"
                    )
                output.append(f"</{tag}>")
        return "".join(output)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def normalize_entities(value: str) -> str:
    """Turn named HTML entities into numeric references so XML parsers accept them."""

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in ("amp", "lt", "gt", "quot", "apos"):
            return match.group(0)
        codepoint = html.entities.name2codepoint.get(name)
        return f"&#{codepoint};" if codepoint else match.group(0)

    return re.sub(r"&([A-Za-z][A-Za-z0-9]+);", replace, value)


def is_well_formed(storage: str) -> tuple[bool, str]:
    fragment = storage.strip()
    if fragment.startswith("<?xml"):
        fragment = re.sub(r"^<\?xml[^>]*\?>", "", fragment).strip()
    wrapped = (
        f'<root xmlns:ac="{AC_NS}" xmlns:ri="{RI_NS}">'
        f"{normalize_entities(fragment)}</root>"
    )
    try:
        ET.fromstring(wrapped)
    except ET.ParseError as exc:
        return False, str(exc)
    return True, ""


def convert(
    text: str,
    *,
    fragment: bool = False,
    lenient: bool = False,
    mermaid_macro: str = "mermaid",
    auto_meta: bool = True,
) -> dict[str, Any]:
    """Convert Markdown to storage XHTML and return storage + manifest data."""
    if fragment:
        frontmatter: dict[str, Any] = {}
        lines = text.splitlines()
    else:
        frontmatter, lines, _ = parse_frontmatter(text)

    converter = Converter(
        frontmatter,
        lenient=lenient,
        mermaid_macro=mermaid_macro,
        auto_meta=auto_meta,
        fragment=fragment,
    )
    storage = converter.render(lines)
    well_formed, error = is_well_formed(storage)
    if not well_formed:
        raise ConversionError(f"generated storage XHTML is not well-formed: {error}")

    return {
        "storage": storage,
        "frontmatter": frontmatter,
        "title": str(frontmatter.get("title", "")).strip(),
        "space": str(frontmatter.get("space", "")).strip(),
        "labels": frontmatter_list(frontmatter, "labels"),
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert enterprise Markdown to Confluence Cloud storage XHTML."
    )
    parser.add_argument("input", type=Path, help="Markdown file to convert")
    parser.add_argument("-o", "--output", type=Path, help="write storage XHTML to this file")
    parser.add_argument(
        "--fragment",
        action="store_true",
        help="treat input as a section fragment (no frontmatter, no auto metadata table)",
    )
    parser.add_argument("--lenient", action="store_true", help="keep unknown macros as literal text")
    parser.add_argument(
        "--mermaid-macro",
        default="mermaid",
        help="macro name installed by the Mermaid app (default: mermaid)",
    )
    parser.add_argument("--no-auto-meta", action="store_true", help="do not prepend the document control table")
    parser.add_argument("--manifest", type=Path, help="write title/space/labels/version as JSON")
    parser.add_argument("--check", action="store_true", help="validate XHTML and print a summary only")
    args = parser.parse_args(argv)

    try:
        text = args.input.read_text(encoding="utf-8")
        result = convert(
            text,
            fragment=args.fragment,
            lenient=args.lenient,
            mermaid_macro=args.mermaid_macro,
            auto_meta=not args.no_auto_meta,
        )
    except FileNotFoundError:
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 2
    except ConversionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    storage = result["storage"]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(storage + "\n", encoding="utf-8")
    if args.manifest:
        manifest = {key: value for key, value in result.items() if key != "storage"}
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.check:
        print(
            f"ok: {args.input} -> {len(storage):,} chars XHTML, "
            f"{storage.count('<ac:structured-macro'):,} macros"
        )
    elif not args.output and not args.manifest:
        print(storage)
    return 0


if __name__ == "__main__":
    sys.exit(main())
