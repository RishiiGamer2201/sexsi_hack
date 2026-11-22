#!/usr/bin/env bash
# Start the team VM, retrying through L4 stockouts. Usage: bash scripts/vm_start.sh [tries, 2 min apart]
P=project-54f35310-8b0b-478f-836; Z=asia-south1-b
for i in $(seq "${1:-15}"); do
  gcloud compute instances start sqlcf-l4b --project $P --zone $Z --quiet >/dev/null 2>&1 && { echo "started (try $i)"; exit 0; }
  echo "stockout, try $i"; sleep 120
done
exit 1
