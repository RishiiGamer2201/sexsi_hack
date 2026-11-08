#!/usr/bin/env bash
# Readable section of a VM run log from the first line matching PATTERN (progress bars and C++
# frames dropped). From the laptop:
#   gcloud compute ssh sqlcf-l4 --project project-54f35310-8b0b-478f-836 --zone asia-south1-a --command "bash -s -- '== grpo'" < scripts/vm_log.sh
PAT=${1:-== grpo}; LOG=~/sexsi_hack/${2:-runs/smoke.log}
tr '\r' '\n' < "$LOG" | sed -n "/$PAT/,\$p" | grep -av -e '<unknown>' -e 'it/s\]' -e '^\s*$' | cut -c1-260 | head -${3:-80}
