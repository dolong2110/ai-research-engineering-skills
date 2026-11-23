---
name: api-and-database-engineering
description: >-
  Design, implement, and optimize production APIs (REST, gRPC/Protobuf, SSE/WebSocket)
  and database layers (SQL schema design, composite indexing, EXPLAIN query plans,
  N+1 elimination, ACID transactions, and zero-downtime migrations). Use this skill
  when building backend endpoints, defining wire schemas, writing queries, or
  evolving schemas safely.
---

# API & Database Engineering

## 1. API Design & Evolution Standards

1. **Explicit, Validated Schemas at Boundaries**:
   - Validate request bodies, query params, and headers strictly at entrypoints (Pydantic / JSON Schema / Protobuf); reject unknown or out-of-range inputs with HTTP `400`/`422` and field-level details.
2. **Consistent Error Envelopes**:
   - Return structured machine-readable errors (`{"error": {"code": "RATE_LIMITED", "message": "...", "request_id": "..."}}`), never raw stack traces or HTML error pages.
3. **Pagination & Filtering at Scale**:
   - Prefer **keyset / cursor pagination** (`WHERE (created_at, id) < (:cursor_ts, :cursor_id) ORDER BY created_at DESC, id DESC LIMIT :n`) over `OFFSET 100000` (which scans and discards 100k rows!). Always enforce a server-side `max_page_size`.
4. **Idempotent Mutations & Concurrency Control**:
   - Accept `Idempotency-Key` headers on `POST`/payment/job-trigger endpoints; use `ETag` / `If-Match` or `version` columns for optimistic concurrency on updates.
5. **Backward-Compatible Evolution**:
   - Add optional fields with sensible defaults; never rename, delete, or change the type/semantics of an existing response or Protobuf wire field without a versioned deprecation cycle.

## 2. Database Schema, Indexing & Query Discipline

1. **Composite Index Ordering (Left-Prefix Rule)**:
   - Order multi-column B-tree index columns as `(equality_filters..., sort_order_cols..., range_filter)` and include hot projection columns (`INCLUDE (...)`) for index-only scans when appropriate.
2. **Eliminate $N+1$ Queries**:
   - Never execute a SQL/RPC lookup inside a loop over parent rows—batch via `WHERE id = ANY(:ids)` / `JOIN` / DataLoader batching.
3. **Verify Plans with `EXPLAIN (ANALYZE, BUFFERS)`**:
   - Confirm sequential scans (`Seq Scan`), disk spills (`external merge Disk`), and row-estimate mismatches on production-scale cardinalities.
4. **Transactions & Lock Safety**:
   - Keep transactions short—**never make external HTTP/LLM calls while holding an open DB transaction or row lock!** Acquire `SELECT ... FOR UPDATE` locks in deterministic primary-key order to prevent deadlocks.
5. **Zero-Downtime Migrations (Expand -> Migrate -> Contract)**:
   - Never run single-step breaking `ALTER TABLE RENAME COLUMN` or blocking `ADD COLUMN ... NOT NULL` rewrites on live tables while old app instances are still serving traffic:
     1. *Expand*: Add nullable column / new index concurrently (`CREATE INDEX CONCURRENTLY`).
     2. *Dual-Write & Backfill*: Deploy code writing both old + new columns; backfill historical rows in small batched chunks.
     3. *Switch Reads & Contract*: Cut reads over, verify zero old reads, then drop legacy column in a later deploy.
