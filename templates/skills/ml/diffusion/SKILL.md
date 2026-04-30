---
name: ml-diffusion
description: "Diffusion model training and inference: schedulers, classifier-free guidance, ControlNet, LoRA, image/video/audio. Triggers: diffusion, stable diffusion, SDXL, SD3, Flux, ControlNet, scheduler, DDIM, DPM-Solver, classifier-free guidance, CFG, latent diffusion, video diffusion."
domain: ml
subdomain: diffusion
facets:
  - lang:python
  - framework:pytorch
  - framework:huggingface
  - target:gpu
  - precision:fp16
  - precision:bf16
applies_when:
  any_of:
    - "task trains, fine-tunes, or distils a diffusion model (image, video, audio, 3D)"
    - "task implements or tunes a sampler (DDIM, DPM-Solver, Heun, LCM, Turbo)"
    - "task adds ControlNet, IP-Adapter, T2I-Adapter, or LoRA to a diffusion pipeline"
    - "task optimises diffusion inference latency (step distillation, batch, KV-cache for transformer DiT)"
version: 0.1.0
---
# Machine Learning / Diffusion

## When to use

Open this skill when the model is a diffusion / flow-matching system
(image, video, audio, or 3D) and the task is training, fine-tuning,
controlling, or accelerating it. For LLM fine-tuning, use
[`../llm-finetuning/SKILL.md`](../llm-finetuning/SKILL.md). For
generic training infra (DDP, mixed precision), use
[`../training/SKILL.md`](../training/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Forward / reverse process** — forward adds Gaussian noise per
  schedule (`β_t`); reverse predicts noise (`ε`-prediction),
  velocity (`v`-prediction), or x₀.
- **Latent diffusion** — diffusion in a VAE-encoded latent space
  (8× smaller than pixel space). Stable Diffusion family.
- **Schedulers / samplers** — DDIM (deterministic), DDPM, DPM-Solver
  (++, 2M, 3M), Heun, Euler-A, LCM, Turbo. Trade quality vs steps.
- **Classifier-free guidance (CFG)** — `ε = ε_uncond + s × (ε_cond
  - ε_uncond)`; `s` is the guidance scale. Higher `s` → more
  prompt adherence, less diversity, more saturated artefacts.
- **DiT (Diffusion Transformer)** — replaces UNet with a transformer
  on patchified latents. SD3, Flux, video models.
- **Flow matching** — alternative to score matching; trains a
  velocity field. Flux uses rectified flow; trains stably with
  fewer tricks than DDPM.
- **ControlNet / T2I-Adapter** — conditioning networks that inject
  spatial signals (edges, depth, pose, segmentation) at specific
  UNet blocks.
- **IP-Adapter** — image-prompt adapter that mixes a reference
  image embedding into cross-attention. Cheaper than ControlNet
  for "use this style".
- **LoRA for diffusion** — typically targets attention `to_q,
  to_k, to_v, to_out` in cross-attention; sometimes the text
  encoder.
- **EMA weights** — exponential moving average of parameters; used
  for inference. Must be saved alongside the live weights.
- **VAE** — pre-trained encoder/decoder between pixel and latent.
  Don't fine-tune unless you have a *lot* of data; usually
  freeze.
- **Step distillation** — LCM, Turbo, ADM, Hyper-SD. Reduces
  20+ → 1–8 steps via consistency or adversarial losses.
- **Negative prompt** — text fed to the unconditional branch of
  CFG; pulls outputs *away* from the described attributes.

## Recommended patterns

1. **Train in `bf16` mixed precision.** `fp16` requires loss
   scaling and frequently NaNs on diffusion losses; `bf16` is
   stable.
2. **Maintain an EMA copy** of the model weights (decay 0.9999 or
   0.999); evaluate and ship the EMA, not the live weights.
3. **Snr-weighted losses** (Min-SNR-γ) for `ε`-prediction
   training; substantially better convergence at large model
   scale.
4. **Cache text embeddings & VAE latents to disk** for fixed
   datasets. CPU encoding is the throughput bottleneck.
5. **Match the scheduler at inference to the training
   parameterisation.** A `v`-prediction model needs a `v`-aware
   sampler; using a default DDPM sampler corrupts outputs.
6. **CFG tuning** — sweep `s ∈ {3, 5, 7, 9}` per prompt class.
   What's right for portraits over-saturates landscapes.
7. **For control** prefer ControlNet for strict spatial fidelity,
   IP-Adapter for style, LoRA for concept/character, textual-
   inversion for trivially small concept changes.
8. **LoRA recipes** — `r=8–32`, `alpha=r` (most diffusion
   pipelines double `alpha`), target attention only first;
   expand if quality lags.
9. **Step distillation for production**. LCM/Turbo + 4–8 steps
   matches 20–30 step quality at 4× throughput.
10. **DiT-specific**: enable `xformers` or PyTorch SDPA;
    `torch.compile(model, mode="reduce-overhead")` cuts 20–40 %
    latency on Ada+ GPUs.
11. **Eval with FID/CLIPScore + human/LLM-judge.** FID alone
    rewards memorisation; CLIPScore alone rewards prompt
    adherence regardless of quality.
12. **Safety filters at the gate**, not in post — NSFW classifier
    on outputs, prompt blocklist on inputs; both auditable.

## Pitfalls (subdomain-specific)

- ❌ **Mixing `ε`-pred and `v`-pred carelessly.** Loss appears
  fine, but FID is way off. Always cross-check the model's
  training parameterisation.
- ❌ **Saving live weights instead of EMA.** Every metric
  regresses 5–15 %.
- ❌ **CFG > ~12 for SD/SDXL** — saturates colours, freezes
  composition, ignores nuance. Keep ≤ 7 unless you know why.
- ❌ **Training without cached latents.** GPU sits at 30 % util
  while VAE encodes on the CPU.
- ❌ **VAE in `fp16` for SD1.5.** Decoder is unstable; cast to
  `fp32` (or use the `madebyollin/sdxl-vae-fp16-fix`).
- ❌ **Forgetting noise schedule at the boundary.** Some
  schedulers expect `t ∈ [0, 1]`, others integer steps. Mix-ups
  produce noise.
- ❌ **LoRA targeting cross-attention only when style change is
  needed in self-attention.** Symptom: prompt obeys, style
  doesn't shift.
- ❌ **ControlNet at full strength on every step.** Causes ghosting
  and prompt drift; fade strength to 0 in the last 30 % of steps.
- ❌ **Distilling a model on its own outputs without filtering.**
  Bias amplification; collapse modes.
- ❌ **Evaluating without prompt diversity.** A 100-prompt eval
  with 10 prompts repeated is not 100 samples.
- ❌ **Shipping without a CLIP/aesthetic safety probe.** Outputs
  drift across versions; gate releases on a fixed probe set.
- ❌ **Streaming images out of `torch.compile`d pipelines without
  warmup.** First image takes 30+ s; don't include in latency
  measurements.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Pick the base** (SD1.5, SDXL, SD3, Flux, video model) and
   verify the parameterisation (`ε`/`v`/flow), VAE, and chat-
   prompt format.
2. **Curate the dataset** — caption with a strong VLM (BLIP-2 or
   GPT-4o), filter NSFW + duplicates, optionally re-caption with
   the target style guide.
3. **Cache VAE latents and text embeddings** to Parquet/Arrow.
4. **Configure training** — `bf16`, EMA, Min-SNR loss for
   `ε`-pred or rectified flow loss for flow matching, gradient
   checkpointing for big DiTs.
5. **Run a small smoke fine-tune** (e.g. 500 steps on 5k
   images); inspect generations every 100 steps.
6. **Scale to full training**; track FID/CLIPScore/aesthetic on a
   fixed eval set every N steps; ship EMA.
7. **For control / customisation**: pick ControlNet vs IP-Adapter
   vs LoRA based on the task; train and eval against the same
   probe.
8. **Step distillation** (optional) once base is converged; eval
   for quality regression.
9. **Inference optimisation** — `xformers`/SDPA, `torch.compile`,
   batched CFG, optionally TensorRT or vLLM-Diffusers.
10. **Safety gates and policy** before public exposure.

## Validation

After completing the procedure, run:

```sh
# Static checks
ruff check diffusion/ && mypy --strict diffusion/

# Smoke fine-tune (must reduce loss within 200 steps on 32 images)
python -m diffusion.smoke --base SDXL-base --data data/smoke

# Sample fixed-prompt grid (deterministic with seed)
python -m diffusion.sample --ckpt ckpts/best --prompts probes/v3.json \
    --seeds 0,1,2 --out probes/out

# Eval against probe
python -m diffusion.eval probes/out --metrics fid,clip,aesthetic \
    --baseline probes/golden.json --max-fid-delta 2.0

# Inference perf (warmup excluded)
python -m diffusion.bench --ckpt ckpts/best --batch 4 --steps 30 \
    --warmup 5 --iters 50

# Safety gate
python -m diffusion.safety_probe --ckpt ckpts/best --probe probes/safety.json
```

## See also

- [`../training/SKILL.md`](../training/SKILL.md) — DDP/FSDP,
  mixed precision, eval discipline.
- [`../inference/SKILL.md`](../inference/SKILL.md) — quantisation,
  graph capture, throughput.
- [`../llm-finetuning/SKILL.md`](../llm-finetuning/SKILL.md) — for
  text-encoder fine-tuning that pairs with diffusion LoRAs.
- �� Diffusers — <https://huggingface.co/docs/diffusers>
- "Elucidating the Design Space of Diffusion Models" (Karras 2022).
- Min-SNR weighting (Hang 2023); rectified flow (Liu 2022).
- LCM (Luo 2023), Hyper-SD (Bytedance 2024).
