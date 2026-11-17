# 📄 Confluence Documents — 12 Enterprise Documentation Disciplines

A production-oriented OpenCode skill for creating, updating and auditing documents in **Atlassian Cloud Confluence**. It turns Markdown into safe Confluence storage XHTML, enforces a professional formatting contract instead of bullet walls, and provides a controlled publish protocol with backups, diffs, version messages and verification.

The skill is built for the documents enterprises actually run on: functional design specifications (FDS), API contracts, RFCs, runbooks, release notes, postmortems and architecture decision records. It supports Vietnamese authoring end to end, including a Vietnamese FDS template, a completed example and a dedicated lint profile.

## ✨ What Makes This Different

- **Formatting is enforceable, not aspirational.** `validate_document.py` fails bullet-only sections, missing document control blocks, unsynced change logs, orphan requirements, colour-only status, vague link text and ASCII-only Vietnamese headings.
- **Publishing is a controlled operation.** `confluence.py` reads before writing, backs up existing storage, refuses blind conflicts, requires a version message and verifies the remote hash after publish.
- **Markdown is the source, storage is generated.** `md2storage.py` emits a conservative XHTML subset with allowlisted macros, CDATA code blocks and accessibility attributes.
- **Twelve disciplines, one contract.** Each guide follows the same 10-section standard and composes with the others through an explicit, symmetric combination matrix.
- **No credentials required to start.** Authoring, linting and conversion work offline. Only the final read/write needs an Atlassian API token.

## 📂 Skill List

| # | Skill | Folder | Summary |
|---|-------|--------|---------|
| 1 | [Document Architecture](./skills/01-document-architecture/SKILL.md) | `01-document-architecture` | The fixed page skeleton: title formula, document control block, TOC, numbered sections, appendices and the 30-second comprehension test. |
| 2 | [FDS and Requirements](./skills/02-fds-requirements/SKILL.md) | `02-fds-requirements` | Atomic requirements, FR/NFR/BR/AC identifiers, MoSCoW priority, Given-When-Then acceptance criteria and traceability. |
| 3 | [Visual Hierarchy](./skills/03-visual-hierarchy/SKILL.md) | `03-visual-hierarchy` | Enterprise formatting: answer-first sections, tables over bullets, panels, status lozenges, expandable depth and density budgets. |
| 4 | [Storage Format](./skills/04-storage-format/SKILL.md) | `04-storage-format` | Confluence Cloud storage XHTML: safe tags, macro anatomy, escaping, CDATA, images, anchors and the raw-storage escape hatch. |
| 5 | [Tables and Matrices](./skills/05-tables-matrices/SKILL.md) | `05-tables-matrices` | Requirement indexes, decision logs, risk registers, RACI, error catalogues and traceability matrices with accessibility-safe structure. |
| 6 | [Diagrams](./skills/06-diagrams/SKILL.md) | `06-diagrams` | C4, sequence, state and ER diagrams, Mermaid/PlantUML sources, captions, alt text and the diagram-versus-table decision. |
| 7 | [Jira Traceability](./skills/07-jira-traceability/SKILL.md) | `07-jira-traceability` | Issue keys in tables, Jira macros, remote links, two-way traceability, status drift and the label taxonomy. |
| 8 | [Update and Versioning](./skills/08-update-versioning/SKILL.md) | `08-update-versioning` | Read-before-write, backups, section-level diffs, version rules, mandatory messages, change logs and conflict handling. |
| 9 | [API Contracts](./skills/09-api-contracts/SKILL.md) | `09-api-contracts` | OpenAPI as canonical schema, endpoint and error tables, idempotency, pagination, rate limits, compatibility and contract tests. |
| 10 | [Review and Governance](./skills/10-review-governance/SKILL.md) | `10-review-governance` | Document states, entry/exit criteria, named reviewers, RACI, finding logs, version-specific sign-off and review cadence. |
| 11 | [Readability and Accessibility](./skills/11-readability-accessibility/SKILL.md) | `11-readability-accessibility` | Plain language, sentence budgets, descriptive links, alt text, status semantics, zoom, screen readers and Vietnamese typography. |
| 12 | [Automation and Quality](./skills/12-automation-quality/SKILL.md) | `12-automation-quality` | Deterministic conversion, lint gates, idempotent publishing, dry runs, backups, verification, drift audits and CI pipelines. |

