---
name: readability-accessibility
description: Readable and accessible Confluence writing — plain language, sentence and paragraph budgets, descriptive headings and links, alt text, status semantics, zoom and screen-reader behaviour, and Vietnamese typography.
tags: [confluence, readability, accessibility, plain-language, vietnamese, wcag]
related: [visual-hierarchy, tables-matrices, document-architecture, review-governance]
---

# Confluence Documents Guide: Readability and Accessibility

## 1. Definition

Readability is the effort a reader spends to extract meaning; accessibility is whether that effort is possible at all for someone using a screen reader, keyboard, zoom or reduced colour perception. In Confluence, most accessibility failures are authoring failures, not platform failures: bold paragraphs pretending to be headings, tables without headers, status conveyed only by colour, links that say "here", images without alt text, Vietnamese stripped of diacritics. Readable documents are not simpler documents — they are documents where the structure does the work instead of the reader.

## 2. Core Principles

- **Answer first:** every section opens with one or two sentences stating the conclusion before evidence or procedure.
- **One idea per paragraph:** three to five sentences, and split before the paragraph becomes a wall.
- **Short sentences:** aim for 25 words or fewer; one clause of qualification is enough.
- **Active voice, named actor:** "Risk Operations approves refunds above 50M VND", not "approval is required".
- **Headings are questions or answers:** `6.2 Dual approval` beats `6.2 Miscellaneous`.
- **Links name their destination:** `FDS-PAY-014 change log`, not `click here` or `tại đây`.
- **Alt text states the conclusion:** describe what the reader should learn, not the file or the pixels.
- **Colour is redundant:** status always carries a text label; method, severity and outcome are written as words.
- **Real structure only:** `<h2>`/`<h3>` for hierarchy, `<th>` for table headers, never bold or font size.
- **Vietnamese keeps its diacritics:** write `Yêu cầu chức năng`, never `Yeu cau chuc nang`; screen readers and search both depend on the marks.
- **Terms are stable:** one concept, one term; define acronyms on first use and keep a glossary.
- **Reflow at 200%:** no horizontal scrolling for prose, and tables stay within the column budget.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Sentence length | `--read-sentence-words` | `≤ 25` | Split at the second clause |
| Paragraph length | `--read-paragraph-sentences` | `3–5` | More becomes a new section |
| Section lede | `--read-lede` | `1–2 sentences` | Before any table or list |
| Heading depth | `--read-heading-depth` | `3` | No skipped levels |
| Link text | `--read-link-text` | `destination + purpose` | Never "here" |
| Alt text | `--read-alt-text` | `8–20 words` | Conclusion, not filename |
| Contrast | `--read-contrast` | `4.5:1` body, `3:1` large | WCAG AA |
| Zoom | `--read-zoom` | `200%` | No loss of content or function |
| Language | `--read-language` | `vi-VN` or `en-US` | Per page and per quotation |
| Acronyms | `--read-acronyms` | `expanded on first use` | Glossary in the appendix |
| Status | `--read-status` | `text + colour` | Icon alone is not a label |
| Table columns | `--read-table-columns` | `≤ 8` | Ten is the hard ceiling |

## 4. Composition

- **With visual-hierarchy (guide 03):** hierarchy is a readability device; panels and tables only help if headings and labels are real.
- **With tables-matrices (guide 05):** header rows, short cells and no merged cells are accessibility requirements, not preferences.
- **With diagrams (guide 06):** alt text and a long description are part of the document, not metadata added at publish time.
- **With review-governance (guide 10):** accessibility evidence belongs in the review checklist for every UI-facing document.
- **With typography (design-system companion):** line length, spacing and heading rhythm apply to pages as much as to interfaces.
- **With automation-quality (guide 12):** lint can detect missing alt text and ASCII-only Vietnamese; it cannot judge whether the wording is clear.

## 5. Signature Patterns

- **Answer-first section:** lede sentence, one table of evidence, one exception panel, optional expand for depth.
- **In-short panel:** three sentences at the top of a long page: what it is, who it is for, what decision it needs.
- **Glossary table:** term, definition, Vietnamese equivalent, first use; linked from the appendix.
- **Do/Don't table:** behaviour, do, don't, reason — the fastest way to remove ambiguity without a paragraph.
- **Text-plus-colour status:** `{{status:green|Approved}}` in a table with a `Status` header; the word carries the meaning.
- **Descriptive link:** `[PAY-1420 — refund epic]({URL})`; the accessible name is useful out of context.
- **Long description for a diagram:** a short expand listing the steps or states, for readers who cannot see the image.
- **Screen-reader test script:** heading outline, table navigation, link list and form/status announcement checked before approval.
- **Vietnamese terminology table:** English term, Vietnamese term, note on declension or abbreviation.

## 6. Real-World Use Cases

- **Mixed-language FDS in Vietnam** — Vietnamese prose with English technical terms; the glossary prevents three translations of the same concept.
- **Screen-reader review of a runbook** — an on-call engineer navigates by headings and tables at 3 a.m., often on a laptop with zoom.
- **Mobile approver** — a manager reads the summary panel and status table on a phone; reflow and short cells decide whether approval happens.
- **Compliance audit** — the auditor checks that the published page is readable, link text is meaningful and alt text describes the evidence.
- **Legacy page retrofit** — replacing bold pseudo-headings and ASCII Vietnamese with real structure and correct diacritics.

## 7. Combination Notes

### With other confluence-document skills

