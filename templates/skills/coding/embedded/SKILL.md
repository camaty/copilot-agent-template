---
name: coding-embedded
description: "Microcontroller, RTOS, and bare-metal development under tight memory and timing budgets. Triggers: MCU, RTOS, firmware, bare-metal, ISR, peripheral, DMA."
domain: coding
subdomain: embedded
facets:
  # - lang:c
  # - lang:cpp
  # - lang:rust
  # - target:mcu
  # - target:rtos
  # - vendor:arm
applies_when:
  any_of:
    - "target is a microcontroller, SoC, or bare-metal environment"
    - "memory budget is constrained (typically < 1 MB RAM)"
    - "task involves ISRs, DMA, peripherals, or hardware timers"
    - "task involves an RTOS (FreeRTOS, Zephyr, RTIC, etc.)"
version: 0.1.0
---
# Coding / Embedded

## When to use

Open this skill when the code runs on a microcontroller or under a real-time OS, or when the task interacts with hardware peripherals, interrupts, or DMA. For Linux-based "embedded" systems with full virtual memory, prefer the network or general coding canon.

## Canon

- **ISR (Interrupt Service Routine)** — code invoked by hardware. Must be short, allocation-free, and reentrancy-aware.
- **Critical section** — code region where interrupts or task switches are disabled.
- **Static allocation** — memory whose lifetime equals program lifetime; preferred over heap on MCUs.
- **WCET (Worst-Case Execution Time)** — upper bound on a code path's runtime; required for hard-real-time guarantees.
- **Volatile** — compiler hint that a memory location can change outside normal program flow (peripheral registers, ISR-shared data).

## Recommended patterns

1. **No heap on the hot path.** Reserve `malloc`/`new` for one-time setup, never inside ISRs or RT tasks.
2. **Bounded everything.** Buffers, retries, loops — every limit is explicit.
3. **Lock-free SPSC ring buffers** for ISR ↔ task communication.
4. **Peripheral access via typed register abstractions** (svd2rust, CMSIS-Driver). Avoid raw pointer casts.
5. **Watchdog from day one.** Feeds only from the main loop, never from a timer ISR.
6. **Separate hardware-abstraction layer (HAL) from application logic** so the latter can be unit-tested on host.

## Pitfalls

- ❌ **Calling `printf` inside an ISR.** Often blocks on a UART and can deadlock.
- ❌ **Sharing data with an ISR via a non-`volatile` variable.** The compiler may cache it in a register.
- ❌ **Floating point in ISRs without saving FPU context.**
- ❌ **`delay_ms()` on a cooperative scheduler.** Starves other tasks; use timers or async.
- ❌ **Stack overflow from recursion or large local arrays.** MCU stacks are typically 1–8 KB.
- ❌ **Assuming initialization order across translation units.** Use explicit init functions.

## Procedure

1. Confirm the toolchain and target (MCU family, core, FPU presence, RTOS or bare-metal).
2. Identify whether the change touches an ISR, a high-priority task, or background code — constraints differ.
3. Estimate stack and heap impact before writing code.
4. Prefer compile-time configuration (`const`, generics) over runtime flags.
5. Test on host where the HAL is mocked; run hardware-in-the-loop tests for timing-sensitive paths.

## Validation

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
# Optional firmware-specific:
# - size <binary>            # check flash/RAM footprint vs budget
# - static stack analyzer    # e.g. cargo-call-stack, bound-t
```

## See also

- [`../_shared/canon.md`](../_shared/canon.md)
- MISRA C / CERT C guidelines (for safety-critical contexts)
