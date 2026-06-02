---
name: coding-embedded
description: "Microcontroller, RTOS, and bare-metal development under tight memory and timing budgets. Triggers: MCU, RTOS, firmware, bare-metal, ISR, peripheral, DMA, FreeRTOS, Zephyr, RTIC, Cortex-M, ESP32, STM32, watchdog, WCET."
domain: coding
subdomain: embedded
facets:
  - lang:c
  - lang:cpp
  - lang:rust
  - target:mcu
  - target:rtos
applies_when:
  any_of:
    - "target is a microcontroller, SoC, or bare-metal environment"
    - "memory budget is constrained (typically < 1 MB RAM)"
    - "task involves ISRs, DMA, peripherals, or hardware timers"
    - "task involves an RTOS (FreeRTOS, Zephyr, RTIC, ThreadX, Mbed)"
    - "task targets safety-critical / functional-safety standards"
version: 0.1.0
---
# Coding / Embedded

## When to use

Open this skill when the code runs on a microcontroller or under a
real-time OS, or when the task interacts with hardware peripherals,
interrupts, or DMA. Typical targets: ARM Cortex-M (STM32, nRF52,
RP2040), ESP32, RISC-V MCUs, AVR. For Linux-based "embedded" systems
with full virtual memory, prefer the network or general coding canon.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **ISR (Interrupt Service Routine)** — code invoked by hardware. Must
  be short, allocation-free, and reentrancy-aware. On Cortex-M, ISRs
  preempt at NVIC priority levels.
- **Critical section** — code region where interrupts or task switches
  are disabled. Keep < 100 cycles; longer disables increase interrupt
  latency and break real-time guarantees.
- **Static allocation** — memory whose lifetime equals program
  lifetime. Strongly preferred over heap on MCUs to avoid
  fragmentation and bound worst-case memory.
- **WCET (Worst-Case Execution Time)** — upper bound on a code path's
  runtime. Required for hard-real-time guarantees. Tools: `bound-t`,
  `aiT`, `cargo-call-stack`.
- **Volatile** — compiler hint that a memory location can change
  outside normal program flow (peripheral registers, ISR-shared data
  in C). Required for any address-mapped peripheral and shared flag.
- **Memory barriers** (`DMB`, `DSB`, `ISB`) — enforce ordering across
  cores or between peripheral writes; needed when MMIO must be
  observed before/after data writes.
- **DMA coherence** — caches and DMA buffers must be flushed/
  invalidated. On Cortex-M7+ with caches, missed cache maintenance
  is the #1 cause of "intermittent" DMA bugs.
- **Stack vs heap** — MCU stacks are tiny (1–8 KB); recursion and
  large local arrays are bugs waiting to overflow into adjacent RAM.
- **Watchdog** — independent timer that resets the MCU if not
  "fed" within a deadline. Feed only from the main loop, never from
  a timer ISR (the latter masks hangs).
- **Tickless idle** — RTOS feature that suppresses periodic ticks
  while idle to save power; required for sub-mA average current.
- **Linker script / memory map** — defines flash, RAM, stack, heap
  regions. Misconfigured maps cause silent overlap and corruption.

For domain-wide canon see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **No heap on the hot path.** Reserve `malloc`/`new` for one-time
   setup; never inside ISRs or RT tasks. Prefer pool allocators
   (FreeRTOS heap_4 with single allocation phase, Rust `heapless`).
2. **Bounded everything.** Buffers, retries, loops — every limit is
   explicit, sized at compile time, and asserted in tests.
3. **Lock-free SPSC ring buffers** for ISR ↔ task communication.
   FreeRTOS stream/message buffers, `heapless::spsc::Queue`,
   ETL `etl::queue_spsc_atomic`.
4. **Peripheral access via typed register abstractions** —
   `svd2rust`-generated PACs, CMSIS-Driver, or Zephyr device API.
   Avoid raw pointer casts; mistakes are silent and hardware-fatal.
5. **Watchdog from day one.** Feed only from the main loop. Add an
   independent watchdog (IWDG on STM32) for catastrophic faults.
6. **Separate hardware-abstraction layer (HAL) from application
   logic.** Application is unit-testable on host with a mock HAL;
   hardware tests run on a Renode/QEMU model or real board in HIL.
7. **Power budgets are first-class.** Annotate each task with its
   peak/average current; review when a task changes scheduling.
8. **Use `-Wall -Wextra -Werror` and language subsets.** MISRA C
   2012 / CERT C for safety-critical; Rust `#![no_std]` + `clippy`
   for memory safety with C-equivalent footprint.
