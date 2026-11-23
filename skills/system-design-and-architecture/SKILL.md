---
name: system-design-and-architecture
description: >-
  Architect clean, modular software systems and distributed backends: requirements
  & non-goals scoping, back-of-the-envelope capacity sizing, domain boundaries &
  SOLID/Hexagonal interfaces, caching, queuing, idempotency, fault tolerance, and
  Architecture Decision Records (ADRs / RFCs). Use this skill when designing new
  systems, planning major refactors, decomposing monoliths, or writing design docs.
---

# System Design & Software Architecture

Use this skill before writing large multi-module features, services, or refactors so boundaries, invariants, failure modes, and trade-offs are explicit upfront.

## 1. Architecture Design Sequence

1. **Clarify Functional Scope, Non-Goals & Constraints**:
   - Separate must-have v1 requirements from explicit **Non-Goals** (prevents scope creep and premature generalization).
   - Quantify scale & SLOs: read/write QPS, payload sizes, storage growth/year, latency targets (`p50` / `p99`), and consistency model (strong vs. bounded staleness / eventual).
2. **Design Clean Module Boundaries (Information Hiding)**:
   - **Deep Modules over Shallow Wrappers** (Ousterhout): The best modules expose a small, simple interface while hiding substantial implementation complexity (retries, caching, serialization, pooling).
   - **Dependency Direction**: Core domain logic depends on pure data structures and narrow protocol interfaces (`typing.Protocol` / interfaces)—never directly on HTTP clients, SDK wire formats, or storage drivers (Ports & Adapters).
   - **Make Illegal States Unrepresentable**: Encode invariants in types/enums/discriminated unions rather than scattering boolean flag combinations (`is_pending and not is_cancelled`).
3. **Distributed Reliability Primitives**:
   - **Idempotency**: Every retryable mutation or job worker accepts an `idempotency_key` and produces the exact same state transition if replayed.
   - **Timeouts + Bounded Retries + Jitter**: Never make an unbounded network/subprocess call; apply exponential backoff + jitter and **never retry non-transient 4xx errors**.
   - **Backpressure & Load Shedding**: Use bounded queues, token-bucket rate limiters, and bulkheads (separate worker pools per tenant/stage) so one slow dependency cannot exhaust process memory or threads.
   - **Caching Discipline**: Measure DB/compute need first; define explicit TTL, invalidation trigger, cache-aside vs. write-through semantics, and single-flight/jitter protection against cache stampedes.
4. **Document Trade-Offs Explicitly**:
   - Use [adr_and_rfc_template.md](./resources/adr_and_rfc_template.md) for non-trivial design choices—always compare at least 2 realistic alternatives (including the simplest baseline) before committing.
