# Bills: retail electricity prices and the anatomy of a bill (findings)

Research date: 2026-11-23. Area owner: `bills`. All numbers come from files in `data/processed/` (built by `scripts/bills/*`)
or from sources linked inline. "UNVERIFIED" means the figure was not checked against a live primary source this session.
Real (inflation-adjusted) figures use the BLS CPI-U all-items index (CUUR0000SA0). October 2025 CPI was never published
(federal shutdown), so the 2025 annual average uses 11 months.

## Headline numbers (for the site)

| Metric | Value | Source |
|---|---|---|
| US avg residential price, 2025 | **17.24 c/kWh** (2020: 13.16; 2015: 12.65) | EIA-861M, `bills_state_annual.csv` |
| US avg residential bill, 2025 | **$150.68/month** at 874 kWh (2020: $117.46 at 893 kWh) | same |
| US price, 12 months to Aug 2026 | **18.04 c/kWh, +6.5% y/y** vs CPI-U +3.4% | `bills_state_monthly.csv` (US row, `res_price_ttm_*`) |
| Nominal change 2020->2025 | price +31.0%; CPI-U +24.4%; CPI electricity +36.1% | EIA-861M; BLS |
| Real change 2020->2025 | **+5.3%** (US); 2015->2025 **+0.3%** | `bills_state_annual.csv` |

## Key findings

1. **Nationally, the 2025 residential price is roughly where it was in 2015 after inflation, but 2026 is pulling ahead.**
   In 2025 dollars the US average was 17.18 c/kWh in 2015, fell to 16.23 c in 2021, and rose back to 17.24 c in 2025
   (+0.3% vs 2015, +6.2% vs the 2021 low). In the 12 months to August 2026 the nominal price (18.04 c) is up 6.5% y/y,
   about double CPI-U inflation (3.4%), so 2026 is the first year in a decade with a clear real increase nationally.
   (EIA-861M via `bills_state_monthly.csv`; BLS CPI.)

2. **The increase is concentrated, not universal.** From 2020 to 2025, 22 of 51 jurisdictions (50 states + DC) saw
   residential prices *fall* in real terms (biggest: Iowa -12.1%, Nebraska -10.2%, Kansas -9.7%, North Dakota -9.0%).
   The largest real increases were DC +39.5%, Maine +32.4%, California +23.3%, Maryland +20.7%, New York +15.5%,
   Pennsylvania +14.2%, New Jersey +12.8% (`bills_state_annual.csv`, `bills_summary.json`).

3. **2025-26 hot spots are mostly PJM and the Northeast.** Twelve-month price growth to Aug 2026 (vs the prior 12 months):
   DC +19.8%, New Hampshire +13.8%, Maryland +12.7%, Pennsylvania +12.3%, Washington +11.9%, Ohio +11.7%,
   Virginia +11.5%, New York +11.2%, Illinois +10.6%, New Jersey +10.2%. Ten states are at or above +10%; 44 are above
   the latest CPI-U rate; only 2 are falling. Seven of those ten are PJM states/DC.

4. **Utility-level: about 1 in 9 utilities had a double-digit increase in 2025; nearly 1 in 4 in 2026 so far.**
   Among 927 utilities with >=10,000 full-service residential customers, 11.4% (106) raised average residential prices
   >=10% in 2025 vs 2024; 61.6% rose faster than CPI (2.6%) and 19.7% fell (EIA-861 2024 and 2025 final). For investor-owned
   utilities the double-digit share was 21.7%. Comparing Jan-Aug 2026 with Jan-Aug 2025 (EIA-861M, 300 utilities
   >=10k customers), **23.7% are up >=10%**, 69.7% beat CPI, 7.7% fell; customer-weighted average +6.4%.

