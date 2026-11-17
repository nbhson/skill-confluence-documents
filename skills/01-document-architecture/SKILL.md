---
name: document-architecture
description: Page anatomy for enterprise Confluence documents — title formula, document control block, TOC, numbered sections, appendices and the 30-second comprehension test.
tags: [confluence, document-architecture, page-anatomy, toc, structure]
related: [visual-hierarchy, fds-requirements, review-governance]
---

# Confluence Documents Guide: Document Architecture

## 1. Definition

Document architecture is the fixed skeleton every page inherits: a predictable title, a document control block, a table of contents, numbered sections in a stable order, and appendices for depth. Readers should know where they are, what the document is worth, and how current it is within thirty seconds. Architecture is not decoration; it is how a reviewer finds the one section they must approve without reading everything else.

## 2. Core Principles

- **Title states type and scope:** `{Feature} — Functional Design Specification`, not `FDS new final v2`.
- **Control before content:** document ID, version, status, owner, reviewers, Jira key and last-updated date appear before the first section.
- **One page, one purpose:** a page is an FDS or an API spec or a runbook — never a mixed notebook.
- **Numbered, shallow sections:** six to twelve H2 sections, numbered `1..n`, depth three at most.
- **Answer first:** each section opens with one or two sentences stating the conclusion, then the evidence.
- **Depth belongs in appendices:** glossary, references and long tables move to `Appendix A/B`, linked from the body.
- **Stable anchors:** sections referenced from Jira or code carry an explicit anchor such as `{#fr-001}`.
- **Version history is the archive:** never create `page-v2`; update the page and record the change.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Page title | `--doc-title-format` | `{Feature} — {Document type}` | Sentence case after the dash |
| Control fields | `--doc-control-fields` | `doc_id, version, status, owner, reviewers, jira, updated` | Frontmatter renders the table |
| TOC threshold | `--doc-toc-min-sections` | `6` | Add `{{toc}}` at or above this count |
| Section count | `--doc-section-count` | `6–12` | Split or group outside this range |
| Section depth | `--doc-max-depth` | `3` | H4 only for detail under a requirement |
| Section numbering | `--doc-numbering` | `1..n` | Appendices use letters |
| Status vocabulary | `--doc-status-vocab` | `Draft, In Review, Approved, Deprecated, Superseded` | Controlled values only |
| Change log position | `--doc-changelog-position` | `last` | Before appendices |
| Page budget | `--doc-storage-budget` | `1 MB` | Move exports to attachments |

## 4. Composition

- **With visual-hierarchy (guide 03):** architecture decides the order; visual hierarchy decides the container — paragraph, table, panel or expand.
- **With fds-requirements (guide 02):** the FDS section order is a specialization of this skeleton; requirement IDs and acceptance criteria plug into sections 4 and 10.
- **With review-governance (guide 10):** the control block and change log are the audit surface reviewers sign.
- **With update-versioning (guide 08):** the change log is written by the update protocol, not by hand at the end.

## 5. Signature Patterns

- **Canonical skeleton:** control table → TOC → scope → requirements → constraints → data/API → flows → acceptance → risks → change log → appendices.
- **30-second test:** a reader can answer *what is this, who owns it, is it approved, what changed last* from the first screen.
- **Answer-first section:** a lede sentence, then one table or panel, then exceptions in an expand.
- **Appendix split:** when a section passes 150 lines, move reference material to an appendix and link the anchor.

## 6. Real-World Use Cases

- **New FDS for a regulated payment flow** — the control block and numbered sections let Risk and Compliance cite exact clauses.
- **Legacy page retrofit** — add frontmatter, TOC and numbering first, then move long appendices without rewriting the content.
- **Microservice documentation set** — one page per service using the same skeleton, with child pages for deep API schemas.

## 7. Combination Notes

### With other confluence-document skills

- **Visual hierarchy:** architecture is the map, hierarchy is the signage; neither works alone.
- **FDS requirements:** the FDS template is the most demanding instance of the skeleton; keep the two aligned.
- **Review governance:** the control table is only useful when status transitions are enforced.
- **Update and versioning:** every revision touches the change log and the `updated` field; the protocol owns both.

### With design-system companions

- **skill-ui-ux:** the same information hierarchy that makes a UI scannable applies to a page; use one primary message per section.
- **skill-typography:** heading levels carry hierarchy; do not compensate with font size or bold.

## 8. Anti-Patterns

- **No document control block** — version, owner and status live only in Slack
- **One page per revision** — `FDS v2 final` pages fork the truth
- **Twenty H2 sections with no grouping** — readers cannot hold the structure in mind
- **TOC used as the only navigation** — sections lack headings or anchors
- **Appendix content mixed into the main narrative** — reference tables interrupt the decision path

### Accessibility Notes

Heading levels are the screen-reader outline. One H1 (the page title), H2 for sections, H3 for sub-sections, no skipped levels. Anchor names must be meaningful (`refund-approval`, not `section-7`). A TOC is a navigation aid, not a substitute for descriptive headings.

## 9. Code Examples

### Example 1 — Canonical skeleton in Markdown

```markdown
---
title: "Payment refund — Functional Design Specification"
doc_id: FDS-PAY-014
version: 1.0
status: Approved
owner: "Nguyễn Minh An"
reviewers: ["Trần Minh Quân", "Lê Thu Hà"]
jira: PAY-1420
space: PAY
labels: [fds, payments, refund]
updated: 2026-11-17
---

{{meta}}

{{toc}}

## 1. Purpose and Scope
## 2. Stakeholders
## 3. Assumptions and Constraints
## 4. Functional Requirements
## 5. Non-Functional Requirements
## 6. Business Rules
## 7. Data Model
## 8. Integrations and API Contracts
## 9. User Flows and UX Notes
## 10. Acceptance Criteria
## 11. Risks and open questions
## 12. Change Log
## Appendix A. Glossary
```

### Example 2 — Promote a legacy page without rewriting it

```bash
# 1. Measure the current structure before touching content.
python3 scripts/validate_document.py legacy.md --profile generic --min-score 0

# 2. Add frontmatter + TOC + numbering in one editorial pass.
# 3. Convert and compare; never overwrite the live page from memory.
python3 scripts/md2storage.py legacy.md -o legacy.storage.html --check
python3 scripts/confluence.py diff --page-id 12345 --from-md legacy.md
```

## 10. Implementation Checklist

- [ ] Page title follows `{Feature} — {Document type}` and does not contain a version number.
- [ ] Document control block has doc_id, version, status, owner, reviewers, Jira key and updated date.
- [ ] TOC exists when the page has six or more H2 sections.
- [ ] H2 sections are numbered, six to twelve in count, and no deeper than H3 for structure.
- [ ] Every section opens with an answer-first sentence before any list or table.
- [ ] Long reference material lives in an appendix and is linked from the body.
- [ ] Status uses the controlled vocabulary; the change log matches the frontmatter version.
- [ ] The 30-second test passes with a colleague who has never seen the page.