- **Visual hierarchy:** panels and tables reduce cognitive load only when the heading outline is correct; decoration without structure makes both worse.
- **Tables:** merged cells, blank cells and colour-only status are readability failures even when the table looks tidy.
- **Diagrams:** alt text is required for every image; a complex diagram needs a text equivalent, not a longer alt string.
- **Review governance:** accessibility is review evidence; "we will fix it later" is an open finding, not an approval.
- **Automation:** lint catches mechanical issues; a human must still read the page aloud or with a screen reader.

### With design-system companions

- **skill-typography:** measure, line height, heading rhythm and numeral style apply to documents; long lines exhaust readers.
- **skill-accessibility:** use the same WCAG criteria and testing habits as for product UI; a document is an interface.
- **skill-ux-writing:** plain-language rules, verb-first labels and specific error messages transfer directly to document prose.
- **skill-color-theory:** contrast maths and colour-blind safety apply to status macros and diagram palettes.

## 8. Anti-Patterns

- **Paragraphs over 180 words with no structure** — readers skim, miss the decision and ask for a meeting
- **"Click here" or "tại đây" link text** — meaningless in a link list and for screen readers
- **Status conveyed only by colour** — invisible in greyscale, print and to colour-blind readers
- **Bold paragraphs used as headings** — the visual hierarchy exists, the accessible outline does not
- **Acronyms and abbreviations never expanded** — excludes new joiners and breaks translation
- **Vietnamese stripped of diacritics** — screen readers mispronounce it and search fails to match
- **Alt text that repeats the filename** — `refund-state.png` tells the reader nothing
- **Tables used for page layout** — breaks reflow at zoom and confuses table navigation

### Accessibility Notes

Target WCAG 2.2 AA for published documents. The relevant criteria are 1.3.1 (structure and relationships), 1.4.3 (contrast), 1.4.4 (resize text), 1.4.10 (reflow), 2.4.4 (link purpose), 2.4.6 (headings and labels), 2.4.7 (focus visible) and 3.1.1 (language of page). In practice: keep one H1, never skip heading levels, use real table headers, give every image alt text, and keep status text beside the colour. Test with VoiceOver or NVDA: navigate by headings, open the link list, move through a table and confirm the status macro announces its title. Test at 200% zoom and in greyscale. For Vietnamese, verify that the page language is set so the screen reader uses the Vietnamese voice; ASCII-only text is a defect, not a simplification. Expand macros can hide content from search and from some assistive flows — never put mandatory criteria only inside an expand.

## 9. Code Examples

### Example 1 — Before and after: readable, accessible section

```markdown
<!-- Before: wall of text, colour-only status, vague link -->
Refunds are possible and need approval in some cases. See the policy here.
Status: 🟢

<!-- After: lede, table with text status, descriptive link -->
Refunds are available for captured payments within 180 days. Amounts at or above 50,000,000 VND need two approvers before the card adapter is called.

| Rule | Threshold | Enforcement | Status |
|---|---|---|---|
| Refund window | 180 days from capture | Refund service | {{status:green\|Approved}} |
| Dual approval | ≥ 50,000,000 VND | Workflow engine | {{status:green\|Approved}} |

Read the [risk policy for refund approval]({URL}) before changing the threshold.
```

### Example 2 — Vietnamese prose with stable terminology

```markdown
## 6. Quy tắc nghiệp vụ

Hệ thống chỉ cho phép hoàn tiền cho giao dịch đã được ghi nhận trong vòng 180 ngày. Giao dịch từ 50.000.000 VND trở lên cần hai người phê duyệt trước khi gọi cổng thanh toán.

| Mã | Quy tắc | Ngưỡng | Điểm thực thi | Trạng thái |
|---|---|---|---|---|
| BR-004 | Phê duyệt kép | ≥ 50.000.000 VND | Workflow engine | {{status:green\|Đã duyệt}} |
| BR-005 | Thời hạn hoàn tiền | 180 ngày | Refund service | {{status:green\|Đã duyệt}} |

| Thuật ngữ | Cách dùng | Ghi chú |
|---|---|---|
| Refund | Hoàn tiền | Dùng thống nhất trong toàn bộ tài liệu |
| Idempotency key | Khóa bất biến | Không dịch khi trích dẫn tên header |
```

### Example 3 — Validate the Vietnamese document contract

```bash
# The fds-vi profile checks Vietnamese section names, diacritics and structure.
python3 scripts/validate_document.py fds.vi.md --profile fds-vi --min-score 90 --publish

# Read the page aloud once; then test headings and tables with a screen reader.
python3 scripts/md2storage.py fds.vi.md -o fds.vi.storage.html --check
```

## 10. Implementation Checklist

- [ ] Every section opens with a one- or two-sentence answer before evidence.
- [ ] Paragraphs stay at three to five sentences and sentences at 25 words or fewer where possible.
- [ ] Headings are descriptive, numbered and use real heading levels without skipping.
- [ ] Every link names its destination and purpose; no "here" or "tại đây".
- [ ] Every image has alt text that states the conclusion; complex diagrams have a text equivalent.
- [ ] Status uses a text label in addition to colour, and tables have header rows.
- [ ] The page reflows at 200% zoom without horizontal scrolling for prose.
- [ ] Acronyms are expanded on first use and the glossary is linked.
- [ ] Vietnamese text keeps its diacritics and uses one stable term per concept.
- [ ] A screen-reader pass covers headings, links, tables and status announcements before approval.
