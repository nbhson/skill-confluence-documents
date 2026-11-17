# Confluence Documents — Claude Code Adapter

This repository is a portable Agent Skill for enterprise Confluence Cloud documents. [`SKILL.md`](./SKILL.md) is the canonical router and formatting contract; read it before authoring, converting, reviewing or publishing a page. Do not answer from memory or improvise a skeleton.

## Load the skill

**Project use:** this file is loaded as project memory. Read `SKILL.md`, then the one discipline guide that matches the task.

**Global use:** link the repository into Claude Code's skills directory so `SKILL.md` is discovered as a skill:

```bash
ln -s /absolute/path/to/skill-confluence-documents ~/.claude/skills/confluence-documents
```

Copy the whole repository if symlinks are unavailable — not only `SKILL.md` — so `skills/`, `scripts/` and `assets/` remain reachable. The frontmatter already satisfies the Agent Skills contract (`name: confluence-documents`).

## Operating rules

1. Read `SKILL.md` and exactly one relevant guide from `skills/`.
2. Start from the matching template in `assets/templates/`; never edit templates in place.
3. Lint with `scripts/validate_document.py ... --publish`, then convert with `scripts/md2storage.py ... --check`.
4. Publish only through `scripts/confluence.py`: search first, dry-run creates, and for updates use get → diff → update with a version message → verify.
5. Never invent page IDs, URLs, Jira keys, owners or approval dates.
6. Never ask for or echo an API token. Credentials come from `.env` per `.env.example`.
7. Read before write; stop on HTTP 409; back up and verify every write.
8. Report exactly what happened, including when nothing was published.
