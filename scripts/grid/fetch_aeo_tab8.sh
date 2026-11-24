#!/bin/zsh
# Fetch EIA AEO table 8 (Electricity supply, disposition, prices) for archived editions.
# Each edition's first column is its base (latest historical/estimated) year, giving a G/T/D price-component trend.
cd "$(dirname $0)/../.."
for yy in 14 15 16 17 18 19 20 21 22 23 25; do
  for name in aeotab8.xlsx aeotab_8.xlsx; do
    d=data/raw/grid/eia_aeo20${yy}_tab8
    mkdir -p $d
    out=$(node scripts/grid/fetch.mjs "https://www.eia.gov/outlooks/archive/aeo${yy}/excel/${name}" $d/${name})
    if echo $out | grep -q '"status":200'; then echo "aeo$yy $name ok"; break; else mv $d/${name} data/raw/grid/_probe/aeo${yy}_${name}.404.html; fi
  done
done
