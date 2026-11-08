import torch
from peft import LoraConfig, get_peft_model

from sqlcf.precision import lora_delta, merge_to_fp16


def _peft(seed=0):
    torch.manual_seed(seed)
    net = torch.nn.Sequential()
    net.add_module("proj", torch.nn.Linear(256, 256, bias=False))
    net = net.to(torch.bfloat16)
    m = get_peft_model(net, LoraConfig(r=8, lora_alpha=16, target_modules=["proj"]))
    lora = m.base_model.model.proj
    torch.nn.init.normal_(lora.lora_B["default"].weight, std=0.0007)  # nonzero delta, ~0.4% of W
    return m, lora


def test_fp16_merge_keeps_small_lora_delta():
    m, lora = _peft()
    w = lora.get_base_layer().weight.detach().float().clone()
    d = lora_delta(lora).detach()
    rel = d.norm() / w.norm()
    assert 1e-3 < rel < 2e-2, rel  # the regime of the SFT run
    truth = w + d
    naive_bf16 = (lora.get_base_layer().weight.detach() + d.to(torch.bfloat16)).float()
    fp16 = merge_to_fp16(m).proj.weight.detach().float()
    err = lambda x: ((x - truth).norm() / d.norm()).item()  # error relative to the update itself
    assert err(fp16) < 0.1 < err(naive_bf16), (err(fp16), err(naive_bf16))
