#!/usr/bin/env bash
# Print the URL and commit of each vendored repo (for README / reproducibility).
cd "$(dirname "$0")/../vendor"
for d in */; do echo "${d%/} $(git -C "$d" remote get-url origin) $(git -C "$d" rev-parse --short HEAD)"; done
