#!/usr/bin/env bash
# BILLABLE. Build/push the image and submit one Vertex custom job (g2-standard-8 + 1x L4, asia-south1).
#   vertex/submit.sh build          # docker build + push to Artifact Registry (one-time per code change)
#   vertex/submit.sh job smoke      # then: sft, grpo_B, grpo_C, eval (sequential; quota is 1 L4)
# Uses --project explicitly; never touches the default gcloud config.
set -euo pipefail
PROJECT=${PROJECT:-project-54f35310-8b0b-478f-836}
REGION=asia-south1
BUCKET=${BUCKET:-${PROJECT}-sqlcf}
IMAGE=$REGION-docker.pkg.dev/$PROJECT/sqlcf/train:latest
cd "$(dirname "$0")/.."

case ${1:?build|job} in
  build)
    gcloud services enable aiplatform.googleapis.com artifactregistry.googleapis.com --project "$PROJECT"
    gcloud artifacts repositories describe sqlcf --location $REGION --project "$PROJECT" >/dev/null 2>&1 ||
      gcloud artifacts repositories create sqlcf --repository-format docker --location $REGION --project "$PROJECT"
    gcloud storage buckets describe "gs://$BUCKET" --project "$PROJECT" >/dev/null 2>&1 ||
      gcloud storage buckets create "gs://$BUCKET" --location $REGION --project "$PROJECT"
    gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
    docker build -f vertex/Dockerfile -t "$IMAGE" . && docker push "$IMAGE"
    ;;
  job)
    STAGE=${2:?stage}
    : "${HF_TOKEN:?export HF_TOKEN (account must have accepted the Tiny Aya licence)}"
    cfg=$(mktemp --suffix .yaml)
    cat > "$cfg" <<EOF
workerPoolSpecs:
- machineSpec: {machineType: g2-standard-8, acceleratorType: NVIDIA_L4, acceleratorCount: 1}
  replicaCount: 1
  diskSpec: {bootDiskType: pd-ssd, bootDiskSizeGb: 200}
  containerSpec:
    imageUri: $IMAGE
    args: ["$STAGE"]
    env: [{name: BUCKET, value: "$BUCKET"}, {name: HF_TOKEN, value: "$HF_TOKEN"}, {name: N, value: "${N:-4}"}]
EOF
    gcloud ai custom-jobs create --project "$PROJECT" --region $REGION \
      --display-name "sqlcf-$STAGE-$(date +%m%d-%H%M)" --config "$cfg"
    rm -f "$cfg"
    echo "logs: gcloud ai custom-jobs stream-logs <JOB_ID> --project $PROJECT --region $REGION"
    ;;
esac
