#!/usr/bin/env bash
# One-time setup on the team VM (run on the VM; idempotent). Needs the repo's read-only deploy key
# at ~/.ssh/sexsi_deploy registered on GitHub. Everything (uv cache, python, venv) stays in ~/sexsi_hack.
#   gcloud compute ssh sqlcf-l4 --project project-54f35310-8b0b-478f-836 --zone asia-south1-a --command "bash -s" < scripts/vm_setup.sh
set -euo pipefail
mkdir -p ~/.ssh
grep -q sexsi_deploy ~/.ssh/config 2>/dev/null ||
  printf 'Host github.com\n  IdentityFile ~/.ssh/sexsi_deploy\n  IdentitiesOnly yes\n' >> ~/.ssh/config
grep -q github.com ~/.ssh/known_hosts 2>/dev/null || ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null
[ -d ~/sexsi_hack/.git ] || git clone -q git@github.com:RishiiGamer2201/sexsi_hack.git ~/sexsi_hack
cd ~/sexsi_hack && git pull -q --ff-only

command -v uv >/dev/null || [ -x ~/.local/bin/uv ] || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH" UV_CACHE_DIR="$PWD/.cache/uv" UV_PYTHON_INSTALL_DIR="$PWD/.cache/python"

mkdir -p vendor
[ -d vendor/AgentTune ] || { git clone -q https://github.com/Lexsi-Labs/AgentTune.git vendor/AgentTune && git -C vendor/AgentTune checkout -q d4db4c1; }
# multi-turn token-stream + double-BOS fix for the vLLM rollout path (idempotent)
git -C vendor/AgentTune apply --reverse --check ../../patches/agenttune-multiturn-ids.patch 2>/dev/null ||
  git -C vendor/AgentTune apply ../../patches/agenttune-multiturn-ids.patch

[ -x .venv-train/bin/python ] || uv venv -q --python 3.12 .venv-train
uv pip install -q --python .venv-train/bin/python -e vendor/AgentTune trl peft datasets pandas scipy matplotlib pytest vllm==0.22.1
.venv-train/bin/python -c "import torch, vllm, trl, peft; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'vllm', vllm.__version__, 'trl', trl.__version__)"