## 🚀 Quick Start

### 1. Author and validate offline

```bash
# See a passing contract: the completed Vietnamese example scores 100.
python3 scripts/validate_document.py assets/examples/fds-payment-refund.vi.md \
  --profile fds-vi --min-score 85 --publish

# Start a new document from a template, fill every placeholder, then lint.
cp assets/templates/fds.vi.md refund-fds.vi.md
python3 scripts/validate_document.py refund-fds.vi.md --profile fds-vi --min-score 90 --publish

# Convert to Confluence storage XHTML and validate the fragment.
python3 scripts/md2storage.py refund-fds.vi.md -o refund-fds.storage.html \
  --manifest refund-fds.json --check
```

A completed reference document lives at [`assets/examples/fds-payment-refund.vi.md`](./assets/examples/fds-payment-refund.vi.md).

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your site, email and API token.
python3 scripts/confluence.py --env-file .env whoami
```

Required variables: `CONFLUENCE_BASE_URL` (for example `https://your-site.atlassian.net/wiki`), `CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN`. `ATLASSIAN_BASE_URL`, `ATLASSIAN_EMAIL` and `ATLASSIAN_API_TOKEN` are accepted as aliases. Create a token at <https://id.atlassian.com/manage-profile/security/api-tokens>.

**Never paste a token into chat or commit `.env`.** The skill works offline without credentials; only the final read/write requires them.

### 3. Create or update a page

```bash
# Find an existing page before creating a duplicate.
python3 scripts/confluence.py --env-file .env search --title "Payment refund" --space PAY

# Create: dry run first, then write.
python3 scripts/confluence.py --env-file .env create --from-md refund-fds.vi.md \
  --space PAY --parent-id 123456 --dry-run
python3 scripts/confluence.py --env-file .env create --from-md refund-fds.vi.md \
  --space PAY --parent-id 123456

# Update: read, diff, write with a real message, verify.
python3 scripts/confluence.py --env-file .env get --page-id 12345 --out .work/current.html
python3 scripts/confluence.py --env-file .env diff --page-id 12345 --from-md refund-fds.vi.md
python3 scripts/confluence.py --env-file .env update --page-id 12345 --from-md refund-fds.vi.md \
  --message "v1.1 — BR-004: dual approval at 50,000,000 VND" --update-labels
python3 scripts/confluence.py --env-file .env verify --page-id 12345
```

## 🧩 Templates and Profiles

| Template | Document | Language | Lint profile | Required sections |
|---|---|---|---|---|
| [`fds.md`](./assets/templates/fds.md) | Functional Design Specification | English | `fds` | 12 + appendices |
| [`fds.vi.md`](./assets/templates/fds.vi.md) | Đặc tả thiết kế chức năng | Vietnamese | `fds-vi` | 12 + phụ lục |
| [`api-spec.md`](./assets/templates/api-spec.md) | API Specification | English | `api` | 9 |
| [`rfc.md`](./assets/templates/rfc.md) | Request for Comments | English | `rfc` | 8 |
| [`runbook.md`](./assets/templates/runbook.md) | Operations Runbook | English | `runbook` | 7 |
| [`release-notes.md`](./assets/templates/release-notes.md) | Release Notes | English | `release` | 6 |
| [`postmortem.md`](./assets/templates/postmortem.md) | Incident Postmortem | English | `postmortem` | 8 |
| [`adr.md`](./assets/templates/adr.md) | Architecture Decision Record | English | `adr` | 6 |
| [`fds-payment-refund.vi.md`](./assets/examples/fds-payment-refund.vi.md) | Completed reference FDS | Vietnamese | `fds-vi` | 12 + phụ lục |

## 🔄 Combination Matrix

Each guide composes with the others. `✅` means the pairing is safe and recommended by default; `⚠️` means it works only with the condition described in the guides' combination notes.

