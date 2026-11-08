#!/usr/bin/env bash
# Milestones/errors from a VM run log (default runs/smoke.log). Run from the laptop:
#   gcloud compute ssh sqlcf-l4 --project project-54f35310-8b0b-478f-836 --zone asia-south1-a --command "bash -s" < scripts/vm_status.sh
LOG=~/sexsi_hack/${1:-runs/smoke.log}
tr '\r' '\n' < "$LOG" | grep -aE "^== |^(sft|grpo) [0-9.]+ s|GRPO prompts|'loss'|'reward'|Traceback|Error|OOM|Killed|Segfault|signal|passed|failed" | grep -v Warning | cut -c1-300
pgrep -f "[t]rain.py|[e]valuate.py" >/dev/null && echo "[running]" || echo "[not running]"
