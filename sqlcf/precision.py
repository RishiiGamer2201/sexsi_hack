"""LoRA deltas are ~0.4% of a weight, about one bf16 step (2^-8): merging them into bf16 weights
rounds most of the update away (SFT, Nov 8: 38-61% of merged weights bit-identical to base; the
merged model failed its own training items). So: compute W + dW in fp32 and store/serve fp16
(fp16 NLL matches fp32 on Tiny Aya; bf16 is ~10x further off), and never merge in place.
"""
import functools

import torch


def lora_delta(mod, adapter: str = "default") -> torch.Tensor:
    """fp32 B @ A * scaling of one peft LoRA Linear."""
    A, B = mod.lora_A[adapter].weight, mod.lora_B[adapter].weight
    return (B.float() @ A.float()) * mod.scaling[adapter]


def _lora_layers(peft_model):
    from peft.tuners.lora import LoraLayer
    return {n: m for n, m in peft_model.named_modules() if isinstance(m, LoraLayer) and "default" in m.lora_A}


def merge_to_fp16(peft_model):
    """PeftModel -> plain fp16 model with W + dW merged in fp32 (one rounding, to fp16)."""
    for _, m in _lora_layers(peft_model).items():
        w = m.get_base_layer().weight
        w.data = (w.data.float() + lora_delta(m)).half()
    return peft_model.unload().half()


def patch_trl_vllm_fp16():
    """TRL colocated vLLM: run the engine in fp16, and sync PEFT weights as fp16(W + dW) computed
    out of place (TRL's merge_adapter/unmerge_adapter rounds in bf16 and drifts the base weights)."""
    from accelerate.utils import is_peft_model
    from trl.generation import vllm_generation as vg

    if getattr(vg, "_sqlcf_fp16", False):
        return
    vg.LLM = functools.partial(vg.LLM, dtype="float16")
    orig = vg.VLLMGeneration.sync_weights

    def sync_weights(self):
        model = self.model
        if not is_peft_model(model) or self._dist.is_fsdp or self.mode != "colocate":
            return orig(self)
        layers = _lora_layers(model)
        with torch.no_grad():
            for name, param in model.named_parameters():
                if "lora_" in name or "original_module" in name:
                    continue
                t = param.data
                owner = name.removesuffix(".base_layer.weight")
                if owner != name and owner in layers:
                    t = t.float() + lora_delta(layers[owner])
                vname = name.removeprefix("base_model.model.").replace(".base_layer", "")
                self._push_param_to_vllm(self._fix_param_name_to_vllm(vname, extra_prefixes=["modules_to_save.default."]), t)
        self.llm.reset_prefix_cache()

    vg.VLLMGeneration.sync_weights = sync_weights
    vg._sqlcf_fp16 = True
