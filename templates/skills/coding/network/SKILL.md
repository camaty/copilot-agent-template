---
name: coding-network
description: "Networked services, protocols, and IO-bound performance work — sockets, HTTP, gRPC, QUIC, WebSocket, message brokers. Triggers: socket, HTTP, gRPC, TCP, UDP, QUIC, WebSocket, latency, throughput, backpressure, congestion, protocol, broker, retry, idempotency."
domain: coding
subdomain: network
facets:
  - lang:rust
  - lang:go
  - lang:python
  - lang:typescript
  - target:linux
  - style:event-driven
applies_when:
  any_of:
    - "task involves a server, client, or protocol implementation"
    - "task mentions latency, throughput, backpressure, or congestion"
    - "task touches sockets, TLS, HTTP, gRPC, WebSocket, QUIC, or message brokers"
    - "task adds retries, timeouts, circuit breakers, or rate limiting to outbound calls"
version: 0.1.0
---
# Coding / Network

## When to use

Open this skill when the task is dominated by network IO, protocol
semantics, or wire-level performance: implementing a server, client,
or proxy; designing a protocol or message format; tuning latency or
throughput SLOs; or hardening a service against partial failures and
backpressure. For pure business logic that happens to call HTTP,
prefer the parent canon and skip this skill.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Backpressure** — propagating consumer slowness upstream so producers
  slow down rather than buffer unboundedly. Implemented as bounded
  queues, credit-based flow control (HTTP/2, gRPC, QUIC), or explicit
  `Accept: deferred` semantics.
- **Idempotency key** — a request-side token that lets a server safely
  deduplicate retried writes. Required for any non-GET retry loop.
- **Tail latency** (p95 / p99 / p99.9) — what the slowest few percent
  of users experience. Means and medians hide tails; always measure
  percentiles.
- **Half-open connection** — a TCP connection that one side considers
  closed (e.g. NAT timeout, kernel reboot) while the other still
  holds it. Detected via TCP keepalive or application-level pings.
- **HOL blocking** (head-of-line) — a stalled request blocks all
  others on the same connection (HTTP/1.1 pipeline, TCP-multiplexed
  streams). HTTP/3 over QUIC mitigates because each stream has its
  own loss recovery.
- **Bandwidth-Delay Product (BDP)** — `bandwidth × RTT`; the in-flight
  bytes a single TCP flow needs to saturate a link. Above ~50 ms RTT,
  default Linux receive windows are too small.
- **Cancellation propagation** — a cancelled request must release
  upstream resources (connection slots, server-side compute). Without
  it, slow clients cause resource exhaustion under load.
- **Exactly-once vs at-least-once** — exactly-once is impossible end
  to end without idempotent receivers; design for at-least-once
  delivery + idempotent handlers.
- **Backoff with jitter** — randomised delays between retries; without
  jitter, peers synchronise into retry storms after a partial outage.
- **TLS** session resumption (PSK / session tickets) — saves a round
  trip on reconnect; significant for tail latency in mobile clients.
- **Length-prefixed framing** vs delimited framing — length-prefixed
  is unambiguous and parseable in O(1) per frame; delimiters require
  escaping and complicate parsers.

For domain-wide canon see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Bounded queues at every async boundary.** Unbounded channels turn
   slowdowns into OOMs. Use `tokio::sync::mpsc::channel(N)`,
   `asyncio.Queue(maxsize=N)`, or equivalent.
2. **Timeouts at every IO call.** No call should be able to hang
   forever. Layer per-call (e.g. 5 s) under per-request (30 s) under
   client-global (60 s). Cancellation must cascade.
3. **Retry with jitter and a budget.** Exponential backoff alone
   causes synchronised storms; add full jitter (`sleep(rand(0, cap))`).
   Cap total retries per parent request, not per hop.
4. **Cancellation propagation.** Pass a cancellation token / context
   through every async call; on cancel, abort outbound IO and release
   semaphore slots before returning.
5. **Structured wire formats with explicit versioning** — Protobuf,
   Avro, Cap'n Proto. Reserve field tags; never reuse a deleted tag.
   Avoid ad-hoc JSON when schema evolution matters.
6. **Idempotent handlers for write paths.** Accept and store an
   `Idempotency-Key` header; return the prior response on replay.
7. **Connection pooling with a clear eviction policy.** Reuse keep-
   alive connections; evict on idle timeout, on per-host failure
   counts, and on TLS errors.
8. **Circuit breakers around unhealthy peers.** Track success rate
   over a sliding window; open the breaker when below threshold;
   half-open with limited probes before closing.
