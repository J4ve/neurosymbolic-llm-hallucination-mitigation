"""Verify HPC env has all imports + GPU access."""

import torch
print("torch:", torch.__version__, "cuda available:", torch.cuda.is_available(),
      "n_gpu:", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    p = torch.cuda.get_device_properties(i)
    free, total = torch.cuda.mem_get_info(i)
    print(f"  GPU {i}: {p.name}  total={total/1e9:.1f}G  free={free/1e9:.1f}G")

import z3
print("z3 ok")

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model
print("transformers + peft ok")

from z3_runner import run_smtlib
r = run_smtlib("(declare-const x Int)(assert (= x 5))(check-sat)(get-value (x))")
print("z3_runner ok:", r)

print("ALL OK")
