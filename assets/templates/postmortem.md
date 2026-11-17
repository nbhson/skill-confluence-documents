---
title: "Postmortem: {Incident title}"
doc_id: PM-{DOMAIN}-001
version: 1.0
status: Approved
owner: "{Incident Commander}"
reviewers: ["{Service Owner}", "{SRE Lead}"]
jira: "{INCIDENT-KEY}"
space: "{SPACE}"
labels: [postmortem, incident, "{domain}"]
classification: Internal
updated: "{YYYY-MM-DD}"
---

{{meta}}

{{toc}}

## 1. Summary

{Two or three sentences: what happened, how long it lasted, who was affected, and the single most important corrective action. Blameless: describe systems and decisions, never individuals.}

:::info
**Incident severity:** {SEV-1 / SEV-2 / SEV-3}. **Duration:** {start} to {end} UTC ({duration}). **Customer impact:** {one sentence}. **Detection:** {alert, customer report or internal test}.
:::

| Attribute | Value |
|---|---|
| Incident ID | {INC-YYYY-NNN} |
| Severity | {SEV-1 / SEV-2 / SEV-3} |
| Start (UTC) | {YYYY-MM-DD HH:mm} |
| Detection (UTC) | {YYYY-MM-DD HH:mm} |
| Mitigated (UTC) | {YYYY-MM-DD HH:mm} |
| Resolved (UTC) | {YYYY-MM-DD HH:mm} |
| Incident commander | {Name} |
| Services affected | {Service names} |
| Detection source | {Alert name / customer report} |

## 2. Impact

| Dimension | Detail | Evidence |
|---|---|---|
| Customers affected | {Number or percentage} | {Dashboard or query} |
| Requests failed | {Number or percentage} | {Metric} |
| Revenue impact | {Estimate or Not applicable} | {Finance or billing source} |
| Data integrity | {No data loss / records affected} | {Audit result} |
| SLA / SLO | {Budget consumed} | {SLO dashboard} |
| Regulatory | {Notification required / none} | {Compliance assessment} |

## 3. Timeline

All times are UTC. Include the detection gap and the mitigation delay explicitly; those are the two intervals the action items should shrink.

| Time | Event | Actor or system |
|---|---|---|
| {HH:mm} | {Change deployed or triggering event} | {Team or system} |
| {HH:mm} | {First customer impact} | {System} |
| {HH:mm} | {Alert fired or report received} | {Monitoring or customer} |
| {HH:mm} | {Incident declared; commander assigned} | {On-call} |
| {HH:mm} | {First mitigation attempted} | {Team} |
| {HH:mm} | {Mitigation effective} | {Team} |
| {HH:mm} | {Service fully restored} | {Team} |
| {HH:mm} | {Incident closed; monitoring confirmed} | {Commander} |

## 4. Root Cause

{Explain the causal chain: trigger, latent condition, and why existing safeguards did not prevent or contain it. Distinguish the trigger from the root cause.}

:::note
Use the "5 whys" only to find the system condition, not to assign blame. Stop when the answer is a missing control that can be fixed.
:::

### 4.1 Contributing factors

| Factor | Category | How it contributed | Evidence |
|---|---|---|---|
| {Factor} | Technical / process / organisational | {Causal link} | {Log, metric or review} |
| {Factor} | Technical / process / organisational | {Causal link} | {Log, metric or review} |
| {Factor} | Technical / process / organisational | {Causal link} | {Log, metric or review} |

## 5. Resolution

| Step | Action | Result |
|---|---|---|
| 1 | {Immediate mitigation} | {Impact stopped or reduced} |
| 2 | {Stabilisation} | {Service healthy} |
| 3 | {Data repair or replay} | {Integrity confirmed} |
| 4 | {Monitoring period} | {No recurrence for X hours} |

## 6. Action Items

| ID | Action | Type | Owner | Priority | Due | Status |
|---|---|---|---|---|---|---|
| AI-001 | {Prevent recurrence} | Preventive | {Owner} | P1 | {YYYY-MM-DD} | {{status:red\|Open}} |
| AI-002 | {Detect faster} | Detective | {Owner} | P1 | {YYYY-MM-DD} | {{status:yellow\|In Progress}} |
| AI-003 | {Limit blast radius} | Mitigating | {Owner} | P2 | {YYYY-MM-DD} | {{status:grey\|Planned}} |
| AI-004 | {Improve runbook or process} | Process | {Owner} | P2 | {YYYY-MM-DD} | {{status:grey\|Planned}} |

:::warning
An action item without an owner, a due date and a tracking issue is a wish. Link every row to a Jira key before approving this postmortem.
:::

## 7. Lessons Learned

| What worked | What did not | What changes |
|---|---|---|
| {Effective detection, tool or decision} | {Gap in alerting, access or process} | {Specific change and owner} |
| {Effective detection, tool or decision} | {Gap in alerting, access or process} | {Specific change and owner} |
| {Effective detection, tool or decision} | {Gap in alerting, access or process} | {Specific change and owner} |

## 8. Change Log

| Version | Date | Author | Change | Jira |
|---|---|---|---|---|
| 1.0 | {YYYY-MM-DD} | {Incident Commander} | Postmortem approved | {{jira:{INCIDENT-KEY}}} |
