---
name: coding-spatial-transfer
description: "High-throughput transport of large 3D assets (splats, point clouds, training sets) using UDP-based protocols. Triggers: Aspera, FASP, UDT, QUIC, large file transfer, 3DGS, point cloud sync, multi-GB binary, dataset distribution."
domain: coding
subdomain: spatial-transfer
facets:
  - lang:python
  - target:linux
  - target:network
  - vendor:aspera
applies_when:
  any_of:
    - "task transfers large 3DGS scenes, point clouds, or ML training datasets between hosts"
    - "task uses UDP-based high-bandwidth transfer (Aspera FASP, UDT, QUIC, MTP) over high-RTT links"
    - "task builds a sync pipeline for multi-GB binary 3D assets with resume + integrity"
    - "task hits TCP throughput ceilings on cross-region transfers"
version: 0.1.0
---
# Coding / Spatial-Asset Transfer

## When to use

Open this skill when the artefacts to move are large (typically > 1 GB),
binary, and need to traverse high-RTT or lossy networks where TCP's
congestion control caps throughput far below link capacity. Common
inputs: 3DGS `.splat`/`.ply` scenes, lidar/photogrammetry point clouds
in `.las`/`.e57`, ML training tarballs, USD bundles with image
sidecars.

For small-payload REST/gRPC traffic, prefer the parent
[`../network/SKILL.md`](../network/SKILL.md). For browser uploads,
prefer resumable HTTP (tus, signed S3 multipart) — UDP-based protocols
rarely traverse browser sandboxes.

## Canon (must-know terms and invariants)

- **BDP (Bandwidth-Delay Product)** — `bandwidth × RTT`; the in-flight
  bytes a single TCP flow must keep on the wire to saturate a link.
  Above ~50 ms RTT, default TCP windows cannot reach line rate.
- **FASP (Fast Adaptive Secure Protocol)** — IBM Aspera's UDP-based
  protocol; rate-controlled rather than window-controlled, so RTT and
  packet loss do not throttle throughput. Requires a paid endpoint
  (HSTS, Faspex, or Aspera on Cloud).
- **UDT / QUIC / MTP** — open alternatives. QUIC (RFC 9000) is the
  modern default; UDT and Tsunami are research-grade. Aspera, IBM
  HSTS, and `ascp` tools dominate enterprise deployments.
- **Resume token** — a server-side record of the byte offset
  successfully received plus a content checksum prefix. A correct
  resume implementation re-validates the prefix before continuing.
- **Chunk integrity** — per-chunk MD5/SHA-256/BLAKE3 hashes carried in a
  manifest separate from the payload. End-to-end hash verification at
  the destination is required; transport-level CRCs are not enough.
- **Manifest** — the directory listing + per-file size + per-chunk
  hashes shipped before the payload. Without it, resume cannot detect
  corruption from a previous partial.
- **Egress cost** — cloud providers charge per-GB out. UDP-based
  transfer changes throughput, not billing; design the topology
  (regional cache, transfer-acceleration endpoint) to minimise
  cross-region egress.
- **MTU & fragmentation** — UDP-based protocols must avoid IP-layer
  fragmentation. Probe Path MTU (typically 1500 on Internet, 1450
  through tunnels, 9000 on dedicated WAN) and stay below it.

For domain-wide canon see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Always ship a manifest first.** Generate a JSON/Parquet manifest
   listing each file's size, per-chunk hashes, and a top-level Merkle
   root. The receiver verifies the root before declaring success.
2. **Chunk to a fixed power-of-two size.** 4 MiB or 16 MiB chunks
   balance retry granularity against header overhead. Avoid one chunk
   per file — a 5 MB file mixed with a 50 GB file in the same job
   stalls on the long tail.
3. **Cap concurrency by link, not by CPU.** A single FASP/QUIC flow
   already saturates 1–10 Gbps. Two or three concurrent jobs are
   plenty; dozens of parallel flows just cause loss and re-tx.
4. **Verify hashes after, not during.** Streaming hash on the wire is
   tempting but conflates network errors with disk errors. Compute
   hash from the destination filesystem after the write fsyncs.
5. **Always resume from manifest, never from "what we have".** A naive
   "send everything missing" loop misses partially written files.
   Resume must consult the manifest and the per-file write offset.
6. **Wrap the binary client; don't reimplement the protocol.** Use
   `ascp` (Aspera), `aws s3 cp` with TA endpoints, `rclone` with QUIC,
   or `aria2c`. Reimplementing UDP rate-control correctly is a
   multi-quarter project.
7. **Pin the client and protocol version in CI.** UDP-based protocols
   evolve; mismatched FASP versions silently fall back to lower rates
   or fail handshake under TLS upgrades.

