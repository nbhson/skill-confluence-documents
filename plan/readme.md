# Design Plan — Confluence Documents Skill

## Goal

Build an OpenCode skill that reliably produces enterprise-grade Confluence Cloud documents: structurally complete, visually scannable, traceable to Jira, accessible and safe to publish. The skill must work for a human author and for an agent that has no prior knowledge of a tenant.

The failure mode this repository exists to prevent: a page that is a wall of bullets, has no owner or version, cannot be traced to an issue, and is published by overwriting the live page from a stale copy.

## Constraints

- **Platform:** Atlassian Cloud (`*.atlassian.net`), Confluence Cloud REST API v2 and the storage format.
- **Runtime:** Python 3.11+ standard library only. No third-party packages, no build step.
- **No configured Confluence/Jira MCP server and no credentials in the development environment.** The authoring path must be fully testable offline; live publishing is verified by unit-level command construction and by fail-closed behaviour when credentials are absent.
- **Bilingual:** English canonical templates and guides, plus a complete Vietnamese FDS template, example and lint profile.
- **Agent-first:** a root router with a non-negotiable contract, a short workflow and a clear no-credential fallback. Sub-guides are loaded only when needed.

## Architecture

```text
Markdown + frontmatter
        │
        ├── validate_document.py ──► formatting contract score
        │
        ├── md2storage.py ─────────► storage XHTML + manifest
        │                              │
        │                              ├── diff (live page vs source)
        │                              ├── backup (.confluence-backups/)
        │                              └── create / update / upsert
        │                                            │
        │                                            └── verify (hash + version)
        │
        └── confluence.py ─────────► REST API v2/v1
```

### Why Markdown is the source

Confluence storage XHTML is an implementation detail with macro-specific quirks, CDATA rules and editor round-tripping. Authoring directly in storage invites malformed pages and unreadable diffs. Markdown is reviewable in a pull request, diffable, portable and convertible deterministically. The generated storage is an artefact, never the source of truth.

### Why the frontmatter contract

A page without owner, status, version and Jira key cannot be governed. Frontmatter makes those fields machine-readable, lets `{{meta}}` render a consistent control table, and gives the linter something to enforce. The control block is the first screen a reviewer sees.

### Why tables over bullets

Bullets flatten priority: every item looks equally important and attributes cannot be compared across items. Enterprise documents need requirement indexes, risk registers, decision logs and traceability matrices. The linter enforces a bullet-ratio budget (≤ 35%) and rejects bullet-only sections. The visual-hierarchy guide defines the replacement patterns: lede, table, decision panel, expand.

### Why a separate linter

The converter guarantees well-formed XHTML; it cannot know whether a change log matches the frontmatter version, whether every FR has an acceptance criterion, or whether a link says "here". `validate_document.py` encodes the editorial contract as findings with rule IDs, severity and a score. It is the difference between "renders" and "reviewable".

### Why a safe CLI instead of raw API calls

The CLI centralises the risky parts of publishing: credential handling, URL normalisation, backups, version conflict detection, content-hash idempotency, post-write verification and consistent error messages. Agents should not hand-craft `curl` calls against a production wiki.

## Document Contract

All document profiles share the same spine:

1. Frontmatter with identity and governance fields.
2. `{{meta}}` control table.
3. `{{toc}}` for pages with six or more H2 sections.
4. Numbered H2 sections, depth at most H3.
5. Answer-first paragraphs before evidence.
6. Tables for parallel facts, panels for decisions, expands for optional depth.
7. Change log as the last numbered section, synced to the frontmatter version.
8. Appendices for glossary and long reference material.

Profiles add required section names and domain checks:

