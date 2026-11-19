# 📄 Confluence Documents — 12 Enterprise Documentation Disciplines

A production-oriented OpenCode skill for creating, updating and auditing documents in **Atlassian Cloud Confluence**. It turns Markdown into safe Confluence storage XHTML, enforces a professional formatting contract instead of bullet walls, and provides a controlled publish protocol with backups, diffs, version messages and verification.

The skill is built for the documents enterprises actually run on: functional design specifications (FDS), API contracts, RFCs, runbooks, release notes, postmortems and architecture decision records. It supports Vietnamese authoring end to end, including a Vietnamese FDS template, a completed example and a dedicated lint profile.

## ✨ What Makes This Different

- **Formatting is enforceable, not aspirational.** `validate_document.py` fails bullet-only sections, missing document control blocks, unsynced change logs, orphan requirements, colour-only status, vague link text and ASCII-only Vietnamese headings.
- **Publishing is a controlled operation.** `confluence.py` reads before writing, backs up existing storage, refuses blind conflicts, requires a version message and verifies the remote hash after publish.
- **Markdown is the source, storage is generated.** `md2storage.py` emits a conservative XHTML subset with allowlisted macros, CDATA code blocks and accessibility attributes.
- **Display format is a decision, not decoration.** A closed Confluence palette — titled info/tip/warning/note panels, expands, two- and three-column layouts, task lists, status lozenges, dates, emoticons, embeds, code/math/diagram macros and a raw-storage escape hatch — with a container-ladder rule, lint budgets and an unknown-macro fail-closed. See the Step 2b palette, the catalogue in guide 04 and the [format showcase](./assets/examples/confluence-format-showcase.md).
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

# See every supported Confluence display container in one page.
python3 scripts/validate_document.py assets/examples/confluence-format-showcase.md \
  --profile generic --min-score 90 --publish
python3 scripts/md2storage.py assets/examples/confluence-format-showcase.md \
  -o showcase.storage.html --check

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

## 🤖 Use With Other Agents

`SKILL.md` is the canonical router and formatting contract. The adapters below are thin entry points for hosts that do not load OpenCode skills automatically; they point back to `SKILL.md` instead of duplicating it.

| Host | Entry point | How it loads |
|---|---|---|
| Claude Code | `CLAUDE.md` | Project memory; or link the repository into `~/.claude/skills/confluence-documents` so `SKILL.md` is discovered as a skill. |
| GitHub Copilot | `.github/copilot-instructions.md` | Repository instructions for Copilot Chat and the coding agent. Use agent mode to run the scripts. |
| Cline | `.clinerules/confluence-documents.md` | Workspace rules. Workflows in `.clinerules/workflows/` are invoked as `/new-document.md`, `/publish-page.md` and `/audit-document.md`. |
| Codex, Gemini CLI, Cursor, Windsurf, Aider | `AGENTS.md` | Host-neutral entry point for any agent with file reads and shell access. |

Claude Code global install:

```bash
ln -s "$(pwd)" ~/.claude/skills/confluence-documents
```

Note: hosts that validate the skill name against the folder name expect the folder **`confluence-documents`** — the frontmatter `name`. Cloning the repository directly into the skills directory as `skill-confluence-documents` will not be discovered; symlink or rename the folder instead.

The scripts stay host-independent: Python 3.11+ standard library only, invoked from a shell. Copilot in plain chat mode cannot execute them; authoring and linting then remain manual.

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
| [`confluence-format-showcase.md`](./assets/examples/confluence-format-showcase.md) | Worked display-format reference | English | `generic` | 11 |

## 🎛 Confluence Display Formats

The skill chooses containers from a closed palette instead of inventing styling. Rule of thumb — the container ladder: **table → titled callout → titled expand → columns → task list → embed → raw storage fence**.

| Syntax | What it becomes on Confluence |
|---|---|
| `:::info Title` / `:::tip` / `:::warning` / `:::note` | Highlighted panel with a title (at most five per page) |
| `:::panel Title` / `:::expand Title` | Neutral panel / collapsible depth for long evidence |
| `:::columns` … `||` … `:::` | Two- or three-column layout section |
| `- [ ] item` / `- [x] done` | Task list that survives export and review |
| `{{status:green\|Approved}}`, `{{date:2026-11-19}}`, `{{jira:PAY-123}}`, `{{emoji:thumbs-up}}` | Status lozenge, locale-rendered date, live issue chip, emoticon |
| `{{embed:https://…}}` | Media embed (video, board, dashboard) |
| ` ```json title="file.json" `, ` ```math `, ` ```mermaid ` | Code macro with language and title, formula, diagram |
| `{{toc}}`, `{{children}}`, `{{include:SPACE:Title}}`, `{{anchor:id}}` | Structure helpers |
| ` ```storage ` | Reviewed raw XHTML escape hatch for anything exotic |

Unknown macros and directives fail closed at lint (`format.directive-unknown`, `format.macro-unknown`, `format.expand-untitled`, `format.callout-budget`) and again at conversion. Full catalogue: Example 0 in [guide 04](./skills/04-storage-format/SKILL.md); everything rendered live in [assets/examples/confluence-format-showcase.md](./assets/examples/confluence-format-showcase.md).

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
7. The format showcase converts cleanly and scores at least 90 with `--profile generic --publish`.
8. Host adapters exist for Claude Code, GitHub Copilot, Cline and generic agents, each points back to `SKILL.md`, and their routing tables carry the same (template, lint profile) pairs as the router.
9. Repository hygiene: no secrets, no `.env`, no generated storage or backup directories committed.

`scripts/test_confluence.py` additionally runs offline regression tests for the publishing CLI: credential parsing and aliases, fail-closed exits, env-file loading, version messages, backups, hashing, error hints, and `create --dry-run` without any network access.

The GitHub Actions workflow in [`.github/workflows/validate.yml`](./.github/workflows/validate.yml) runs the same gates on every push and pull request.

## 📁 Repository Layout

```text
skill-confluence-documents/
├── SKILL.md                     # Agent router: contract, workflow, publish protocol
├── README.md                    # This file: overview, usage, matrix
├── AGENTS.md                    # Host-neutral adapter: Codex, Gemini CLI, Cursor, …
├── CLAUDE.md                    # Claude Code adapter
├── .clinerules/                 # Cline rules and slash-command workflows
├── .github/
│   ├── copilot-instructions.md  # GitHub Copilot adapter
│   └── workflows/validate.yml
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
│   ├── test_confluence.py       # Offline regression tests for the CLI
│   └── validate_skills.py       # Repository CI contract
├── plan/readme.md               # Design decisions and quality gates
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
