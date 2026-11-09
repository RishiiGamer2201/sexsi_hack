#!/usr/bin/env bash
# Power the VM off at the end of a job (stops GPU billing) unless someone else is logged in
# or still has a job running. Run as the last line of a VM job script.
# A laptop watcher can touch runs/HOLD_AUTOSTOP to copy results off first: wait until it is gone (max 30 min).
for _ in $(seq 60); do [ -f ~/sexsi_hack/runs/HOLD_AUTOSTOP ] || break; sleep 30; done
others=$(who | awk -v me="$(whoami)" '$1 != me' | wc -l)
jobs=$(pgrep -fc "[t]rain.py|[e]valuate.py" || true)
if [ "$others" -gt 0 ] || [ "$jobs" -gt 0 ]; then
  echo "== autostop skipped: $others other sessions, $jobs jobs"; exit 0
fi
echo "== autostop: powering off $(date -u +%H:%MZ)"
sudo shutdown -h now
