---
domain: ml
version: 0.1.0
---
# Machine Learning — Domain Index

> Training, fine-tuning, evaluation, deployment, and monitoring of machine-learning models. For the surrounding software (data services, APIs, glue code), prefer [`coding`](../coding/INDEX.md).

## What this domain covers

Data preparation, model architecture and training, evaluation methodology, hyperparameter search, fine-tuning, quantization, serving, and observability. Deep specializations (LLM, CV, RL, classical tabular) are facets unless their canon truly diverges.

## Subdomain decision tree

| If the task involves… | Open this subdomain |
|---|---|
| Training, fine-tuning, dataset prep, evaluation, experiment tracking | [`training/SKILL.md`](./training/SKILL.md) |
| Serving, batch inference, quantization, deployment, latency/throughput | [`inference/SKILL.md`](./inference/SKILL.md) |
| Extracting skeletal kinematics from video, BVH generation, or avatar retargeting | [`motion-fm/SKILL.md`](./motion-fm/SKILL.md) |
| Vision-language reasoning over a 3D scene (point cloud / 3DGS), scene-graph extraction, autonomous re-arrangement | [`vlm-spatial/SKILL.md`](./vlm-spatial/SKILL.md) |
| Fine-tuning LLMs (LoRA, QLoRA, full FT), instruction tuning, preference optimisation (DPO, ORPO, RLHF) | [`llm-finetuning/SKILL.md`](./llm-finetuning/SKILL.md) |
| Diffusion / flow-matching models (image, video, audio): training, schedulers, ControlNet, LoRA, step distillation | [`diffusion/SKILL.md`](./diffusion/SKILL.md) |
| End-to-end MLOps / pipelines spanning both | start with `training`, then read `inference` |

## Facet vocabulary

| Axis | Allowed values |
|---|---|
| `lang:`        | `python` |
| `framework:`   | `pytorch`, `tensorflow`, `jax`, `sklearn`, `xgboost`, `huggingface` |
| `task:`        | `cv`, `nlp`, `llm`, `tabular`, `rl`, `multimodal`, `tts`, `asr` |
| `target:`      | `gpu`, `cpu`, `tpu`, `mobile`, `edge`, `browser-wasm` |
| `precision:`   | `fp32`, `fp16`, `bf16`, `int8`, `int4` |
| `format:`      | `bvh`, `vrm`, `splat`, `pcd` |

## Shared resources

The `_shared/` folder is **not yet created** for this domain — add it when canon starts duplicating across `training/` and `inference/`:

- `_shared/canon.md` — train/val/test discipline, leakage, reproducibility
- `_shared/pitfalls.md`

See [`../coding/_shared/`](../coding/_shared/) for a reference layout.

## Related domains

- `coding` — for the surrounding services and tooling
- `3dcg`, `gameengine` — when ML is applied to graphics (denoising, generative, animation)