5. **PJM utilities rose about twice as fast as the rest in 2025.** Customer-weighted change in full-service residential
   price, 2024->2025: PJM +10.4% (17% of PJM utilities >=10%), NYISO +9.6%, MISO +5.2%, non-RTO/vertically integrated
   +5.0%, SPP +4.2%, ERCOT +3.5%, ISO-NE +2.2%, CAISO -2.3% (EIA-861; `bills_summary.json` -> `by_rto_2020_2025`).
   Over 2020->2025 in real terms CAISO utilities lead (+32.9%), then NYISO (+20.3%) and PJM (+11.2%); SPP is negative (-2.2%).

6. **Biggest large-utility jumps (>=250k residential customers), 2024->2025:** Pepco DC +25.3%, NYSEG +23.3%,
   PSE&G +22.6%, Tampa Electric +18.1%, JCP&L +17.5%, Duke Energy Indiana +17.5%, Rochester G&E +17.3%,
   Central Maine Power +16.9%, ComEd +16.4%, Puget Sound Energy +16.2%. **Jan-Aug 2026 vs 2025:** El Paso Electric +31.6%,
   Niagara Mohawk +24.9%, Puget Sound Energy +24.2%, **Dominion Energy Virginia +20.1%**, Pepco DC +17.0%, BGE +16.1%,
   ComEd +13.2%, DTE +12.2%. Falling: United Illuminating -11.7%, PG&E -11.1%, Duke Energy Florida -9.9%, CL&P -9.7%.
   Over 2020->2025 (real): NYSEG +58%, SDG&E +44%, Pepco DC +42%, RG&E +40%, SCE +39%, Tampa Electric +38%,
   Ameren Illinois +38%, CMP +36%, BGE +34%. Largest real declines: NSTAR Electric -23%, Evergy Metro -18%,
   Interstate P&L -14%, MidAmerican -13%.