## Pitfalls (subdomain-specific)

- ❌ **Sending one file per job.** Job-setup latency dominates for
  thousands of small splat tiles. Pack into a tar/zip before transfer.
- ❌ **No fsync between write and hash.** A crash between OS-cache
  write and disk write yields a hash mismatch on next resume; treat
  hashes as authoritative only after `fsync`.
- ❌ **Trusting `Content-Length` only.** A truncated transfer can match
  expected length if the manifest is wrong; always end-to-end hash.
- ❌ **Running ascp as root.** `ascp` honours destination filesystem
  permissions; run as the project's service user, not root.
- ❌ **Disabling TLS on the control channel.** Even when the data path
  is encrypted, the control handshake leaks file paths and tokens
  without TLS.
- ❌ **Forgetting to set `--policy fair` (Aspera) on shared links.**
  Default `fixed` rate ignores other tenants and gets you rate-limited
  upstream.
- ❌ **Hard-coding throughput targets.** Bandwidth-target should adapt
  to link probing, not be a constant; static 10 Gbps targets cause
  packet storms on commodity links.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Profile the link.**
   - Measure `iperf3 -t 30 -P 4` for TCP baseline and `iperf3 -u -b 0`
     for UDP capacity. Record RTT (`mtr`), loss %, and Path MTU.
   - If TCP already reaches > 70 % of link capacity, UDP-based
     protocols add little; stick with TCP + parallel streams.

2. **Build a manifest.**
   ```python
   # build_manifest.py — pseudo-Python
   for path in walk(src):
       size = os.path.getsize(path)
       chunks = [hash_chunk(path, off, CHUNK) for off in range(0, size, CHUNK)]
       manifest.append({"path": rel(path), "size": size, "chunks": chunks})
   merkle_root = merkle(manifest)
   write_json("manifest.json", {"root": merkle_root, "files": manifest})
   ```
   Ship `manifest.json` first via TLS HTTPS (small, integrity-critical).

3. **Choose & invoke the transport.**
   - Aspera (paid):
     ```sh
     ascp -P 33001 -l 5G -k 3 --policy fair \
          --file-manifest=text --file-checksum=sha256 \
          src/ user@host:/dest/
     ```
     `-k 3` enables full resume; `--policy fair` shares fairly with
     other flows.
   - QUIC / rclone (open):
     ```sh
     rclone --transfers=4 --multi-thread-streams=4 \
            --checksum --progress \
            sync src/ remote:bucket/
     ```
   - AWS S3 with Transfer Acceleration:
     ```sh
     aws s3 cp src/ s3://bucket/dest/ --recursive \
            --endpoint-url https://s3-accelerate.amazonaws.com
     ```

4. **Verify end-to-end.**
   - On destination: compute per-chunk hashes from the on-disk files,
     rebuild the Merkle root, compare with the manifest root.
   - If mismatched, the resume token is the offset of the first failing
     chunk; re-transfer from that point.

5. **Fan-out to consumers.**
   - Push the verified bundle to a regional cache (S3, Cloudflare R2,
     Backblaze B2). Workers pull from the cache, never from origin.
   - Record `(manifest_root, dataset_id, version)` in a registry so
     consumers reproduce a known good snapshot.

6. **Emit lane events** for traceability:
   `[SKILL:spatial-transfer][TRANSFER ok bytes=N rate=X mbps elapsed=Ts]`.

## Validation

After completing the procedure, run:

```sh
# Lint / static checks for the wrapper code
ruff check transfer/
mypy transfer/ --ignore-missing-imports

# Unit + integration tests (mock the transport client)
pytest tests/transfer/ -v

# End-to-end smoke test: small synthetic dataset, real transport
./scripts/transfer_smoke.sh

# Integrity check: rebuild Merkle root at destination
python -m transfer.verify --manifest manifest.json --root /data/dest

# Throughput regression: compare measured rate against link probe ±20 %
python -m transfer.benchmark --link-profile profiles/aws-eu-us.json
```

## See also

- [`../network/SKILL.md`](../network/SKILL.md) — for control-plane
  protocol design (resume tokens, manifests, registry APIs).
- [`../agent-sca/SKILL.md`](../agent-sca/SKILL.md) — security review
  of any auto-generated transfer scripts (credentials, command
  injection in `ascp` args).
- [`../../3dcg/3dgs/SKILL.md`](../../3dcg/3dgs/SKILL.md) — primary
  consumer of large `.splat` payloads.
- IBM Aspera FASP technical overview — <https://www.ibm.com/products/aspera>
- RFC 9000 (QUIC), RFC 9114 (HTTP/3) — for QUIC-based transfer paths.
- BBR congestion control — <https://research.google/pubs/pub45646/>
  (alternative when constrained to TCP).
