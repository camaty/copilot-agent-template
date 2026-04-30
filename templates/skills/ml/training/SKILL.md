---
name: ml-training
description: "Model training, fine-tuning, dataset preparation, evaluation, and experiment tracking. Triggers: train, fine-tune, dataset, dataloader, loss, optimizer, evaluation, experiment, hyperparameter, mixed precision, distributed training, DDP, FSDP, DeepSpeed."
domain: ml
subdomain: training
facets:
  - lang:python
  - framework:pytorch
  - framework:huggingface
  - target:gpu
  - precision:bf16
applies_when:
  any_of:
    - "task involves training a model from scratch or fine-tuning"
    - "task involves dataset construction, splits, or data augmentation"
    - "task involves loss design, optimizer choice, or hyperparameter search"
    - "task involves offline evaluation or experiment tracking"
    - "task involves distributed training (DDP, FSDP, DeepSpeed, ZeRO)"
version: 0.1.0
---
# Machine Learning / Training

## When to use

Open this skill when the deliverable is a trained or fine-tuned model
artifact, an evaluation report, or a training pipeline. For taking an
existing artifact into production, use [`../inference/SKILL.md`](../inference/SKILL.md).
For LLM-specific PEFT (LoRA, QLoRA), see
[`../llm-finetuning/SKILL.md`](../llm-finetuning/SKILL.md). For
diffusion-specific training, see [`../diffusion/SKILL.md`](../diffusion/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Train / val / test split** — fixed once, never tuned against the
  test set. Split by group / time / user where leakage is possible
  (don't just shuffle).
- **Leakage** — any signal in training that wouldn't be available at
  inference. Always assume it exists until proven otherwise; common
  sources: future timestamps, target-leaking features, user-id
  shortcuts.
- **Reproducibility** — pinned seeds (`torch`, `numpy`, `random`,
  CUDA), pinned dependencies (`requirements.lock`, `uv.lock`),
  recorded data version (hash), recorded code commit.
- **Class imbalance** — accuracy is misleading; prefer per-class
  metrics, PR-AUC, balanced loss, or stratified sampling.
- **Evaluation harness** — code that computes metrics; must be the
  *same* for every experiment compared.
- **Mixed precision** — `bf16` on Ampere+ / Hopper / TPU, `fp16`
  elsewhere. `fp16` requires loss scaling; `bf16` does not.
- **Effective batch size** — `per_device_batch × n_devices ×
  grad_accum_steps`. What the optimiser actually sees; the only
  number that matters for hyperparameter transfer.
- **DDP / FSDP / DeepSpeed-ZeRO** — data-parallel (replicated weights),
  fully-sharded (sharded weights+grads+opt-state), and ZeRO-2/3
  (sharded various). Choose by model size vs HBM.
- **Gradient clipping** — `clip_grad_norm_(model.parameters(),
  max_norm)`; standard remedy for training instability.
- **EMA (exponential moving average)** of weights — used in
  diffusion, vision foundation models; saved alongside the live
  weights for inference.
- **LR schedule** — warmup → cosine / linear / step decay. Warmup is
  not optional for adaptive optimisers (Adam family) on transformer
  training.

## Recommended patterns

1. **Lock the eval harness first.** No model change before metrics
   are reproducible on a baseline. Eval is the unit of truth.
2. **One change per experiment.** Co-changing data + model +
   optimiser makes attribution impossible. Use a `--name` flag and
   commit-per-change discipline.
3. **Track every run** (Weights & Biases, MLflow, AIM, or filesystem-
   based) with config, metrics, code SHA, dataset hash, hardware,
   git diff (for uncommitted changes).
4. **Cap epochs by validation early-stopping**, not wall-clock time.
   Early-stop with patience; restore best checkpoint.
5. **Save checkpoints with the tokenizer / preprocessor bundled** —
   the model alone is useless without them. Save Hugging Face
   `save_pretrained()` style.
6. **Mixed precision (`bf16` preferred)** for any non-trivial
   training run; halves memory, doubles throughput, and on Ampere+
   has no numerical pitfalls.
7. **Gradient accumulation** when memory limits batch size; effective
   batch size is what matters for transfer of hyperparameters.
8. **Distributed: start with DDP**; reach for FSDP/ZeRO only when
   the model exceeds single-GPU memory. The complexity step-up is
   real.
9. **Scale LR with effective batch** — linear scaling for SGD,
   square-root for Adam-family heuristically; use μP / μTransfer
   for hyperparameter transfer across model sizes.
10. **Overfit a tiny subset first.** ~64 examples should drive train
    loss to ~0 within a few hundred steps. If not, the bug is
    upstream of training.
11. **Hyperparameter search** with low-fidelity stages (HyperBand,
    ASHA); never grid-search at full fidelity.

## Pitfalls (subdomain-specific)

- ❌ **Tuning hyperparameters on the test set.** Reserve test for the
  final number, after model is frozen.
- ❌ **Data leakage via global normalisation** computed on
  train+test combined. Always fit normalisers on train only.
- ❌ **Augmentation applied to the validation set.** Validation must
  reflect inference-time inputs.
- ❌ **`.eval()` forgotten** during validation — dropout/batchnorm
  distort metrics; gradient computation wastes memory.
- ❌ **Silent dtype upcasts.** `model.to(device)` may not move
  buffers; always check `.dtype` post-load. Custom layers without
  `.to()` are common offenders.
- ❌ **Comparing to a different baseline run** with a different
  eval harness or data version. Re-run the baseline under the
  current harness.
- ❌ **Distributed training without verifying loss curves match
  single-GPU** within tolerance — a sync bug can train a different
  model silently.
- ❌ **Logging at every step in DDP from all ranks.** Multiplies log
  volume by world size; log only from rank 0.
- ❌ **Saving optimizer state to a different path on each rank.**
  Resume requires sharded state to land in matching paths.
- ❌ **Hard-coding `cuda:0`.** Use `device = torch.device("cuda" if
  torch.cuda.is_available() else "cpu")`; pass via env in DDP.
- ❌ **Random crops / shuffles without a seed per worker.** The
  default `DataLoader` worker init seeds Python's `random` non-
  deterministically; set `worker_init_fn`.
- ❌ **Mixing `bf16` model with `fp32` master grads silently** —
  works on PyTorch but blows up on TPU; declare precision policy
  explicitly.

Domain-wide pitfalls (when present) live in `../_shared/pitfalls.md`.

## Procedure

1. **Define the metric and freeze the eval harness**; reproduce a
   published or prior baseline on it.
2. **Version the dataset** (hash files; document any filtering /
   sampling). Commit the recipe, not the data.
3. **Write a deterministic data loader**; verify with a fixed-seed
   run that batches are bit-identical across runs.
4. **Run a tiny end-to-end overfit** on a handful of samples to
   confirm the loss can drive to ~0. Catches model-build bugs
   cheaply.
5. **Scale to a small representative run** (1–10 % of data) to
   confirm loss curve shape; adjust LR, schedule, and batch size.
6. **Scale to full training**; track config, metrics, and the
   resulting checkpoint.
7. **Report metrics with confidence intervals** (multiple seeds when
   feasible; ≥ 3 seeds for any claim).
8. **Hyperparameter search** with HyperBand/ASHA on a low-fidelity
   proxy; promote top configs to full training.
9. **Distributed training**: run a DDP smoke test (2 GPUs, 100
   steps) and assert single-GPU and DDP loss agree within 1 %.

## Validation

After completing the procedure, run:

```sh
# Static checks
ruff check src/ tests/
mypy --strict src/

# Reproducibility test: two runs with same seed produce identical
# train loss curves
pytest tests/test_repro.py -v

# Tiny overfit smoke test (must reach loss < 1e-3 in 200 steps)
python -m train.run --config configs/overfit_smoke.yaml \
    --max-steps 200 --assert-final-loss-below 1e-3

# Distributed parity (when training distributed)
torchrun --nproc-per-node=2 -m train.run \
    --config configs/ddp_smoke.yaml --max-steps 100
python -m tests.compare_logs single.log ddp.log --tol 0.01

# Re-run eval on the saved checkpoint; metrics must match the run
# log within tolerance
python -m eval.run --ckpt ckpts/best.pt --tol 1e-4

# For fine-tunes, compare against the base model on the same eval
python -m eval.run --ckpt base/ --output base_eval.json
python -m eval.run --ckpt ft/ --output ft_eval.json
python -m tools.compare_eval base_eval.json ft_eval.json
```

## Validation gates (PR-ready criteria)

- All `tests/` pass; tiny-overfit reaches threshold.
- Eval metric on val set ≥ documented baseline (or improvement
  recorded with seed-CI).
- Run config, metrics, checkpoint, dataset hash, and code SHA all
  logged in the experiment tracker.

## See also

- [`../inference/SKILL.md`](../inference/SKILL.md) — packaging and
  serving the resulting checkpoint.
- [`../llm-finetuning/SKILL.md`](../llm-finetuning/SKILL.md) — LLM-
  specific PEFT (LoRA, QLoRA), DPO, instruction tuning.
- [`../diffusion/SKILL.md`](../diffusion/SKILL.md) — diffusion-
  specific schedulers, EMA, classifier-free guidance.
- [`../motion-fm/SKILL.md`](../motion-fm/SKILL.md) — when training
  motion foundation models.
- ML reproducibility checklist (NeurIPS / ICML).
- μP / μTransfer paper — hyperparameter transfer across scales.
- DeepSpeed / FSDP / Accelerate documentation.
