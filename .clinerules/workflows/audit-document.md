# Audit a Confluence Document

Review a document against the formatting contract without editing it unless asked.

1. Read `SKILL.md`, `skills/10-review-governance/SKILL.md` and `skills/11-readability-accessibility/SKILL.md`.
2. Run `python3 scripts/validate_document.py path/to/doc.md --profile PROFILE` and capture the score and findings.
3. If a page ID is available, fetch the live storage with `confluence.py get` and compare it with the Markdown source using `diff`.
4. Check the control block, change log, requirement IDs, Jira keys, table structure, link text, alt text and status semantics.
5. Report findings by severity, the score, the top fixes and the evidence. Do not rewrite the document unless the user asks.
