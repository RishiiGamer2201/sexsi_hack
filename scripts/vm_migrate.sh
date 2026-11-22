#!/usr/bin/env bash
# BILLABLE (~$0.74/hr once up). Move sqlcf-l4 out of asia-south1-a (L4 stockout since Nov 21 20:27 IST; move OK'd by Rishii Nov 22).
#  1. snapshot its disk (seed-1 adapters, venv, model cache all live there);
#  2. each round: try to start the old VM, then create sqlcf-l4b from the snapshot in the first zone with a free L4;
#  3. point the repo scripts at the new name + zone and relaunch laptop_seed2.sh + laptop_leaky.sh.
# The old stopped VM (asia-south1-a) and the snapshot are kept until seed 1 is copied off the new VM: delete them by hand.
#   setsid nohup bash scripts/vm_migrate.sh > runs/vm_migrate.log 2>&1 < /dev/null &
set -uo pipefail
cd "$(dirname "$0")/.."
P=project-54f35310-8b0b-478f-836; OLD=asia-south1-a; SNAP=sqlcf-l4-move
DEADLINE=$(date -d "2026-11-24T12:00:00+05:30" +%s)
# asia first: the snapshot lives in the asia multi-region, so restoring elsewhere adds egress
ZONES="asia-south1-b asia-south1-c asia-southeast1-c asia-southeast1-a asia-southeast1-b asia-east1-a asia-east1-b
 asia-east1-c asia-northeast1-a asia-northeast1-b asia-northeast1-c europe-west4-a europe-west4-b europe-west4-c
 us-central1-a us-central1-b us-central1-c us-east1-b us-east1-c us-east1-d us-west1-a us-west1-b us-west1-c"
ist() { TZ=Asia/Kolkata date "+%d %b %H:%M"; }

gcloud compute snapshots describe $SNAP --project $P >/dev/null 2>&1 ||
  gcloud compute disks snapshot sqlcf-l4 --project $P --zone $OLD --snapshot-names $SNAP --quiet || { echo "== snapshot failed"; exit 1; }
echo "== snapshot $SNAP ready $(ist) IST ($(gcloud compute snapshots describe $SNAP --project $P --format='value(storageBytes)') bytes)"

Z=; VM=; n=0
# instance names are unique project-wide here, so the moved VM is sqlcf-l4b.
# rerun after a laptop restart: a sqlcf-l4b this script already made gets restarted, not re-created
NZ=$(gcloud compute instances list --project $P --filter="name=sqlcf-l4b" --format="value(zone.basename())" | head -1)
while :; do
  gcloud compute instances start sqlcf-l4 --project $P --zone $OLD --quiet >/dev/null 2>&1 && { VM=sqlcf-l4; Z=$OLD; break; }
  if [ -n "$NZ" ]; then
    gcloud compute instances start sqlcf-l4b --project $P --zone $NZ --quiet >/dev/null 2>&1 && { VM=sqlcf-l4b; Z=$NZ; break; }
  else
    for z in $ZONES; do
      err=$(gcloud compute instances create sqlcf-l4b --project $P --zone "$z" --machine-type g2-standard-4 \
        --accelerator type=nvidia-l4,count=1 --maintenance-policy TERMINATE \
        --source-snapshot $SNAP --boot-disk-size 150GB --boot-disk-type pd-balanced --quiet 2>&1) && { VM=sqlcf-l4b; Z=$z; break 2; }
      [ $n -eq 0 ] && echo "$z: $(echo "$err" | grep -oE 'STOCKOUT|[A-Z_]*QUOTA[A-Z_]*|already exists|not found' | head -1)"
      # a failed create can leave its boot disk behind, which would block every later try in that zone
      gcloud compute disks delete sqlcf-l4b --project $P --zone "$z" --quiet >/dev/null 2>&1
    done
  fi
  n=$((n + 1))
  [ "$(date +%s)" -gt "$DEADLINE" ] && { echo "== gave up $(ist) IST after $n rounds"; exit 1; }
  echo "no L4 in any zone, round $n, $(ist) IST"; sleep 300
done
echo "== $VM up in $Z $(ist) IST"

if [ "$VM" = sqlcf-l4b ]; then
  F="scripts/laptop_seed2.sh scripts/laptop_leaky.sh scripts/vm_start.sh scripts/vm_status.sh scripts/vm_log.sh scripts/vm_grpo.sh scripts/vm_setup.sh scripts/vm_sft.sh"
  sed -i -e "s/asia-south1-a/$Z/g" -e 's/sqlcf-l4\([^-a-z0-9]\|$\)/sqlcf-l4b\1/g' $F
  echo "== scripts now use $VM in $Z: $(grep -l "sqlcf-l4b" $F | tr '\n' ' ')"
fi
setsid nohup bash scripts/laptop_seed2.sh >> runs/laptop_seed2.log 2>&1 < /dev/null &
sleep 60  # laptop_leaky waits for vm_seed2.sh on the VM anyway
setsid nohup bash scripts/laptop_leaky.sh >> runs/leaky/laptop.log 2>&1 < /dev/null &
echo "== relaunched laptop_seed2.sh + laptop_leaky.sh $(ist) IST"
