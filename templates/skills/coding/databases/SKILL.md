---
name: coding-databases
description: "Relational, document, and vector data stores: schema design, migrations, transactions, indexing, isolation, query plans. Triggers: SQL, Postgres, MySQL, SQLite, MongoDB, Redis, vector DB, pgvector, migration, transaction, isolation, query plan, EXPLAIN, ORM."
domain: coding
subdomain: databases
facets:
  - lang:python
  - lang:typescript
  - lang:go
  - target:linux
applies_when:
  any_of:
    - "task designs or migrates a database schema (relational, document, or vector)"
    - "task tunes a slow query, an index, or a transaction"
    - "task adds caching, replication, or sharding to a data tier"
    - "task integrates a vector store (pgvector, Qdrant, Pinecone) for retrieval"
version: 0.1.0
---
# Coding / Databases

## When to use

Open this skill when the change touches a data store: schema, query,
index, migration, transaction boundary, ORM, replica topology, or
backup. For pure cache layers (Redis as a key-value with no
durability requirements), the network skill may be enough.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Isolation levels** — `READ UNCOMMITTED`, `READ COMMITTED`,
  `REPEATABLE READ`, `SERIALIZABLE`. Postgres default is `READ
  COMMITTED`; MySQL InnoDB default is `REPEATABLE READ`. Each level
  permits different anomalies (dirty read, non-repeatable read,
  phantom read).
- **MVCC** (Postgres, Oracle, SQL Server, MySQL InnoDB) — readers
  don't block writers and vice versa via row-level versioning;
  `VACUUM` reclaims dead tuples in Postgres.
- **Indexes** — B-tree (default), hash, GIN (inverted, `jsonb` /
  arrays), GiST (geometric / range), BRIN (large append-only),
  partial, expression. Each accelerates a different shape of
  predicate.
- **Query plan** — `EXPLAIN ANALYZE` output; sequential scan vs
  index scan vs index-only scan vs bitmap heap scan. The plan
  shape — not the millisecond — is the unit of optimisation.
- **Transactions** — atomic, consistent, isolated, durable.
  Long-running transactions hold locks and bloat MVCC tables; keep
  them short.
- **Migrations** — versioned, ordered schema changes (Alembic,
  Flyway, Liquibase, Knex, Prisma Migrate). Always reversible and
  always tested on a copy of production.
- **Online vs offline migrations** — online = no exclusive lock
  (e.g. Postgres `CREATE INDEX CONCURRENTLY`, `ALTER TABLE … ADD
  COLUMN` with no default); offline = locks the table.
- **N+1 query** — fetching a list and then issuing one query per
  item; the most common ORM perf bug.
- **Connection pool** — finite resource; over-provisioning the pool
  exhausts the database. PgBouncer (transaction or session mode)
  is standard for Postgres.
- **Read replica** — async replica for scale-out reads;
  replication lag must be observable and accommodated by the app.
- **Vector index** — IVF, HNSW, ScaNN; trade recall vs latency.
  Pgvector supports HNSW and IVFFlat; tune `m`, `ef_search`, and
  list count.
- **Document model joins** — embedding vs referencing; embed when
  read together always, reference when independent lifecycle.
- **CAP / PACELC** — partition tolerance is non-optional in
  distributed DBs; consistency vs availability is the real tradeoff
  and depends on configuration (Mongo `writeConcern`, Cassandra
  `quorum`).

## Recommended patterns

1. **Author migrations as code, version-controlled, reversible.**
   Test forward and backward on a production-shape dataset before
   shipping.
2. **Online schema changes only.** Never `ALTER TABLE ADD COLUMN
   NOT NULL DEFAULT …` on a busy table; do nullable + backfill +
   constraint.
3. **Indexes follow queries, not schemas.** Add an index because
   `EXPLAIN ANALYZE` of a real query asked for one; remove unused
   indexes (`pg_stat_user_indexes`).
4. **Short transactions.** Acquire late, release early. No network
   IO inside a transaction other than to the DB itself.
5. **Use the pool, not the raw driver.** Tune pool size to
   `max_connections / replicas`; cap per-process at a safe
   fraction.
6. **Read-your-writes via primary** for the user who just wrote;
   tolerate replica lag elsewhere.
7. **Idempotent application code** for retries; the DB is one of
   many systems that may retry.
8. **Encrypt at rest and in transit** by default; rotate
   credentials via secret managers.
9. **Backups are tested by restore, not by the absence of errors.**
   Quarterly restore drills.
