# New Confluence Document

Author a Confluence-ready document from this repository's templates. Do not publish.

1. Ask for the document type, feature name, Confluence space, Jira key, owner and reviewers if they are not already known. If a fact is missing, keep an explicit placeholder and set status `Draft`.
2. Read `SKILL.md` and the one discipline guide that matches the document type.
3. Copy the matching template from `assets/templates/` into the working directory. Never edit the template in place.
4. Fill the frontmatter first, then the body: purpose and scope, requirement or contract rows, evidence, risks and open questions, change log.
5. Run the linter with the matching profile and `--publish`; fix every error and review every warning.
6. Convert with `scripts/md2storage.py ... --check` and confirm the fragment is well formed.
7. Report the source file, storage file, lint score, remaining placeholders and the exact `confluence.py create` command. Do not claim the page exists.