| Profile | Document | Notable checks |
|---|---|---|
| `fds` | Functional Design Specification | FR/NFR/BR/AC IDs, traceability, acceptance criteria |
| `fds-vi` | Vietnamese FDS | Transliterated headings, Vietnamese section names, diacritics |
| `api` | API Specification | Endpoint, error, auth, versioning sections |
| `rfc` | Request for Comments | Alternatives, risks, rollout, open questions |
| `runbook` | Operations Runbook | Procedure, rollback, troubleshooting, escalation |
| `release` | Release Notes | Highlights, breaking changes, migration, known issues |
| `postmortem` | Incident Postmortem | Impact, timeline, root cause, action items |
| `adr` | Architecture Decision Record | Context, decision, consequences, alternatives |
| `generic` | Any page | Structural checks without a domain section list |

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Source format | Markdown + YAML frontmatter | Reviewable, diffable, portable |
| Conversion | Custom stdlib converter | No dependencies; conservative XHTML subset |
| Macro syntax | Directives (`:::info`) and macros (`{{toc}}`) | Readable in source, deterministic in output |
| Storage escape hatch | Fenced `storage` blocks | Reviewed exception, not the default |
| Lint model | Profiles + weighted score + `--publish` | One engine, domain-specific contracts |
| Publish semantics | `update` requires `--message`; `upsert` is hash-idempotent | Audit trail and no empty versions |
| Conflict policy | Stop on 409 | Never overwrite a human edit |
| Backups | Local timestamped snapshots | Rollback without relying on the wiki |
| Verification | Re-fetch and compare hash/version | Success is proven, not assumed |
| Language | English canonical + Vietnamese specialization | Shared structure, local readability |
| Dependencies | Python standard library only | Runs anywhere, no supply-chain surface |

## Quality Gates

`python3 scripts/validate_skills.py` is the repository contract. It fails when:

1. A guide folder is missing, misnumbered or does not have the 10-section anatomy.
2. Frontmatter is missing or a `related` reference does not resolve.
3. `skills/data.json` does not mirror the guides (definition, principles, tokens, composition, patterns, use cases, anti-patterns, accessibility).
4. A combination is asymmetric or lists a skill twice.
5. The README matrix differs from `data.json`.
6. A template does not convert to well-formed storage XHTML.
7. The completed Vietnamese example has a publication error or scores below 85.
8. The root router, references, glossary, plan, CI workflow, env example or licence is missing.
9. A generated directory (`.work`, `.confluence-backups`), `.env` file or likely secret is present.

The second gate is the document contract itself:

```bash
python3 scripts/validate_document.py assets/examples/fds-payment-refund.vi.md \
  --profile fds-vi --min-score 85 --publish
```

## Testing Strategy

| Layer | Test | Status |
|---|---|---|
| Converter | Every template and the completed example convert with `--check` | Automated in CI |
| Linter | The completed example scores 100/100 with `--publish` | Automated in CI |
| CLI construction | `--help`, argument parsing and missing-credential failure | Manual (offline) |
| Storage validity | `xml.etree` well-formedness on every conversion | Automated |
| Repository contract | 12 guides, data.json parity, matrix symmetry | Automated in CI |
| Live publish | Create/update/verify against a real Confluence Cloud site | Blocked: no credentials or MCP server in this environment |

The live-publish gap is deliberate and documented. The CLI fails closed with an actionable message when credentials are missing; it never pretends to publish. Adding credentials and running `whoami` is the first step in a tenant-specific smoke test.

## Known Limitations

- **No live tenant verification in this repository.** Page create/update/verify paths are exercised only through argument handling and error paths until credentials exist.
- **Macro availability varies by tenant.** Mermaid, PlantUML and Jira macros depend on installed apps. The guides require confirming the macro name and falling back to tables or links.
- **The CLI does not manage comments, permissions or page restrictions.** Those remain manual governance steps; the review guide defines the evidence.
- **The linter is editorial, not factual.** A 100 score proves structure and formatting, not correctness.
- **Vietnamese profile checks headings and diacritics, not translation quality.** A human reviewer remains mandatory.
- **No automatic Jira status sync.** The `jira-link` command manages remote links; live status reconciliation is a scheduled audit or a human check.

## Maintenance

1. Edit the guide and its examples.
2. Update `skills/data.json` to mirror the guide; keep combinations symmetric.
3. Regenerate the README matrix from `data.json`.
4. Run `python3 scripts/validate_skills.py --verbose`.
5. Run the example lint with `--publish`.
6. If the schema changes, bump `meta.version` in `data.json` and update the README version section.

## Acceptance Criteria

- [x] Twelve discipline guides with the 10-section standard.
- [x] Eight templates covering FDS, API, RFC, runbook, release, postmortem and ADR, plus the Vietnamese FDS.
- [x] A completed Vietnamese FDS example at 100/100 with `--publish`.
- [x] A converter, linter and safe Confluence CLI using only the standard library.
- [x] Root router with the formatting contract, create/update protocols and no-credential fallback.
- [x] Machine-readable `data.json` with symmetric combinations and mirrored anti-patterns.
- [x] README matrix, glossary, references, CI workflow and repository contract checker.
- [ ] Live create/update/verify smoke test against a real Confluence Cloud tenant (requires credentials).
