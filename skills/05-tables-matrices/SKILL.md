---
name: tables-matrices
description: Table design for specifications — requirement indexes, decision logs, risk registers, RACI, error codes and traceability matrices with column budgets and accessibility-safe structure.
tags: [confluence, tables, matrices, requirements, decision-log, traceability]
related: [fds-requirements, visual-hierarchy, readability-accessibility]
---

# Confluence Documents Guide: Tables and Matrices

## 1. Definition

A table is a comparison instrument: one entity per row, one attribute per column, and a header that tells the reader what can be compared. Matrices extend the idea to relationships — requirement to test, risk to owner, decision to date. The moment a table stops comparing and starts laying out the page, it becomes a liability for reflow, zoom and screen readers.

## 2. Core Principles

- **One entity per row:** a requirement, a risk, a decision or an endpoint — never two kinds in one table.
- **ID first:** the first column is a stable identifier so reviews can cite `BR-004` or `AC-002`.
- **Decision-useful columns:** every column answers a question a reviewer will ask; delete decorative columns.
- **Units in the header:** `Latency (ms)`, not a number with a footnote.
- **No merged cells:** merging breaks sorting, copy-paste and screen-reader navigation.
- **Explicit empty state:** use an em dash, never a blank cell that looks unfinished.
- **Short cells:** a table cell is a label or a value, not a paragraph; move prose above the table.
- **Eight columns is the budget:** ten is the hard ceiling; split rather than scroll.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Minimum rows | `--table-min-rows` | `3` | Below three, use prose or a short list |
| Column budget | `--table-columns` | `≤ 8` | Hard ceiling of 10 |
| Header row | `--table-header` | `mandatory` | `<th>` in storage |
| Identifier column | `--table-id-column` | `first` | Stable IDs, never reused |
| Cell budget | `--table-cell-words` | `40` | Longer text becomes prose |
| Empty cell | `--table-empty` | `—` | Explicit, not blank |
| Units | `--table-units` | `in header` | `Amount (VND)`, `Latency (ms)` |
| Status column | `--table-status-column` | `last or second-last` | Text plus colour |
| Merge policy | `--table-merge` | `forbidden` | Use repeated values instead |

## 4. Composition

- **With fds-requirements (guide 02):** the requirement index, AC matrix and open-question register are the canonical tables.
- **With visual-hierarchy (guide 03):** tables are the default container for three or more parallel facts.
- **With jira-traceability (guide 07):** the Jira column is the join key between Confluence and delivery.
- **With readability-accessibility (guide 11):** headers, cell length and no-merge rules are accessibility contracts.

## 5. Signature Patterns

- **Requirement index:** ID, requirement, priority, Jira, status.
- **Decision log:** ID, date, decision, rationale, owner, status.
- **Risk register:** ID, risk, likelihood, impact, mitigation, owner, status.
- **Open questions:** ID, question, owner, needed by, status.
- **RACI:** role, name, responsibility, R/A/C/I.
- **Error catalogue:** code, HTTP, meaning, retry, user message.
- **Traceability matrix:** FR, AC, Jira, test evidence, release.
- **Do/Don't:** behaviour, do, don't, reason.

## 6. Real-World Use Cases

- **Release readiness review** — the FR → AC → evidence matrix is the agenda; empty evidence cells block the release.
- **Architecture decision record** — options, consequences and revisit triggers in one comparison table.
- **Incident postmortem** — timeline and action items are tables; the narrative stays in paragraphs.
- **Compliance evidence** — control, owner, evidence link, last verified date.

## 7. Combination Notes

### With other confluence-document skills

- **FDS requirements:** a requirement table without a unique ID column is not reviewable.
- **Visual hierarchy:** tables replace bullet walls, but a page of only tables also lacks narrative; pair each table with a lede.
- **Jira traceability:** the Jira column must hold a real issue key, not a pasted status.
- **Readability:** header rows and short cells keep large tables usable at zoom and with a screen reader.

### With design-system companions

- **skill-component-recipes (data grids):** the same rules apply to UI tables — header, alignment, empty state, no merged cells.
- **skill-color-theory:** status colour is redundant with text; never encode meaning in cell fill alone.

## 8. Anti-Patterns

- **Bullet list pretending to be a comparison table** — the reader cannot align attributes across items
- **Twelve-column table that requires horizontal scrolling** — the last columns are never read
- **Merged cells that break sorting and screen readers** — repeated values are cheaper than merges
- **Empty cells instead of an explicit em dash** — blanks look like missing work, not "not applicable"
- **Status conveyed only by cell colour** — invisible in greyscale and to colour-blind readers

### Accessibility Notes

Every table needs a header row; screen readers announce column names from `<th>`. Avoid merged cells and nested tables. Keep cell text short so zoom does not force horizontal scrolling. If a table exceeds ten columns, split it into a summary table and a detail table with a shared ID column.

## 9. Code Examples

### Example 1 — Requirement, decision and risk tables

```markdown
| ID | Requirement | Priority | Jira | Status |
|---|---|---|---|---|
| FR-001 | Create a partial or full refund | Must | {{jira:PAY-1420}} | {{status:green\|Approved}} |
| FR-002 | Replay the result for a repeated key | Must | {{jira:PAY-1421}} | {{status:green\|Approved}} |

| ID | Date | Decision | Rationale | Owner | Status |
|---|---|---|---|---|---|
| DEC-001 | 2026-11-10 | Require dual approval at 50,000,000 VND | Fraud loss exceeded threshold twice in Q3 | Risk Ops | {{status:green\|Approved}} |

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| RSK-001 | Duplicate refund from retry | Medium | High | Idempotency key plus unique constraint | Payments | {{status:green\|Mitigated}} |
```

### Example 2 — Traceability matrix and validation

```markdown
| FR | AC | Jira | Test evidence | Release |
|---|---|---|---|---|
| FR-001 | AC-001, AC-002, AC-003 | {{jira:PAY-1420}} | [Regression run 1842]({URL}) | R2026.12 |
| FR-002 | AC-004 | {{jira:PAY-1421}} | [Contract test 77]({URL}) | R2026.12 |
```

```bash
# Column mismatches, empty cells and over-wide tables are lint findings.
python3 scripts/validate_document.py fds.md --profile fds --min-score 90
```

## 10. Implementation Checklist

- [ ] Every table compares one kind of entity and has a header row.
- [ ] The first column is a stable ID when rows are referenced elsewhere.
- [ ] Columns stay at or below eight; cells stay at or below 40 words.
- [ ] Units are in the header, not in every cell.
- [ ] No merged cells and no blank cells; use an explicit em dash.
- [ ] Status cells include a text label in addition to colour.
- [ ] Each table is introduced by a sentence explaining what it proves.
- [ ] The table is readable at 200% zoom without horizontal scrolling.
