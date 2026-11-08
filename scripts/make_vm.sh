#!/usr/bin/env bash
# BILLABLE (~$0.74/hr running). Create the team's L4 VM; tries each asia-south1 zone on stockout.
# Stop it when idle:  gcloud compute instances stop sqlcf-l4 --project $PROJECT --zone <zone>
set -u
PROJECT=${PROJECT:-project-54f35310-8b0b-478f-836}
for z in asia-south1-a asia-south1-b asia-south1-c; do
  gcloud compute instances create sqlcf-l4 --project "$PROJECT" --zone "$z" \
    --machine-type g2-standard-4 --accelerator type=nvidia-l4,count=1 --maintenance-policy TERMINATE \
    --image-family common-cu129-ubuntu-2204-nvidia-580 --image-project deeplearning-platform-release \
    --boot-disk-size 150GB --boot-disk-type pd-balanced \
    --metadata install-nvidia-driver=True && { echo "CREATED in $z"; exit 0; }
done
exit 1
