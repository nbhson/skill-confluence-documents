---
name: visual-hierarchy
description: Enterprise formatting system for Confluence — answer-first sections, tables over bullet walls, panels, status lozenges, expandable depth, scannable density and the bullet-ratio budget.
tags: [confluence, formatting, visual-hierarchy, tables, panels, scannability]
related: [document-architecture, tables-matrices, readability-accessibility]
---

# Confluence Documents Guide: Visual Hierarchy and Formatting

## 1. Definition

Visual hierarchy is the deliberate use of paragraphs, tables, panels, status lozenges and headings to tell the reader what matters first. Enterprise formatting is not "more decoration"; it is fewer, stronger containers. A page with twelve bullet lists has no hierarchy — everything is equally unimportant. A page with one answer-first paragraph, one comparison table and one decision panel can be approved in two minutes.

## 2. Core Principles

- **Answer first, evidence second:** open each section with one or two sentences stating the conclusion.
- **Table when parallel, prose when causal:** three or more comparable facts become a table; a chain of reasoning stays a paragraph.
- **Bullets are the exception:** use them for short sequences, never as the default container for requirements, risks or options.
- **One callout per decision:** a panel marks a decision, warning or constraint; if every paragraph is in a panel, none stands out.
- **Format follows content, and choosing it is a decision:** walk the container ladder — table for parallel facts, callout for exceptions, expand for long evidence, columns for side-by-side, task list for owned work, embed for media — and stop at the first container that fits.
- **Status is text plus colour:** `{{status:green|Approved}}`, never a green cell without a label.
- **Depth is collapsible:** long evidence moves into `:::expand`, keeping the main path short.
- **Whitespace is structure:** one idea per section; split before the page becomes a scroll marathon.
- **Format follows content:** do not use a table as page layout or a heading as font size.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Bullet budget | `--doc-bullet-ratio` | `≤ 35%` | Share of prose lines that are bullets |
| Bullet run | `--doc-bullet-run` | `≤ 8` | Consecutive bullet lines before a break |
| Bullet depth | `--doc-bullet-depth` | `2` | Third level requires a table instead |
| Table threshold | `--doc-table-threshold` | `3` | Parallel items at or above this become a table |
| Paragraph budget | `--doc-paragraph-words` | `180` | Longer paragraphs split or move to an expand |
| Section lede | `--doc-section-lede` | `1–2 sentences` | Before any list or table |
| Callout budget | `--doc-callout-budget` | `1 per section` | More than one competes for attention |
| Callout page budget | `--doc-callout-page-budget` | `≤ 5` | The linter warns above this count |
| Container ladder | `--doc-container-ladder` | `table → callout → expand → columns → task → embed → raw storage` | Pick the first container that fits |
| Expand title | `--doc-expand-title` | `required` | Untitled expands fail the lint budget |
| Status colours | `--doc-status-colours` | `Grey, Yellow, Green, Red, Purple` | Text label is mandatory |
| Code language | `--doc-code-language` | `required` | Enables syntax highlighting |
| Table columns | `--doc-table-columns` | `≤ 8` | Ten is the hard ceiling |

## 4. Composition

- **With document-architecture (guide 01):** architecture defines section order; hierarchy chooses the container inside each section.
- **With tables-matrices (guide 05):** the table is the workhorse container; this guide sets the budget, that guide sets the columns.
- **With readability-accessibility (guide 11):** visual contrast must survive greyscale, zoom and screen readers.
- **With storage-format (guide 04):** every container maps to a supported macro; do not invent styling the editor will strip.

## 5. Signature Patterns

- **Answer-first section:** lede paragraph → one table → exception panel → optional expand.
- **Decision panel:** `:::info` with the decision, owner and deadline; the body links to the evidence.
- **Risk table:** ID, risk, likelihood, impact, mitigation, owner, status — never a bulleted risk list.
- **Do/Don't table:** two columns, one behaviour per row; the fastest way to remove ambiguity.
- **Progressive disclosure:** summary table in the body, full schema or test evidence in `:::expand`.
- **Before/after table:** legacy behaviour versus new behaviour, with a verification column.
- **Titled callout:** `:::warning Refund window` — colour plus a name the reader can cite; untitled callouts are decoration.
- **Two-column decision frame:** `:::columns` with a `||` separator places the decision beside its counter-evidence, not two screens apart.
- **Owned checklist:** action items with owners and dates become task lists (`- [ ]`), so completion state survives export and review.

