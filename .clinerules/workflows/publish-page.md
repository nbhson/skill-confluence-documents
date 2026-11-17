# Publish or Update a Confluence Page

Publish a validated document through `scripts/confluence.py`. Never write from memory.

1. Confirm credentials with `python3 scripts/confluence.py --env-file .env whoami`. If credentials are missing, stop and deliver the local files plus the command to run later.
2. Search by exact title before creating: `search --title "..." --space KEY`.
3. **Existing page:** fetch the live storage with `get`, run `diff --from-md`, lint again if the source changed, then `update --message "vX.Y — AREA: change"` and `verify --file`.
4. **New page:** run `create --dry-run` first, review title, space, parent and payload, then repeat without `--dry-run` and `verify`.
5. Stop on HTTP 409, re-read the page and rebase. Never retry blindly.
6. Report the page title, page ID, URL, version, lint score and verification result. If nothing was written, say so plainly.
