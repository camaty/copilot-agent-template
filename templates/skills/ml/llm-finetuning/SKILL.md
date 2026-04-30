---
name: ml-llm-finetuning
description: "Fine-tuning large language models with PEFT (LoRA, QLoRA), full fine-tuning, instruction tuning, and preference optimisation (DPO, ORPO). Triggers: LoRA, QLoRA, PEFT, fine-tune, SFT, DPO, ORPO, RLHF, instruction tuning, adapter, llama, mistral, qwen, gemma."
domain: ml
subdomain: llm-finetuning
facets:
  - lang:python
  - framework:pytorch
  - framework:huggingface
  - target:gpu
  - precision:bf16
  - precision:int4
applies_when:
  any_of:
    - "task fine-tunes a pretrained LLM (full or PEFT)"
    - "task uses LoRA, QLoRA, or other parameter-efficient adapters"
    - "task aligns a model with DPO, ORPO, KTO, or RLHF"
    - "task curates an SFT or preference dataset for instruction tuning"
version: 0.1.0
---
# Machine Learning / LLM Fine-tuning

## When to use

Open this skill when the deliverable is a fine-tuned LLM checkpoint
or adapter, an alignment artefact (DPO/ORPO/RLHF), or a curated
fine-tuning dataset. For generic training infrastructure (DDP,
mixed precision, eval harness) defer to
[`../training/SKILL.md`](../training/SKILL.md). For serving the
resulting model, see [`../inference/SKILL.md`](../inference/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **SFT (Supervised Fine-Tuning)** — next-token training on
  instruction–response pairs; the standard first step.
- **PEFT** — Parameter-Efficient Fine-Tuning: train a small adapter
  while freezing the base model. LoRA, IA³, prefix tuning,
  prompt tuning are the dominant families.
- **LoRA** — low-rank update `ΔW = BA` with `B ∈ ℝ^{d×r}`,
  `A ∈ ℝ^{r×d}`, rank `r ≪ d`. Typical r=8–64. Trainable params
  drop to < 1 %.
- **QLoRA** — LoRA on top of a 4-bit (NF4) quantised base.
  Enables 7B–70B fine-tunes on a single 24–80 GB GPU.
- **DPO / ORPO / KTO** — preference optimisation without an
  explicit reward model. DPO directly compares chosen vs rejected
  pairs; ORPO joins SFT + preference in one loss; KTO needs only
  binary feedback.
- **RLHF / PPO** — reward-model + RL loop; expensive and finicky.
  DPO has largely replaced it for new projects.
- **Chat template** — model-specific tokenisation of system / user
  / assistant turns. Wrong template = silent quality loss.
- **Special tokens** — `<|im_start|>`, `<|endoftext|>`,
  `<|eot_id|>`. Must be in the tokeniser and embedded; missing
  ones get split into many subwords.
- **Loss masking** — train only on assistant tokens, not on the
  system/user prompt. Otherwise the model learns to memorise
  prompts.
- **Catastrophic forgetting** — fine-tuning narrows capabilities.
  Mix in general-purpose data (5–20 %) or use PEFT to mitigate.
- **Adapter merging** — folding `BA` back into base weights for
  zero-overhead serving; pick this only after evaluating the
  merged model.
- **Sequence packing** — concatenating multiple examples per
  sequence to maximise GPU utilisation; requires `position_ids`
  reset per example.

## Recommended patterns

1. **Start with PEFT.** LoRA/QLoRA reaches 90–100 % of full fine-
   tune quality at 1–10 % of the cost. Reach for full FT only on
   evidence.
2. **QLoRA when memory-bound** (single 24/40/80 GB GPU on a 7–70B
   base). Quantise to NF4, train LoRA in bf16, paged optimiser.
3. **Use the model's official chat template.** Render every
   training example through `tokenizer.apply_chat_template`;
   never hand-format.
4. **Mask loss on prompt tokens.** Train only on assistant
   completion tokens; pad mask = `-100`.
5. **Pack sequences** to ~95 % of `max_seq_len`. Either Hugging
   Face TRL `packing=True` or unsloth's flash-attn-aware packer.
6. **Mix general data** (5–20 %) when fine-tuning on a narrow
   distribution to slow forgetting.
7. **For preferences, prefer DPO/ORPO.** Cleaner than PPO; one
   forward pair, no reward model.
8. **Evaluate on BOTH** task-specific metrics (your gold set) and
   a general benchmark (MMLU/IFEval/BBH) to detect regression.
9. **LoRA hyperparameters that usually work**: `r=16, alpha=32,
   dropout=0.05`, target `q_proj, k_proj, v_proj, o_proj` and
   the MLP up/down/gate. `lr=2e-4`, cosine schedule, 1–3 epochs.
10. **Save adapter only**, not the merged model, until validated.
    Adapters are MBs; merged is GBs.
11. **Test the chat template at inference time** before deploying;
    a mismatch silently degrades quality.
12. **For multi-GPU LoRA** use FSDP with `bf16` and full sharding;
    for QLoRA, FSDP-QLoRA needs PyTorch 2.4+ and recent PEFT.

## Pitfalls (subdomain-specific)

- ❌ **Wrong chat template at training time.** Often discovered
  weeks later when serving outputs are rambling. Use the
  tokeniser's built-in template.
- ❌ **Loss on the prompt tokens.** Inflates train loss; teaches
  the model to repeat user instructions.
- ❌ **Forgetting to add the EOS token** to each completion. The
  model never learns to stop; generates run-on outputs.
- ❌ **Tokeniser version mismatch** between training and serving.
  Pin via `tokenizer.json` content hash.
- ❌ **QLoRA with `fp16` LoRA params.** NaN city; use `bf16`.
- ❌ **Training on the test set.** When the dataset is web-scraped,
  audit for benchmark contamination (e.g. MMLU strings).
- ❌ **DPO with implausible `(chosen, rejected)` pairs.** If
  rejected is gibberish, the model just learns "fluent vs not";
  you've trained nothing useful.
- ❌ **Adapter-merged models with embedding resize ignored.**
  When new special tokens are added, embedding rows must be
  saved alongside the adapter.
- ❌ **Skipping eval on a general benchmark.** A specialised model
  may be unable to count or reason simply; capture this before
  release.
- ❌ **Re-tokenising data at every epoch.** Pre-tokenise to disk
  (Arrow / Parquet) and stream; CPU tokenisation throttles GPUs.
- ❌ **`gradient_checkpointing=True` + `use_cache=True`.** The
  cache breaks; explicitly `use_cache=False` during training.
- ❌ **Using the base model's `pad_token` as `eos`.** If pad ==
  eos, generation can't tell padding from end of sequence.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Pick the base model + license.** Match parameter count to
   serving budget; verify the licence permits your use.
2. **Curate the dataset.** Deduplicate (MinHash), filter
   length/quality, decontaminate against eval benchmarks.
   Annotate by source for ablation.
3. **Pre-tokenise** with the model's tokeniser using its chat
   template; mask non-assistant tokens; pack sequences. Save to
   Arrow/Parquet.
4. **Pick the recipe**: SFT + LoRA → optionally DPO/ORPO. Decide
   `r`, `alpha`, target modules, schedule.
5. **Run a small smoke fine-tune** (1k–10k examples, 100 steps)
   to confirm loss decreases and the chat template parses.
6. **Scale to full training**; track loss, gradient norm,
   eval metrics every N steps.
7. **Evaluate** on task-specific gold + general benchmark; stop
   when general regression > budget.
8. **Decide adapter vs merge** for serving; if merge, validate
   identical outputs on a fixed prompt set.
9. **Quantise for serving** (AWQ, GPTQ, bitsandbytes int4) and
   re-evaluate quality delta.
10. **Document the model card** — base, data, training config,
    evals, licence, intended use, known limitations.

## Validation

After completing the procedure, run:

```sh
# Static checks
ruff check ft/
mypy --strict ft/

# Smoke test: tokenise + render chat template + train 50 steps
python -m ft.smoke --base meta-llama/Llama-3.1-8B-Instruct \
    --data data/sft_packed.arrow --steps 50

# Loss-mask test: assert prompt tokens are masked (label = -100)
pytest tests/ft/test_masking.py -v

# Eval task-specific
python -m eval.run --model ckpts/best/ --suite gold_v3.jsonl

# Eval general (regression check)
lm_eval --model hf --model_args pretrained=ckpts/best/ \
    --tasks ifeval,gsm8k,mmlu --batch_size 8

# Adapter-merge parity
python -m ft.merge_and_check --adapter ckpts/best --base meta-llama/...

# Serve smoke (vLLM)
vllm serve ckpts/best/ --max-model-len 8192 &
python -m tests.serve_smoke --prompts tests/prompts.jsonl
```

## See also

- [`../training/SKILL.md`](../training/SKILL.md) — generic
  training infrastructure, distributed, mixed precision.
- [`../inference/SKILL.md`](../inference/SKILL.md) — quantising
  and serving the resulting checkpoint.
- [`../diffusion/SKILL.md`](../diffusion/SKILL.md) — for
  diffusion-LoRA workflows (different target modules, rank).
- TRL — <https://huggingface.co/docs/trl>
- PEFT — <https://huggingface.co/docs/peft>
- Unsloth — <https://github.com/unslothai/unsloth>
- DPO paper (Rafailov et al. 2023); ORPO paper (Hong et al. 2024).
- LM-Evaluation-Harness — <https://github.com/EleutherAI/lm-evaluation-harness>