9. **Linker-defined symbols for ROM/RAM regions** — never hard-code
   addresses in C; use `extern char __stack_top;`-style symbols.
10. **Boot-time self-test.** RAM pattern test, flash CRC, peripheral
    presence; fail fast and visible (LED blink code, UART message).

## Pitfalls (subdomain-specific)

- ❌ **Calling `printf` inside an ISR.** Often blocks on a UART, which
  can deadlock. Use a lock-free log queue drained by a low-priority
  task.
- ❌ **Sharing data with an ISR via a non-`volatile` variable.** The
  compiler may cache it in a register; use `volatile` (C) or
  `core::sync::atomic` (Rust) and an explicit memory barrier.
- ❌ **Floating-point in ISRs without saving FPU context.** On
  Cortex-M with lazy stacking, the FPU context isn't pushed unless
  the FPU is touched; mixing FPU and non-FPU ISRs corrupts state.
- ❌ **`delay_ms()` on a cooperative scheduler.** Starves other tasks;
  use timers, async, or RTOS sleep primitives.
- ❌ **Stack overflow from recursion or large local arrays.** Static-
  analyse stack usage; reserve a guard region with a known pattern.
- ❌ **Assuming initialisation order across translation units.** C++
  static initialisers in a `.cpp` may run before `main()` but in
  unspecified order; use explicit init functions.
- ❌ **DMA from a buffer not aligned to cache-line size.** On
  Cortex-M7, partial cache invalidation corrupts neighbours.
- ❌ **Sharing a peripheral register across cores without atomics.**
  Read-modify-write is not atomic on most ARM cores; use bit-band or
  a critical section.
- ❌ **Ignoring brown-out and POR/external-reset paths.** A reset
  during flash write can leave a corrupt boot image; design dual-bank
  / A/B update.
- ❌ **Toolchain assumed to round consistently.** GCC and IAR diverge
  on `INT_MAX`+1 corner cases; pin the compiler version in CI.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Confirm the toolchain and target** — MCU family, core, FPU
   presence, RTOS or bare-metal, debug probe (J-Link/CMSIS-DAP).
   Pin compiler and HAL versions.
2. **Identify the change scope** — ISR, high-priority task, DMA
   path, or background code. Constraints differ.
3. **Estimate stack, heap, and flash impact** *before* writing code:
   `arm-none-eabi-size`, `cargo bloat`, `puncover`. Reject changes
   that exceed budget.
4. **Author against the typed peripheral API** (HAL/PAC). Treat raw
   register pokes as a smell.
5. **Prefer compile-time configuration** (`const`, generics, Kconfig,
   `feature`) over runtime flags; it shrinks code and surfaces bugs
   at compile time.
6. **Test on host** where the HAL is mocked; run hardware-in-the-loop
   tests for timing-sensitive paths. Renode and QEMU cover most
   Cortex-M targets without a board.
7. **Validate timing** with cycle counters (DWT on Cortex-M), GPIO
   pulses + logic analyser, or an RTOS-aware tracer (Tracealyzer,
   SystemView).
8. **Power profile** with a current monitor (PPK2, Otii Arc) for any
   battery-powered build.

## Validation

After completing the procedure, run:

```sh
# Static checks
clang-format --dry-run --Werror src/         # C/C++ formatting
clang-tidy src/*.c -- -Iinclude              # plus MISRA addons if applicable
cargo clippy --target thumbv7em-none-eabihf -- -D warnings   # Rust

# Build & footprint
make -j flash      # or: cargo build --release --target thumbv7em-none-eabihf
arm-none-eabi-size build/firmware.elf      # vs documented budget
puncover --elf build/firmware.elf           # per-symbol breakdown

# Tests
make test                                  # host unit tests with HAL mocks
qemu-system-arm -M netduino2 -kernel build/firmware.elf -nographic   # smoke

# Hardware-in-the-loop (when board present)
pyocd flash -t stm32l476 build/firmware.elf
pytest tests/hil/ -v                        # exercises the live board

# Stack & WCET
cargo call-stack --target thumbv7em-none-eabihf
bound-t --target arm build/firmware.elf
```

## See also

- [`../_shared/canon.md`](../_shared/canon.md)
- [`../network/SKILL.md`](../network/SKILL.md) — for embedded
  networking stacks (lwIP, Zephyr net, Embassy).
- MISRA C:2012, CERT C — safety-critical guidelines.
- ARM Architecture Reference Manual — barriers, NVIC, FPU lazy
  stacking.
- Zephyr / FreeRTOS / RTIC documentation.