9. **Health and readiness as separate signals.** Liveness = "process
   responds"; readiness = "ready to take traffic". Failing readiness
   sheds load without restarting the process.
10. **Observability is part of the protocol.** Propagate `traceparent`
    (W3C) on every outbound; emit RED metrics (rate, errors,
    duration) per route.

## Pitfalls (subdomain-specific)

- ❌ **`SO_REUSEADDR` cargo-culting** without understanding TIME_WAIT
  semantics — can lead to stale connections receiving new data.
- ❌ **Reading until EOF on a half-closed peer.** Use length-prefixed
  framing or explicit terminators; EOF can mean "done" or "lost".
- ❌ **Logging payloads at INFO.** Leaks PII; bloats log storage; turns
  debug ergonomics into a compliance incident.
- ❌ **Treating DNS as static.** TTLs exist; long-lived clients must
  re-resolve. JVM clients are notorious for caching DNS forever.
- ❌ **Synchronous DNS lookup in an async runtime.** Blocks the
  executor thread; use the runtime's resolver (tokio's `lookup_host`,
  Go's pure-Go resolver).
- ❌ **One TCP connection per request when keep-alive is available.**
  TLS handshakes dominate latency; reuse aggressively.
- ❌ **Disabling TCP `Nagle` (`TCP_NODELAY`) without measuring.** Helps
  RPC, hurts bulk; benchmark on the workload before flipping.
- ❌ **Treating gRPC errors as HTTP status codes.** gRPC has its own
  status codes (`UNAVAILABLE`, `DEADLINE_EXCEEDED`, …); mapping is
  not 1:1 to HTTP.
- ❌ **`recvfrom` in a tight loop without `MSG_DONTWAIT`** — a slow
  packet stalls the worker; use non-blocking sockets + epoll/kqueue.
- ❌ **Letting clients control retry budgets.** Aggressive client
  retries plus aggressive server retries multiply load; cap at one
  layer.

## Procedure

1. **Define the SLOs first.** Write target p95/p99 latency, error
   rate, and throughput before designing. Without numbers, "fast
   enough" is unfalsifiable.
2. **Identify the protocol layer the change targets** (transport /
   application / message). Each has different testing strategies.
3. **Add or update wire-level tests first** — golden bytes for
   serialisation, property tests for parsers (round-trip, fuzz).
4. **Implement with timeouts, bounded buffers, and cancellation hooks
   from the start.** Retrofitting is harder than authoring correctly.
5. **Add structured logging and metrics** alongside the implementation;
   spans and counters at every IO boundary.
6. **Write a load test or benchmark** when the change has performance
   implications. Use `wrk`, `oha`, `vegeta`, `ghz` (gRPC), or `h2load`.
7. **Verify graceful shutdown** — in-flight requests complete,
   listeners stop accepting, drain timeout enforced, exit code
   reflects success.
8. **Chaos-test failure modes** — slow upstream, dropped TCP RSTs,
   DNS NXDOMAIN, partial network partitions. Tools: `toxiproxy`,
   `tc netem`.

## Validation

After completing the procedure, run:

```sh
# Lint / static checks (per language)
cargo clippy --all-targets --all-features -- -D warnings   # Rust
go vet ./... && staticcheck ./...                          # Go
ruff check . && mypy --strict src/                         # Python

# Build & unit tests
cargo test --all-features                                  # Rust
go test ./... -race                                        # Go (race detector!)
pytest -v --asyncio-mode=auto                              # Python

# Wire-level / protocol tests
# - golden-bytes round-trip
# - property tests on parsers (e.g. proptest, hypothesis, gopter)

# Load smoke test
wrk -t4 -c128 -d30s --latency http://localhost:8080/api
oha -z 30s -c 128 http://localhost:8080/api
ghz --insecure --total 10000 --concurrency 50 \
    --proto api.proto --call svc.Method localhost:50051

# Chaos: slow upstream
toxiproxy-cli toxic add upstream -t latency -a latency=500
```

## See also

- [`../spatial-transfer/SKILL.md`](../spatial-transfer/SKILL.md) — for
  high-throughput bulk transfer over UDP-based protocols.
- [`../mapreduce-codegen/SKILL.md`](../mapreduce-codegen/SKILL.md) —
  when the orchestrator talks to executors over HTTP/gRPC.
- [`../_shared/pitfalls.md`](../_shared/pitfalls.md)
- RFC 9110 (HTTP semantics), RFC 9000/9114 (QUIC, HTTP/3), RFC 6455
  (WebSocket).
- Google SRE Book — chapters on overload, cascading failures,
  load balancing.
