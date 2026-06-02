---
name: coding-observability
description: "Logs, metrics, traces, and continuous profiling — OpenTelemetry, Prometheus, structured logs, RED/USE methodology, SLOs. Triggers: observability, OpenTelemetry, OTel, tracing, metrics, structured logs, Prometheus, Grafana, SLO, SLI, RED, USE."
domain: coding
subdomain: observability
facets:
  - lang:python
  - lang:typescript
  - lang:go
  - lang:rust
  - target:network
applies_when:
  any_of:
    - "task adds or improves logs, metrics, traces, or profiling for a service"
    - "task instruments code with OpenTelemetry / Prometheus / OpenMetrics"
    - "task defines SLIs / SLOs / error budgets"
    - "task investigates a production incident and needs better signals to reproduce"
version: 0.1.0
---
# Coding / Observability

## When to use

Open this skill when the change introduces or improves the *signals*
a running system produces — logs, metrics, traces, profiles — or when
the deliverable is an SLO, dashboard, or alert. For client-side RUM
and frontend telemetry, the same patterns apply but with browser
SDKs.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **The three pillars**:
  - *Logs* — append-only event records; high-cardinality friendly
    but expensive at scale.
  - *Metrics* — pre-aggregated time series; cheap to query, low
    cardinality.
  - *Traces* — causally-linked spans across services; show *where*
    latency lives.
- **OpenTelemetry (OTel)** — vendor-neutral SDK + protocol (OTLP).
  Standard for instrumentation across languages; ship to any
  backend (Jaeger, Tempo, Datadog, Honeycomb, Lightstep).
- **W3C `traceparent`** — header that propagates trace context
  across services. Always forward; never originate without
  context.
- **RED method** (services) — Rate, Errors, Duration. The minimum
  per-endpoint metric set.
- **USE method** (resources) — Utilisation, Saturation, Errors.
  For CPU, memory, disk, queues.
- **Cardinality** — distinct label/attribute combinations. The
  silent killer of Prometheus / metric backends. `user_id` as a
  label is almost always wrong.
- **SLI / SLO / error budget** — Indicator (measurement),
  Objective (target, e.g. 99.9 % over 30 days), budget
  (`(1 - SLO) × window`). Burn-rate alerts beat threshold alerts.
- **Structured logs** — key-value JSON; greppable AND queryable.
  Free-form prose belongs in `message`, never in field values.
- **Sampling** — head-based (decide at root) vs tail-based (decide
  after the trace completes). Tail-based catches errors better;
  costs more.
- **Continuous profiling** — eBPF-based always-on profilers
  (Pyroscope, Parca, Datadog) tag samples with the live trace.
- **Observability vs monitoring** — monitoring = pre-defined
  questions (alerts on known failure modes); observability =
  ability to ask new questions of an unknown failure.

## Recommended patterns

1. **Instrument once, at the boundary.** Use OpenTelemetry SDKs +
   auto-instrumentation libraries; manual spans only inside
   business logic worth measuring.
2. **Propagate context everywhere.** Forward `traceparent`
   (and `baggage`) through every hop, including async queues.
3. **Structured logs with a fixed schema.** Stable field names:
   `severity`, `message`, `trace_id`, `span_id`, `service`,
   `error.kind`. JSON output; one event per line.
4. **Low-cardinality metrics, high-cardinality logs/traces.** A
   metric with `request_id` is a logging system in disguise.
5. **RED per endpoint, USE per resource.** Bake into the service
   template so it's automatic.
6. **One trace per request, root in the entry point.** Span names
   describe operations (`HTTP GET /users/:id`), not data.
7. **Define SLIs as ratios.** `good_events / total_events` over a
   window; aggregate with `sum` and `rate`, not `avg` of averages.
8. **Burn-rate multi-window alerts.** Alert on "consuming the
   monthly budget in 1 hour" (fast burn) and "in 6 days" (slow
   burn) — much fewer false pages than threshold alerts.
9. **Logs without PII**, or with a redaction filter at the SDK
   layer. Never assume downstream pipelines redact.