## 6. Real-World Use Cases

- **FDS review** — reviewers scan the requirement table, open one detail section, and sign the change log.
- **Incident postmortem** — the timeline table carries the evidence; the summary panel carries the conclusion.
- **API change notice** — breaking changes in a table with impact and required action, not a wall of bullets.
- **Runbook** — numbered procedure plus decision table; bullets only for short checklists.

## 7. Combination Notes

### With other confluence-document skills

- **Tables and matrices:** this guide says *when* to use a table; the table guide says *how* to design one.
- **Readability and accessibility:** strong hierarchy helps sighted skimmers and screen-reader users; both depend on real headings and labelled status.
- **Storage format:** panels, status and expand are macros; use the allowlisted forms to avoid editor drift.
- **Update and versioning:** formatting changes are still changes; a restructure gets its own version message.

### With design-system companions

- **skill-ui-ux (minimalism, flat design):** the same restraint applies — one primary message, generous whitespace, no decorative noise.
- **skill-typography:** hierarchy comes from heading level and spacing, not from bold or all caps.

## 8. Anti-Patterns

- **Bullet wall where every section is a flat list** — no hierarchy, no prioritisation, no narrative
- **Bold, caps and colour used together for emphasis** — three signals for one meaning, none trusted
- **Rainbow status colours with no legend or text** — meaning lost in greyscale and for colour-blind readers
- **Four levels of nested bullets** — the reader cannot reconstruct the hierarchy
- **Tables used as page layout rather than data** — breaks reflow, zoom and screen readers
- **Callout spam** — a page of coloured boxes where every paragraph is highlighted and no exception stands out
- **Untitled expand as a hiding place** — content nobody can find by scanning, cite from Jira or approve
- **Screenshots of text instead of selectable content** — unsearchable, untranslatable, inaccessible

### Accessibility Notes

Never rely on colour alone: the status macro includes a text label. Body text must meet 4.5:1 contrast; headings are real heading elements, not bold paragraphs. Tables need a header row so screen readers announce column names. Expand macros hide content from search results in some configurations — never put mandatory acceptance criteria only inside an expand.

## 9. Code Examples

### Example 1 — Before and after a bullet-wall section

```markdown
<!-- Before: flat list, no priority, no ownership -->
- Refunds need approval
- Refunds can be partial
- Refunds have a 180-day limit
- We need an audit log

<!-- After: lede, table, decision panel -->
Refunds are available for captured payments within 180 days. Amounts at or above 50,000,000 VND require two approvers.

| Rule | Threshold | Enforcement | Error code |
|---|---|---|---|
| Refund window | 180 days from capture | Refund service | `REFUND_WINDOW_EXPIRED` |
| Dual approval | ≥ 50,000,000 VND | Workflow engine | `APPROVAL_REQUIRED` |
| Partial refund | ≤ remaining amount | Ledger constraint | `REFUND_AMOUNT_EXCEEDED` |

:::info
**Decision owner:** Risk Operations. **Required by:** 24 Nov 2026. **Tracking:** {{jira:PAY-1455}}.
:::
```

### Example 2 — Generated storage containers

```bash
python3 scripts/md2storage.py section.md -o section.storage.html --check
```

```xml
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p><strong>Decision required by 24 Nov 2026.</strong> Refunds above 50,000,000 VND need two approvers.</p>
  </ac:rich-text-body>
</ac:structured-macro>
<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Green</ac:parameter>
  <ac:parameter ac:name="title">Approved</ac:parameter>
</ac:structured-macro>
```

```bash
# The linter fails a section that is bullets only.
python3 scripts/validate_document.py fds.md --profile fds --min-score 90
```

## 10. Implementation Checklist

- [ ] Every section starts with a one- or two-sentence answer before any list or table.
- [ ] Bullet lines stay at or below 35% of prose lines; no section is bullets only.
- [ ] No more than eight consecutive bullets and no more than two nesting levels.
- [ ] Three or more parallel facts are in a table with a header row.
- [ ] At most one decision panel per section, with owner and deadline.
- [ ] Status always includes a text label, not only a colour.
- [ ] Long evidence is in an expand; mandatory criteria stay in the body.
- [ ] Callouts stay at five or fewer per page and every expand and callout has a title.
- [ ] The page is readable at 200% zoom and in greyscale.