10. **For document stores, model around access patterns.** Don't
    map an OLTP relational model into Mongo verbatim.
11. **For vector stores, profile recall vs latency.** Tune index
    parameters on a labelled probe set; pgvector HNSW with
    `m=16, ef_search=64` is a sane default.
12. **Connection-pool at L4 (PgBouncer) for Postgres** when many
    short-lived processes connect (Lambdas, serverless).

## Pitfalls (subdomain-specific)

- ❌ **Schema-less is not free.** A document DB without a written
  schema becomes a dialect every team member invents differently.
  Use JSON Schema validation server-side.
- ❌ **`SELECT *` in application queries.** Adds I/O cost; breaks
  on column rename/add.
- ❌ **Implicit `NULL` semantics.** `WHERE x = NULL` is never true;
  use `IS NULL`. `NOT IN (subquery)` returns wrong results when
  the subquery yields a `NULL`.
- ❌ **ORM lazy loading inside a loop.** N+1; fix with eager
  load / `select_related` / DataLoader.
- ❌ **Long-running transaction during a deploy.** Holds locks;
  blocks `ALTER TABLE` migrations indefinitely.
- ❌ **`COUNT(*)` of huge tables on each request.** O(N); cache
  approximate counts (`pg_class.reltuples`, materialised views).
- ❌ **Storing money in `float`.** Use `numeric(p, s)` /
  `DECIMAL`; floats round wrong on cents.
- ❌ **JSON columns without indexes.** Postgres `jsonb` + GIN is
  great; raw `text` JSON is a full-table scan.
- ❌ **Cross-database transactions.** No two-phase commit by
  default; choose one source of truth or a saga.
- ❌ **Trusting `ORDER BY id` for pagination across writes.**
  Concurrent inserts skip rows; use cursor pagination.
- ❌ **Vector-store recall regressions silently shipped.** Always
  evaluate recall@k on a held-out probe set after index changes.
- ❌ **Dropping a unique constraint to "fix" a migration.** Almost
  always the wrong fix; surface the duplicate first.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Identify the workload shape.** OLTP (many small txns) vs OLAP
   (few large) vs mixed; reads vs writes; cardinality. The shape
   drives every other decision.
2. **Design the schema for the queries** you can name. ER diagram
   for relational, access-pattern table for document/key-value.
3. **Author migrations** with the migration tool of choice;
   include `up` and `down`; test on a clone.
4. **Write the queries** alongside the schema; capture
   `EXPLAIN ANALYZE` for each in `docs/queries.md`.
5. **Add indexes only after queries exist.** One index per query
   shape, prefixed by the most-selective columns.
6. **Set transaction boundaries explicitly.** No "framework
   default" magic; document why each begins and ends where it
   does.
7. **Configure the connection pool** based on capacity-plan math;
   add a backpressure mechanism upstream.
8. **Add observability** — slow-query log, per-query histograms
   tagged with `query_id`, replication lag metric, pool
   saturation.
9. **Plan for restore.** Backup format, retention, encryption,
   restore RTO/RPO. Run a restore drill.

## Validation

After completing the procedure, run:

```sh
# Static checks for migrations and queries
sqlfluff lint migrations/ --dialect postgres
ruff check . && mypy --strict src/
prisma format && prisma validate                 # if Prisma

# Run migrations forward and backward against a clone
make db-clone-from-prod
alembic upgrade head && alembic downgrade -1 && alembic upgrade head

# Query plan regressions (golden EXPLAIN output per query)
psql -f tests/queries/explain_all.sql > current.plan
diff -u tests/queries/golden.plan current.plan

# Index hygiene
psql -c "SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;"

# Vector recall (when applicable)
python -m vector.eval --probe probes/recall_v3.jsonl --min-recall 0.95

# Backup restore drill
make backup-then-restore && make data-checksum-equal
```

## See also

- [`../api-design/SKILL.md`](../api-design/SKILL.md) — keep the
  public schema decoupled from the DB schema.
- [`../observability/SKILL.md`](../observability/SKILL.md) — for
  query tracing and slow-query alerts.
- [`../network/SKILL.md`](../network/SKILL.md) — for connection
  pooling and timeout discipline.
- Postgres docs (especially `EXPLAIN`, `MVCC`, `VACUUM`).
- "Designing Data-Intensive Applications" (Martin Kleppmann).
- pgvector — <https://github.com/pgvector/pgvector>
- "The Many Faces of Consistency" (Bailis et al.).