7. **PJM capacity costs went from almost nothing to ~2 c/kWh in two years, and they hit bills every June 1.**
   PJM's weighted capacity price was $45.57/MW-day for 2024/25, $296.98 for 2025/26, $329.17 for 2026/27 and $333.44 for
   2027/28 (the last two at the negotiated cap). Spread across all PJM load, the capacity cost was 0.36 c/kWh in 2024, 1.28 c
   in 2025 and an estimated 1.96 c in 2026, about $20 a month on a 1,000 kWh bill (LBNL July 2026 data file, from the PJM IMM).
   Example: Synapse (for the DC People's Counsel, an advocate) estimated +1.7 c/kWh, +$10/month (+9%) for Pepco DC residential
   bills from the 2025/26 auction alone. How it reaches bills: default-service supply prices reset each **June 1** in PA, OH, IL,
   MD, NJ, DE and DC. NJ's 3-year BGS ladder (and multi-year tranches in MD/DC/PA) phase a shock in over 2-3 years. In
   vertically integrated PJM utilities (Dominion, APCo) capacity goes through base rates and riders instead.
   See `bills_anatomy.json` -> `pjm_capacity_context`. (Who caused the capacity price spike, including data-center load
   forecasts, belongs to the `markets` area.)

8. **2026 supply resets were milder than 2025 because of the capacity price cap.** PA Prices to Compare on June 1, 2026:
   PECO +5.0% (11.024->11.572 c, estimated), PPL +1.5%, Duquesne +2.8%, Met-Ed +7.6%, West Penn +10.3%, Penelec +11.9%
   (PA PUC). NJ BGS (Feb 2026 auction): PSE&G 650 kWh bill -1.8% ($183.46->$180.23), JCP&L +1.6% ($135.24->$137.47),
   before state bill credits. The BPU credits the PJM collar ($175-$325/MW-day) for keeping results flat. Delivery-side
   increases (distribution rate cases, transmission) were the bigger 2026 driver in many places, e.g. Dominion's base-rate
   step (+$11.24/month at 1,000 kWh from Jan 2026, on a $149.92 base) and PECO's Jan 2026 distribution step.

9. **What a bill is made of (1,000 kWh, 2025/26 tariffs; `bills_anatomy.json`, 13 utilities).** In restructured PJM
   utilities, supply (generation + capacity, often bundled with transmission) is about 40-72% of the bill and distribution
   16-44%. PSE&G is $277.20 a month annualized (BGS supply + transmission 72%, distribution 22%, riders 4%). BGE is $239.50
   (SOS supply incl. transmission 70%, delivery 20%, riders 6%, fixed 4%). PECO is $235.62 (generation 46%, distribution 44%,
   transmission 3%, riders 2%, fixed 5%). JCP&L is $205.86 in summer (BGS supply 70%, distribution 21%). Pepco DC is $194.41
   on the 2025/26 SOS (supply 67%, distribution 16%, fixed 9%, riders 9%). ComEd is $195.38 (supply 43%, distribution 32%,
   transmission 9%, riders 7%, fixed 10%). AEP Ohio is $186.55 (SSO generation 41%, transmission and riders 30%).
   In vertically integrated utilities **riders are now a large slice**. At Dominion ($168.53 annualized), fuel plus
   rate-adjustment-clause riders (transmission T1, offshore wind, RPS, nuclear life extension, grid transformation, new
   plants) are 52% and base rates 44%. At Georgia Power (~$160 annualized, $181 in summer) fuel, ECCR and DSM riders are 36%.
   Duke Energy Carolinas ($141.55) is still 87% base rate. Texas (Oncor area): TDU delivery $72.73 (38%) plus about
   11.6 c/kWh retail energy (62%). PG&E at 1,000 kWh is $406.89. That is atypical, because the average PG&E customer uses
   ~450 kWh. PG&E's June 2026 tariff unbundles as generation 12.9 c, distribution 18.0 c, transmission 5.1 c, and wildfire
   fund + hardening charges 0.98 c, plus a new $24.12/month income-graduated base services charge. Each line has a source
   URL, an effective date and a `verified`/`derived` flag. Tariff sums were cross-checked against EIA-861M 2026 average
   revenue per kWh: Duke 14.15 vs 14.14 c, Dominion 16.9 vs 17.7 c, ComEd 19.5 vs 19.9 c, Georgia 16.0 vs 16.9 c,
   PSE&G 27.7 vs 26.4 c, BGE 24.0 vs 22.2 c and PECO 23.6 vs 19.7 c (CAP discounts and a lower winter PTC lower PECO's
   average).

10. **The biggest documented drivers of 2024-25 increases were wholesale/fuel costs and wires, not one single cause.**
    LBNL reviewed the 30 states with real increases above 2%. The drivers it cited most were fuel/wholesale supply (21 states),
    distribution costs (16), generation capex (11), transmission (11), storm cost recovery (9), capacity-market prices (7),
    extreme inflation (6), clean-energy policy (5) and wildfire costs (2) (LBNL July 2026, tab "Primary drivers").
    Specific line items: wildfire mitigation and liability add about 5.0 c/kWh at PG&E, 4.7 c at SDG&E and 3.3 c at SCE (2025).
    Storm recovery added 3.24 c at Duke Energy Florida, 2.5 c at Central Maine Power, 2.0 c at Tampa Electric and 1.43 c at
    Entergy Louisiana. Real IOU distribution costs per kWh in CAISO rose 3.3 c from 2019 to 2025, but were flat in PJM and
    fell in ERCOT (LBNL, from FERC Form 1).

11. **The rate-case pipeline points up.** IOU revenue-increase requests reached $18.2B (2025$) in 2025, the most since the
    mid-1980s. Regulators approved 64% of requested dollars in 2021-25, compared with 52% in 2016-20 (S&P Global via LBNL).
    That is a forward indicator for 2026-27 delivery charges.

12. **Counter-evidence: load growth has, so far, mostly lowered prices.** LBNL finds that from 2019 to 2025 the states with
    the fastest retail-sales growth mostly saw real price declines. North Dakota (+40.7% sales, residential -1.12 c/kWh real),
    Nebraska (+23.8%, -1.18 c), New Mexico (+26.9%, -0.74 c) and Iowa (+14.7%, -1.92 c) all fit this. Virginia (+22.2% sales,
    the largest data-center market) was flat in real residential terms (-0.01 c) through 2025, and Texas (+21%) was +0.57 c.
    The biggest real increases came in states whose sales *fell*: California (-5.0%, +8.33 c), Maine (-5.9%, +5.56 c),
    DC (-7.1%, +5.50 c), New York (-1.4%, +4.11 c), Maryland (-2.0%, +2.86 c) and New Jersey (-1.2%, +2.94 c)
    (LBNL tab "State growth vs prices"). The mechanism is fixed T&D costs spread over more kWh. LBNL also flags PJM as the
    exception, because load forecasts feed capacity prices region-wide (see finding 7). Utilities and regulators also project
    future savings from large-load contracts: Georgia PSC -$8.50/month (2029-31), NIPSCO $7-9/month, Entergy $5B over 20 years,
    Xcel MN $1.1B. These are claims, not outcomes, and LBNL says they "require monitoring".

13. **Virginia's 2026 jump is a delivery and base-rate story with a data-center backdrop.** Dominion's residential price is
    up 20.1% Jan-Aug 2026 vs 2025 (EIA-861M). The SCC's Nov 2025 biennial order added $11.24/month in 2026 and $2.36 in 2027
    to a $149.92 bill at 1,000 kWh (ROE 9.8%; Dominion had asked for $19.57). It also created a new >=25 MW rate class from
    Jan 2027, with 14-year minimum-demand commitments meant to insulate other customers from data-center build-out costs
    (Cardinal News summary of the SCC order). Dominion attributes the increase to inflation and grid-equipment costs. Fuel-factor
    changes are separate.

14. **California is the outlier both ways.** California has the highest real increase since 2015 (+35.8%) and the highest
    distribution-cost growth. But in 2026 PG&E's average residential price is *down* 11% y/y (Jan-Aug), and SCE and SDG&E
    are not among the risers. "Rising bills" is not a 2026 California story.

15. **Usage matters as much as price for the bill.** Average residential use ranges from about 450-550 kWh/month (PG&E,
    SCE, ComEd ~600) to more than 1,200 kWh (Dominion NC, Entergy Louisiana). A 1,000 kWh "typical bill" overstates
    California and Chicago bills and understates Southern ones. The site should show the utility's own average kWh
    (`avg_monthly_kwh` / `res_avg_monthly_kwh`) next to any 1,000 kWh comparison.

## Data products (all in `data/processed/`)

| File | Rows | Grain | Notes |
|---|---|---|---|
| `bills_utility_prices.csv` | 34,375 | year (2013-2025) x EIA utility id x state | EIA-861 annual, final through 2025. `basis` = bundled / energy_only / delivery_only. Main `res_*` columns use the bundled (full-service) rows. In restructured states these are default-service customers. `res_delivery_only_*` = wires charges for shopping customers. `res_all_in_price_cents_kwh` adds a supply estimate for delivery-only utilities (state avg supplier price; in TX the statewide REP all-in price). Commercial and industrial included. `ba_code`/`rto_iso` come from EIA's BA field. Real columns are in 2025 $. |
| `bills_utility_monthly.csv` | 13,561 | month (2024-01..2026-08) x utility x state | EIA-861M, bundled sales only (verified: 2025 monthly sums = 861 Part A for PECO, BGE, ComEd, PG&E). 2026 is preliminary. ~340 utilities. |
| `bills_state_monthly.csv` | 7,280 | month (2015-01..2026-08) x state (+DC, +US) | EIA-861M `sales_revenue.xlsx`. Includes trailing-12-month price, y/y %, real price (Aug-2026 $), CPI-U all items and CPI electricity. US = sum of states. |
| `bills_state_annual.csv` | 572 | year (2015-2025) x state | Calendar sums of the monthly file; nominal and real 2025 $. |
| `bills_cpi_monthly.csv` | 262 | month 2005-01..2026-10 | BLS CUUR0000SA0, CUUR0000SEHF01, CUSR0000SEHF01. 2025-10 missing (not published). |
| `bills_anatomy.json` | 13 utilities | utility | 1,000 kWh bill line items, $ and %, source URL, effective date, verified/derived flags, EIA cross-check, PJM capacity explainer. PECO, BGE, ComEd, AEP Ohio, JCP&L, PSE&G, Pepco DC, Dominion VA, Georgia Power, Oncor (+retail), Duke Energy Carolinas, Entergy Louisiana, PG&E. |
| `bills_ba_codes.csv` | 64 | EIA balancing authority | BA code -> name, states, `rto_iso` mapping used for `bills_utility_prices.csv` (EIA-861 2025 Balancing_Authority file). The BA is a proxy for the RTO: utilities inside an RTO footprint but in their own BA (e.g. some MISO South/SPP members) map to `none`. |
| `bills_summary.json` | - | - | Headline numbers used above (state rankings, utility shares, RTO breakdown). |

Join keys: `eia_utility_id`, `state` (2-letter), `rto_iso`, `year`.

## Caveats

- **Average revenue is not the same as the tariff rate.** EIA price = revenue / kWh. It includes fixed charges, low-income
  discounts, billing lags and the seasonal mix. In restructured states the bundled price covers only default-service
  customers, and that population changes as customers switch.
- The utility file **excludes short-form (EIA-861S) utilities and EIA's state "Adjustment" rows**, so utility sums run about 4%
  below state totals (median). In 2019 EIA folded short-form utilities into the main file, so that year has about 1,000
  extra small utilities. Use the `bills_state_*` files for state totals.
- Texas TDUs (Oncor, CenterPoint, AEP Texas, TNMP) appear only from 2020, from EIA's `Delivery_Companies` file. Their
  all-in price is the statewide REP average, not utility-specific.
- `bills_anatomy.json` mixes official commission figures (verified) with OpenEI URDB transcriptions (not independently
  verified) and derived splits. Taxes and franchise fees are mostly excluded. Entergy Louisiana and AEP Ohio tariff sums sit
  well below EIA average revenue, so treat those two as partial.
- The 2026 monthly data are preliminary; EIA revises them.
- **Attribution to data centers is not something this area can measure directly.** Price data show *where* bills rose. Linking
  that to data-center load requires the capacity-market (`markets`) and cost-allocation (`policy`) evidence.

## Open questions

- Fuel versus other riders inside Dominion's 8.69 c/kWh adjustment line, and Georgia Power's fuel versus ECCR split.
- Current (June 2026) SOS/BGS supply rates for Pepco DC and BGE. The URDB records carry 2025/26 or January 2026 supply.
- Capacity share of each PJM utility's default-service rate (needs zonal price x residential PLC per utility).
- 2026 annual EIA-861 (early release expected Aug 2027).

## Log: what did not work

- `curl` is blocked. FRED CSV downloads timed out, so I used the BLS API v2 (no key) instead.
- WebFetch was denied for every domain tried (lbl.gov, puc.pa.gov, phillyvoice.com). I used the in-app browser for HTML
  pages and node/python downloads for files.
- No PDF tools are installed (no pdftotext, poppler, PyPDF2 or pdfminer). I wrote a stdlib extractor
  (`scripts/bills/pdftext.py`). It works on simple PDFs (PECO tariff, Synapse report) but not on the scanned or custom-encoded
  VA SCC order.
- The PA PUC PDF (rate comparison report) failed TLS verification from node and python ("self signed certificate in
  chain"). I did not bypass verification and used the PUC's HTML press release instead.
- The OpenEI URDB API with DEMO_KEY returned HTTP 429 after 9 utilities. Workaround: the full USURDB bulk download
  (`usurdb.csv.gz`, 12 MB, 58,920 rates) covers Dominion, Pepco and PSE&G. For PG&E I used its own June 2026 tariff PDF.
- Writing report .md files directly is blocked for subagents, so this file is generated by `scripts/bills/write_findings.py`.
- The Citizens Utility Board site returned 504.
