---
title: "{Service} — Operations Runbook"
doc_id: RUN-{DOMAIN}-001
version: 1.0
status: Approved
owner: "{SRE Owner}"
reviewers: ["{Service Owner}", "{On-call Lead}"]
jira: "{EPIC-KEY}"
space: "{SPACE}"
labels: [runbook, operations, "{domain}"]
classification: Internal
updated: "{YYYY-MM-DD}"
---

{{meta}}

{{toc}}

## 1. Overview

This runbook tells an on-call engineer how to detect, mitigate and recover {Service} incidents without relying on tribal knowledge. Follow it exactly during an incident; propose improvements afterwards through the change log.

| Attribute | Value |
|---|---|
| Service | {Service name} |
| Tier | {1 / 2 / 3} |
| On-call rotation | {PagerDuty or Opsgenie schedule} |
| Primary dashboard | [{Dashboard name}]({URL}) |
| Alert channel | {Slack channel} |
| Deployment pipeline | [{Pipeline name}]({URL}) |
| Last game day | {YYYY-MM-DD} |

:::warning
If customer impact is ongoing, mitigate first and diagnose second. A known-good rollback in 5 minutes beats a perfect root-cause analysis in 60.
:::

## 2. Prerequisites

| Requirement | Detail | Verify |
|---|---|---|
| Access | Production read/write role | `kubectl auth can-i` returns `yes` |
| Access | Incident tool | You can open and update an incident |
| Access | Secret manager | You can read `{secret-path}` |
| Tooling | `kubectl` {version}+ | `kubectl version --client` |
| Tooling | `{service}` CLI {version}+ | `{service} --version` |
| Knowledge | This runbook read end-to-end | You can explain the rollback trigger |

```bash
# Verify context before touching production.
kubectl config current-context
kubectl -n {namespace} get pods -l app={service}
```

## 3. Procedure

### 3.1 Assess impact

1. Open the {dashboard} and confirm the alert is real, not a stale threshold.
2. Check the customer-impact banner: {status page link}.
3. Record the incident start time in UTC and open an incident channel.
4. Classify severity using the table below and page the escalation path in section 6 if SEV-1 or SEV-2.

| Severity | Definition | Response target |
|---|---|---|
| SEV-1 | {Customer-facing outage or data loss} | Acknowledge in 5 minutes |
| SEV-2 | {Degraded experience for a large segment} | Acknowledge in 15 minutes |
| SEV-3 | {Internal-only or single-tenant impact} | Acknowledge in 1 hour |

### 3.2 Stabilise the service

1. Capture the current state before changing anything.
2. Apply the narrowest mitigation that addresses the observed failure.
3. Verify the mitigation with the health commands below.
4. If the mitigation fails twice, stop and escalate rather than experimenting in production.

```bash
# Capture state for the incident record.
kubectl -n {namespace} get deploy {service} -o yaml > /tmp/{service}-deploy-$(date +%s).yaml
kubectl -n {namespace} get pods -l app={service} -o wide
kubectl -n {namespace} logs -l app={service} --tail=200 --since=15m
```

```bash
# Health verification after a mitigation.
curl -fsS "https://{service}.{domain}.example.com/health/ready" | jq .
curl -fsS "https://{service}.{domain}.example.com/metrics" | grep '{metric_name}'
```

### 3.3 Recover

| Step | Action | Success signal |
|---|---|---|
| 1 | {Restart, scale or fail over} | Pods ready; error rate falling |
| 2 | {Drain or replay queue} | Consumer lag below {threshold} |
| 3 | {Re-enable traffic gradually} | p95 latency below {threshold} |
| 4 | {Close the incident} | No alerts for 30 minutes |

## 4. Rollback

| Trigger | Rollback action | Expected duration | Owner |
|---|---|---|---|
| {Error rate above X% for 5 min} | `{rollback command}` | 5 minutes | On-call |
| {Latency above X ms for 10 min} | {Previous release or feature flag off} | 2 minutes | On-call |
| {Data integrity alarm} | Stop writes, restore from {snapshot} | {RTO} | Data owner |

```bash
# Roll back the application to the previous release.
{rollback command}
kubectl -n {namespace} rollout status deploy/{service} --timeout=5m
```

:::note
Record the release tag or image digest you rolled back from. The postmortem needs it, and a second rollback may need the same reference.
:::

## 5. Troubleshooting

| Symptom | Likely cause | Check | Action |
|---|---|---|---|
| `{ERROR_CODE}` in logs | {Cause} | `{query}` | {Mitigation} |
| Pods crash-looping | {Cause} | `kubectl describe pod` | {Mitigation} |
| High latency, low CPU | {Cause} | {Dashboard panel} | {Mitigation} |
| Queue lag increasing | {Cause} | {Queue metric} | {Mitigation} |
| 5xx from dependency | {Cause} | {Dependency status page} | {Fallback or escalate} |

## 6. Escalation

| Level | Contact | When | Channel |
|---|---|---|---|
| L1 | On-call engineer | First response | {Pager} |
| L2 | Service owner: {Name} | Mitigation failed or data risk | {Phone or pager} |
| L3 | Engineering manager: {Name} | SEV-1 or prolonged outage | {Phone} |
| Vendor | {Vendor support} | Confirmed vendor outage | {Portal or phone} |

1. Escalate when the response target for the severity is breached.
2. Escalate immediately for suspected data loss, security incident or regulatory exposure.
3. Hand over with a written summary: impact, actions taken, current state, next step.

## 7. Change Log

| Version | Date | Author | Change | Jira |
|---|---|---|---|---|
| 1.0 | {YYYY-MM-DD} | {SRE Owner} | Initial approved runbook | {{jira:{EPIC-KEY}}} |
