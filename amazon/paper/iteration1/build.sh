#!/usr/bin/env bash
# Build iteration-1 paper in WSL and run the pre-submission checks (NEURIPS_PAPER_RULES.md 19.2, 19.14, 26).
set -e
cd "$(dirname "$0")"
python3 scripts/make_tables.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex > build.log 2>&1 || { grep -m10 '^!' main.log; exit 1; }
echo "pages: $(pdfinfo main.pdf | awk '/^Pages/{print $2}')  size: $(pdfinfo main.pdf | awk -F': *' '/^Page size/{print $2}')"
echo "type3 fonts: $(pdffonts main.pdf | grep -c 'Type 3' || true)"
echo "undefined refs/cites: $(grep -ci 'undefined' main.log || true)"
echo "?? in pdf: $(pdftotext main.pdf - | grep -c '??' || true)"
echo "overfull boxes: $(grep -c '^Overfull' main.log || true)"
python3 scripts/check_numbers.py
