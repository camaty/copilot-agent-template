---
name: coding-network
description: "Networked services, protocols, and IO-bound performance work. Triggers: socket, HTTP, gRPC, TCP, UDP, latency, throughput, protocol."
domain: coding
subdomain: network
facets:
  # Fill in per-task; remove unused.
  # - lang:rust
  # - lang:go
  # - target:linux
applies_when:
  any_of:
    - "task involves a server, client, or protocol implementation"
    - "task mentions latency, throughput, backpressure, or congestion"
    - "task touches sockets, TLS, HTTP, gRPC, WebSocket, QUIC, or message brokers"
version: 0.1.0
---
# Coding / Network

## When to use

Open this skill when the task is dominated by network IO, protocol semantics, or wire-level performance. For pure business logic that happens to make HTTP calls, prefer the parent domain canon and skip this skill.

## Canon

- **Backpressure** — propagating consumer slowness upstream so producers slow down rather than buffer unboundedly.
- **Idempotency key** — a request-side token allowing safe retries without duplicate side effects.
- **Tail latency** — p99 / p99.9 of response time; mean is misleading for user experience.
- **Half-open connection** — a TCP connection that one side considers closed while the other still holds it.

For domain-wide canon see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Bounded queues at every async boundary.** Unbounded channels turn slowdowns into OOMs.
2. **Timeouts at every IO call.** No call should be able to hang forever.
3. **Retry with jitter and a budget.** Exponential backoff alone causes synchronized retry storms.
4. **Cancellation propagation.** A cancelled request must release upstream resources.
5. **Structured wire formats with explicit versioning** (Protobuf, Avro). Avoid ad-hoc JSON when schema evolution matters.

## Pitfalls

- ❌ **`SO_REUSEADDR` cargo-culting** without understanding TIME_WAIT semantics.
- ❌ **Reading until EOF on a half-closed peer.** Use length-prefixed framing or explicit terminators.
- ❌ **Logging payloads at INFO.** Leaks PII; bloats logs.
- ❌ **Treating DNS as static.** TTLs exist; long-lived clients must re-resolve.
- ❌ **Synchronous DNS lookup in an async runtime.** Blocks the executor.

## Procedure

1. Identify the protocol layer the change targets (transport / application / message).
2. Add or update wire-level tests **first** (golden bytes, property tests for parsers).
3. Implement with timeouts, bounded buffers, and cancellation hooks from the start.
4. Add a load test or benchmark when the change has performance implications.
5. Verify graceful shutdown: in-flight requests complete, listeners stop accepting.

## Validation

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
# Optional: a load smoke test, e.g. `wrk -t2 -c50 -d10s http://localhost:8080/`
```

## See also

- [`../_shared/pitfalls.md`](../_shared/pitfalls.md)
- RFC 9110 (HTTP semantics), RFC 9000 (QUIC) for protocol grounding.