10. **Exemplars on histograms** — link metric percentile spikes
    to the exact trace that caused them.
11. **Continuous profiling on by default** in non-prod; sampled
    in prod; tagged with `service.version` so deploys diff.
12. **Treat dashboards as code.** Commit Grafana JSON or
    Terraform-managed dashboards next to the service.

## Pitfalls (subdomain-specific)

- ❌ **`user_id` as a metric label.** Cardinality explosion; backend
  starts dropping series silently.
- ❌ **Free-form log messages with embedded variables.**
  `f"user {id} did {action}"` defeats structured search; use
  `log.info("action", user_id=id, action=action)`.
- ❌ **Logging in tight loops at INFO.** Disk bandwidth and
  ingestion cost dominate.
- ❌ **Traces without errors marked.** Span `status_code=ERROR`
  must be set for failed operations; otherwise tail-sampling
  skips them.
- ❌ **Sampling on the client without sending the decision.**
  Inconsistent sampling fragments traces; use OTel's
  `traceparent` flags.
- ❌ **Counting requests after the load balancer rewrites paths.**
  `/users/:id` becomes `/users/123`; cardinality explodes.
- ❌ **Average latency in dashboards.** Means hide tails; chart
  p50/p95/p99.
- ❌ **Single-replica Prometheus with no remote-write.** Restart
  loses metrics; use HA pair or Mimir / Thanos / Grafana Cloud.
- ❌ **Alerting on raw error rate.** A flap from 0.0001 to 0.001
  is 10× higher *and* meaningless; alert on burn rate.
- ❌ **Blocking calls inside the OTel exporter.** Use the batched
  span processor; never the simple one in production.
- ❌ **Mixing time zones.** All timestamps RFC 3339 UTC; never
  rely on the host's TZ.
- ❌ **Dashboards that no one owns.** Each dashboard needs a
  documented owner and a kill date if untouched > 90 days.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Define the SLIs / SLOs first.** What does "the service is
   healthy" mean as a query? Write the SLI math; pick a window.
2. **Adopt OpenTelemetry.** Install the SDK, enable auto-
   instrumentation for the framework, set `service.name` and
   `service.version` resource attributes.
3. **Forward `traceparent`** through every IO boundary, including
   message queues (use OTel's instrumentation libraries; don't
   roll your own).
4. **Emit structured logs** with `trace_id` / `span_id`
   correlation; pick a single logging library.
5. **Add RED metrics** per endpoint and USE metrics per resource;
   prefer auto-instrumentation libraries over hand-rolled
   counters.
6. **Build dashboards** for service health and per-endpoint
   latency. Commit the JSON.
7. **Define burn-rate alerts** for SLOs with multi-window logic.
   Alert on user-facing pain, not internal anomalies.
8. **Run a chaos / failure-mode drill** to verify the signals
   actually surface the problem you'd diagnose with them.

## Validation

After completing the procedure, run:

```sh
# Static checks
ruff check observability/
mypy --strict observability/

# Verify OTel pipeline locally
docker compose up -d otel-collector jaeger prometheus
pytest tests/observability/ -v          # asserts spans + metrics emitted

# SLO math test
python -m slo.validate --config slo.yaml --window 30d

# Cardinality budget check
prometheus-cardinality-exporter --max-series-per-metric 100000

# Dashboard syntax / lint
jsonnet -J vendor dashboards/*.libsonnet > /dev/null
grafana-tools dashboard validate dashboards/*.json
```

## See also

- [`../network/SKILL.md`](../network/SKILL.md) — for context
  propagation and per-call timeouts.
- [`../api-design/SKILL.md`](../api-design/SKILL.md) — for
  request-id and error envelope conventions.
- [`../databases/SKILL.md`](../databases/SKILL.md) — for tracing
  query plans and slow queries.
- OpenTelemetry specification — <https://opentelemetry.io/docs/specs/otel/>
- Google SRE Workbook — SLO/error-budget chapters.
- "Observability Engineering" (Majors, Fong-Jones, Miranda).
- Multi-window multi-burn-rate alerts (Google SRE).
