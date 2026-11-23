# Engineering Design Doc / ADR: [Feature or System Name]

- **Status:** Draft | Proposed | Accepted | Superseded
- **Date:** YYYY-MM-DD

## 1. Context & Problem Statement
What concrete user or system problem are we solving right now, and what breaks if we do nothing?

## 2. Goals & Explicit Non-Goals
- **Goals (v1):**
  - ...
- **Non-Goals (Out of Scope):**
  - ...

## 3. Scale & SLO Assumptions
- **Traffic / Workload:** Read QPS, Write QPS, peak burst factor.
- **Data Size & Growth:** Item size, total dataset / DB footprint over 12 months.
- **Latency & Availability Targets:** `p50` / `p99` budget, acceptable recovery point/time.

## 4. Alternatives Considered

| Criterion | Option A (Simplest Baseline) | Option B (Proposed) | Option C |
| :--- | :--- | :--- | :--- |
| Complexity & Maintenance | Low | Medium | High |
| Latency / Throughput | ... | ... | ... |
| Failure Blast Radius | ... | ... | ... |

## 5. Proposed Architecture & Data Model
- Component responsibilities & dependency boundaries.
- Core schemas / state machine transitions.
- API contracts & idempotency keys.

## 6. Failure Modes, Security & Rollout Plan
- **Dependency Timeouts / Retries / Fallbacks:**
- **AuthZ, Tenant Isolation & Secrets:**
- **Observability (Key Metrics, Logs, Alerts):**
- **Incremental Rollout & Rollback Path:** (feature flag, dual-read, safe revert)