| | Architecture | FDS | Hierarchy | Storage | Tables | Diagrams | Jira | Versioning | API | Review | Readability | Automation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Document Architecture** | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **FDS and Requirements** | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| **Visual Hierarchy and Formatting** | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Storage Format** | ✅ | ✅ | ✅ | — | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Tables and Matrices** | ✅ | ✅ | ✅ | ✅ | — | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Diagrams and Visuals** | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Jira Traceability** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Update and Versioning** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| **API Contracts** | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| **Review and Governance** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ⚠️ |
| **Readability and Accessibility** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| **Automation and Quality** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | — |

## 🧪 Quality Gates

Run the repository check before opening a pull request:

```bash
python3 scripts/validate_skills.py
```

It verifies:

1. All 12 guide folders exist and follow the 10-section standard.
2. Frontmatter is present and `related` references resolve.
3. `skills/data.json` covers all 12 skills and mirrors every guide section.
4. The combination matrix is symmetric and matches the README.
5. Every template converts to well-formed storage XHTML.
6. The completed Vietnamese example scores at least 85 with `--profile fds-vi --publish`.
7. Repository hygiene: no secrets, no `.env`, no generated storage or backup directories committed.

The GitHub Actions workflow in [`.github/workflows/validate.yml`](./.github/workflows/validate.yml) runs the same gates on every push and pull request.

## 📁 Repository Layout

```text
skill-confluence-documents/
├── SKILL.md                     # Agent router: contract, workflow, publish protocol
├── README.md                    # This file: overview, usage, matrix
├── assets/
│   ├── templates/               # Canonical Markdown templates (English + Vietnamese FDS)
│   ├── examples/                # Completed, lint-clean reference document
│   └── terminology/             # Vietnamese–English glossary
├── skills/
│   ├── 01-document-architecture/SKILL.md
│   ├── …
│   ├── 12-automation-quality/SKILL.md
│   ├── data.json                # Machine-readable 12-skill contract
│   └── assets/references.md     # Curated external references
├── scripts/
│   ├── md2storage.py            # Markdown → Confluence storage XHTML
│   ├── validate_document.py     # Document formatting and quality linter
│   ├── confluence.py            # Safe Confluence Cloud API CLI
│   └── validate_skills.py       # Repository CI contract
├── plan/readme.md               # Design decisions and quality gates
├── .github/workflows/validate.yml
├── .env.example
└── LICENSE
```

## 🇻🇳 Vietnamese Support

- `assets/templates/fds.vi.md` uses Vietnamese section names recognized by `--profile fds-vi`.
- `assets/examples/fds-payment-refund.vi.md` is a fully populated, lint-clean example with Vietnamese prose, Jira macros and decision tables.
- The linter transliterates Vietnamese headings before profile matching, so diacritics are preserved in content while section names still resolve.
- The glossary at [`assets/terminology/vi-en-glossary.md`](./assets/terminology/vi-en-glossary.md) fixes one Vietnamese term per concept.
- Version messages, change logs and review records may be written in Vietnamese; keep dates in ISO format and Jira keys unchanged.

## 📚 References

- [Curated references](./skills/assets/references.md) — Atlassian Cloud REST API, storage format, WCAG 2.2, OpenAPI 3.1, docs-as-code.
- [Design plan](./plan/readme.md) — architecture, decisions and validation strategy.
- [Machine-readable data](./skills/data.json) — definitions, principles, tokens, composition, patterns, use cases, combinations, anti-patterns and accessibility contracts.

## Version

- **Schema version:** 1.0 (`skills/data.json` → `meta.version`)
- **Skills:** 12
- **Token prefixes:** `--doc-*`, `--req-*`, `--storage-*`, `--table-*`, `--diagram-*`, `--jira-*`, `--update-*`, `--api-*`, `--gov-*`, `--read-*`, `--auto-*`
- **Runtime:** Python 3.11+ standard library only; no third-party dependencies
- **Platform:** Atlassian Cloud Confluence (`*.atlassian.net`), REST API v2 + v1

## License

MIT — see [LICENSE](./LICENSE).
