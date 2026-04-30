---
name: ml-training
description: "Model training, fine-tuning, dataset preparation, and evaluation. Triggers: train, fine-tune, dataset, dataloader, loss, optimizer, evaluation, experiment."
domain: ml
subdomain: training
facets:
  # - framework:pytorch
  # - framework:huggingface
  # - task:llm
  # - task:cv
  # - target:gpu
applies_when:
  any_of:
    - "task involves training a model from scratch or fine-tuning"
    - "task involves dataset construction, splits, or data augmentation"
    - "task involves loss design, optimizer choice, or hyperparameter search"
    - "task involves offline evaluation or experiment tracking"
version: 0.1.0
---
# Machine Learning / Training

## When to use

Open this skill when the deliverable is a trained or fine-tuned model artifact, an evaluation report, or a training pipeline. For taking an existing artifact into production, use [`../inference/SKILL.md`](../inference/SKILL.md).

## Canon

- **Train / val / test split** — fixed once, never tuned against the test set.
- **Leakage** — any signal in training that wouldn't be available at inference. Always assume it exists until proven otherwise.
- **Reproducibility** — pinned seeds, pinned dependencies, recorded data version, recorded code commit.
- **Class imbalance** — accuracy is misleading; prefer per-class metrics, PR-AUC, or balanced loss.
- **Evaluation harness** — code that computes metrics; must be the **same** for every experiment compared.

## Recommended patterns

1. **Lock the eval harness first.** No model change before metrics are reproducible on a baseline.
2. **One change per experiment.** Co-changing data + model + optimizer makes attribution impossible.
3. **Track every run** (Weights & Biases, MLflow, or filesystem-based) with config, metrics, code SHA, data hash.
4. **Cap epochs by validation early-stopping**, not wall-clock time.
5. **Save checkpoints with the tokenizer / preprocessor** bundled — the model alone is useless without them.
6. **Mixed precision (`bf16` on Ampere+ / `fp16` elsewhere)** for any non-trivial training run.
7. **Gradient accumulation** when memory limits batch size; effective batch size is what matters.

## Pitfalls

- ❌ **Tuning hyperparameters on the test set.** Reserve test for the final number, after model is frozen.
- ❌ **Data leakage via global normalization** computed on train+test combined.
- ❌ **Augmentation applied to the validation set.**
- ❌ **`.eval()` forgotten** during validation — dropout/batchnorm distort metrics.
- ❌ **Silent dtype upcasts.** `model.to(device)` may not move buffers; always check `.dtype`.
- ❌ **Comparing to a different baseline run** with a different eval harness or data version.
- ❌ **Distributed training without verifying loss curves match single-GPU** within tolerance.

## Procedure

1. Define the metric and freeze the eval harness; reproduce a published or prior baseline.
2. Version the dataset (hash files; document any filtering/sampling).
3. Write a deterministic data loader; verify with a fixed-seed run that batches are bit-identical.
4. Run a tiny end-to-end overfit on a handful of samples to confirm the loss can drive to ~0.
5. Scale to full training; track config, metrics, and the resulting checkpoint.
6. Report metrics with confidence intervals (multiple seeds when feasible).

## Validation

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
# ML-specific:
# - Re-run eval on the saved checkpoint; metrics must match the run log within tolerance.
# - For fine-tunes, compare against the base model on the same eval set.
```

## See also

- [`../inference/SKILL.md`](../inference/SKILL.md) — packaging and serving the resulting checkpoint
- Reproducibility checklists (e.g. NeurIPS, ML reproducibility checklist)
