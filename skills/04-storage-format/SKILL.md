---
name: storage-format
description: Confluence Cloud storage XHTML — the safe tag subset, macro anatomy, escaping, CDATA, images, anchors and the raw-storage escape hatch.
tags: [confluence, storage-format, xhtml, macros, api]
related: [visual-hierarchy, tables-matrices, automation-quality]
---

# Confluence Documents Guide: Storage Format

## 1. Definition

Confluence stores page bodies as *storage format*: an XHTML fragment with `ac:` macros and `ri:` resource identifiers. The REST API accepts and returns this representation, and the editor round-trips it. A document is safe to publish when every tag is well formed, every macro is allowlisted, every attribute is escaped, and the fragment survives a parse. Anything else becomes broken layout, literal text or a page the editor silently rewrites.

## 2. Core Principles

- **Emit a conservative subset:** headings, paragraphs, lists, tables, links, images and the macros in section 3 — nothing else.
- **Well-formed before publish:** every element closes; every `&` is `&amp;`; every attribute quote is balanced.
- **No executable content:** no `<script>`, `<style>`, `<iframe>`, event handlers or `javascript:` links.
- **CDATA for code:** macro bodies that contain `<`, `>` or `&` use `ac:plain-text-body` with CDATA, splitting `]]>` safely.
- **Rich text for prose:** panels and expands wrap prose in `ac:rich-text-body`.
- **Images are attachments:** reference `ri:attachment` by filename; never inline base64.
- **One source of truth:** generate storage from Markdown; hand-editing live storage is a review exception, not the workflow.
- **Fail closed:** unknown macros abort conversion unless `--lenient` is explicit.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Allowed block tags | `--storage-block-tags` | `h1–h6, p, ul, ol, li, table, thead, tbody, tr, th, td, blockquote, hr, pre` | No div/span styling |
| Allowed inline tags | `--storage-inline-tags` | `strong, em, del, code, a, br` | No font/size tags |
| Macro allowlist | `--storage-macros` | `info, note, tip, warning, panel, expand, status, jira, toc, anchor, code, children, include` | Confirm tenant-specific apps |
| Page budget | `--storage-page-budget` | `1 MB` | Hard warning above 2 MB |
| Macro count | `--storage-macro-budget` | `500` | Split the page above this |
| Table rows | `--storage-table-rows` | `500` | Move exports to attachments |
| Escaping | `--storage-escape` | `& < > "` | Attributes use `&quot;` |
| Raw escape hatch | `--storage-raw-fence` | ` ```storage ` | Reviewed like code |
| Namespaces | `--storage-namespaces` | `ac, ri` | Declared by Confluence |

## 4. Composition

- **With visual-hierarchy (guide 03):** every container in that guide maps to one macro here; choose containers before writing storage.
- **With tables-matrices (guide 05):** tables are plain XHTML with `<th>` headers, not macros.
- **With diagrams (guide 06):** diagram macros are app-specific; confirm the macro name before relying on it.
- **With automation-quality (guide 12):** conversion and well-formedness checks belong in CI, not in a reviewer's browser.

## 5. Signature Patterns

- **Macro anatomy:** `ac:structured-macro` + named parameters + one body type (`ac:rich-text-body` or `ac:plain-text-body`).
- **Status lozenge:** colour parameter plus title parameter; text is the meaning.
- **Panel:** optional title, rich-text body, no custom colours (theme handles dark mode).
- **Expand:** optional title, rich-text body; detail only, never mandatory criteria.
- **Code block:** language parameter plus `ac:plain-text-body` in CDATA.
- **Anchor:** unnamed parameter carrying the anchor slug, placed inside the heading.
- **Attachment image:** `ac:image` with `ac:alt` and `ri:attachment ri:filename`.

## 6. Real-World Use Cases

- **API-generated release notes** — deterministic storage from a template, validated before every publish.
- **Migration from another wiki** — convert to the allowlisted subset instead of pasting exported HTML.
- **Agent-authored updates** — fetch storage, replace one section, validate and push with a version message.
- **Audit of legacy pages** — scan for scripts, iframes, base64 images and unknown macros before a space migration.

## 7. Combination Notes

### With other confluence-document skills

- **Visual hierarchy:** storage is the implementation of the formatting system; do not add tags the guide does not request.
- **Tables and matrices:** table structure must include `<th>`; merged cells are avoided for accessibility.
- **Diagrams:** the diagram macro is often an app; treat its name as configuration, not a hard-coded assumption.
- **Automation and quality:** `md2storage.py --check` is the gate; `confluence.py` refuses malformed storage.

### With design-system companions

- **skill-design-tokens:** the same principle applies — use semantic containers, not ad-hoc inline styling.
- **skill-accessibility:** storage must preserve heading order, table headers and alt text; the editor cannot repair missing semantics.

## 8. Anti-Patterns

- **Unclosed or misspelled ac:structured-macro tags** — the page renders literal XML or loses the body
- **Raw HTML copied from Word or Google Docs** — font, span and style noise the editor strips unpredictably
- **Script, style or iframe tags pasted into storage** — a security and rendering hazard
- **Base64 images embedded in the page body** — bloats the page and breaks caching
- **Unknown macros published as literal text** — readers see `{{status:...}}` instead of a status

### Accessibility Notes

Storage must carry semantics, not styling: real `<h2>`/`<h3>` elements, `<th>` for table headers, `ac:alt` on every image, descriptive link text. A `<span style="font-weight:bold">` looks like a heading to sighted readers and is invisible to assistive technology. CDATA code blocks need a language parameter so screen readers and highlighters can treat them consistently.

## 9. Code Examples

### Example 1 — Macro cheat sheet

```xml
<!-- Info panel -->
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>Decision required by 24 Nov 2026.</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Status lozenge -->
<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Green</ac:parameter>
  <ac:parameter ac:name="title">Approved</ac:parameter>
</ac:structured-macro>

<!-- Code block -->
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">json</ac:parameter>
  <ac:plain-text-body><![CDATA[{"refund": true}]]></ac:plain-text-body>
</ac:structured-macro>

<!-- Attachment image -->
<ac:image ac:alt="Refund state machine from pending to succeeded">
  <ri:attachment ri:filename="refund-state.png" />
</ac:image>
```

### Example 2 — Convert, validate, publish

```bash
# Markdown is the source of truth; storage is generated.
python3 scripts/md2storage.py fds.md -o fds.storage.html --manifest fds.json --check

# Reject malformed XHTML before it reaches Confluence.
python3 scripts/confluence.py diff --page-id 12345 --file fds.storage.html
python3 scripts/confluence.py update --page-id 12345 --file fds.storage.html \
  --message "Clarify refund approval threshold"
```

## 10. Implementation Checklist

- [ ] Every tag is from the allowlisted subset and every element closes.
- [ ] `&`, `<` and `>` are escaped in text; attributes use quoted escaped values.
- [ ] Code and diagram bodies use CDATA; `]]>` is split safely.
- [ ] Every macro is in the allowlist; app-specific macros are confirmed in the tenant.
- [ ] Images reference attachments with descriptive `ac:alt`; no base64.
- [ ] No script, style, iframe or event-handler attributes.
- [ ] The generated fragment passes `md2storage.py --check` and `confluence.py verify`.
- [ ] Page size, macro count and table rows stay within the budgets.
