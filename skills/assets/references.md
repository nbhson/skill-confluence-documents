# References

Curated sources for the Confluence Documents skill. Prefer primary documentation over blog summaries; check the date before relying on a product behaviour.

## Atlassian Cloud

| Source | Use for |
|---|---|
| [Confluence Cloud REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/) | Pages, spaces, labels, versions, attachments |
| [Confluence Cloud REST API v1](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/) | Legacy endpoints and Jira remote links |
| [Confluence storage format](https://developer.atlassian.com/cloud/confluence/understanding-confluence-storage-format/) | XHTML subset, macros, resource identifiers |
| [Confluence macros](https://support.atlassian.com/confluence-cloud/docs/insert-macros/) | Installed macro names and parameters |
| [Advanced search with CQL](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/) | Drift audits and page discovery |
| [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens) | Creating and rotating credentials |
| [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/) | Issue lookup and remote links |
| [Jira remote links](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/) | Two-way Confluence ↔ Jira traceability |

## Standards and Contracts

| Source | Use for |
|---|---|
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Accessibility criteria and conformance |
| [WAI page structure](https://www.w3.org/WAI/tutorials/page-structure/) | Headings, landmarks and reading order |
| [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html) | Machine-readable API schema |
| [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) | MUST / SHOULD / MAY requirement language |
| [Semantic Versioning](https://semver.org/) | Document and API version boundaries |
| [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) | Dates and UTC timestamps |
| [Idempotency-Key header](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/) | Retry-safe write contract |
| [Keep a Changelog](https://keepachangelog.com/) | Change-log structure and reader expectations |

## Documentation Practice

| Source | Use for |
|---|---|
| [Google developer documentation style guide](https://developers.google.com/style) | Plain language, terminology and code formatting |
| [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/) | Voice, procedures and global-ready wording |
| [Diátaxis](https://diataxis.fr/) | Separating tutorials, how-to, reference and explanation |
| [Write the Docs — docs as code](https://www.writethedocs.org/guide/docs-as-code/) | Source control, review and publishing pipelines |
| [C4 model](https://c4model.com/) | Context, container, component and code diagrams |
| [Mermaid](https://mermaid.js.org/) | Diagram source syntax and rendering |
| [PlantUML](https://plantuml.com/) | UML sequence, state and deployment diagrams |
| [Google API design guide](https://cloud.google.com/apis/design) | Resource naming, pagination, errors and versioning |

## Vietnamese Language

| Source | Use for |
|---|---|
| [Vietnamese language — typography](https://www.w3.org/International/articles/language-tags/) | Language tags (`vi-VN`) and screen-reader language |
| [Unicode Vietnamese](https://unicode.org/charts/PDF/U1EA0.pdf) | Precomposed characters and diacritics |
| [Vietnam government terminology portal](https://chinhphu.vn/) | Reference for administrative terms when a domain term is unclear |

## How to Use These Sources

1. Use the Atlassian API documentation for endpoint shapes and limits; this repository's CLI is a safe wrapper, not a replacement for the API contract.
2. Use WCAG 2.2 for acceptance criteria, not as a post-publication audit.
3. Use OpenAPI as the canonical schema and link it from the page; do not paste generated schemas into prose.
4. Use style guides for wording; use the [Vietnamese glossary](../assets/terminology/vi-en-glossary.md) for consistent terminology inside this repository.
