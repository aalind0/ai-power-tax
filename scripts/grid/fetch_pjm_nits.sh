#!/bin/zsh
# Fetch PJM Network Integration Transmission Service (NITS) rate postings + transmission enhancement worksheet.
# Source page: https://www.pjm.com/markets-and-operations/billing-settlements-and-credit
cd "$(dirname $0)/../.."
B="https://www.pjm.com/-/media/DotCom/markets-ops/settlements"
for f in network-integration-trans-service-october-2026-xls.xlsx network-integration-trans-service-june-2026-xls.xlsx \
         network-integration-trans-service-january-2026-xls.xlsx network-integration-trans-service-2025.pdf \
         network-integration-trans-service-2024.pdf network-integration-trans-service-2023.pdf \
         network-integration-trans-service-2022.pdf network-integration-trans-service-2021.pdf \
         network-service-peak-loads-2026.pdf; do
  d=data/raw/grid/pjm_${f%.*}; mkdir -p $d; node scripts/grid/fetch.mjs "$B/$f" $d/$f
done
d=data/raw/grid/pjm_transmission-enhancement-worksheet-october-2026; mkdir -p $d
node scripts/grid/fetch.mjs "https://www.pjm.com/-/media/DotCom/committees-groups/subcommittees/mss/postings/2026/transmission-enhancement-worksheet-october-2026.xlsx" $d/transmission-enhancement-worksheet-october-2026.xlsx
