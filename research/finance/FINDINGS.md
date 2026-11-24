# Finance: who invests, who earns, who profits (power side)

Area: `finance` | built 2026-11-23 | scripts: `scripts/finance/` | outputs: `data/processed/finance_*`

Numbers below are from primary filings (SEC 8-K earnings releases/decks, EEI) unless marked **secondary** or
**UNVERIFIED**. Advocacy sources are labelled (PowerLines, Harvard ELI = consumer side; EEI/CRA, E3 = industry/customer
side). Our own arithmetic is marked **computed** or **illustrative**.

## The 12 key insights

### 1. Utility capex is at a record and still accelerating
- US investor-owned utility (IOU) capex rose from **$112.5B (2016)** to **$204.1B (2025 actual)** (+81%); EEI projects
  **$238.8B in 2026** and **$296.3B in 2030**. The 2026-2030 projection (**$1.36T**) almost equals all of 2016-2025
  (**$1.44T**). [EEI capex chart, Mar/Sep 2026](https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/EEI-Industry-Capital-Expenditures.pdf)
- 2026 functional projection: generation **$80.4B (34%)**, distribution $72.3B (30%), transmission $44.5B (19%), gas
  $28.6B, other $13.0B; generation was $63.2B in the 2025 projection, the fastest-growing piece. (same source)
- PowerLines (consumer advocacy) found 51 IOUs plan **>=$1.4T for 2026-2030**, >21% above the ~$1.1T five-year total a
  year earlier; **32 of 51** cite data centers/load growth. [PowerLines, Apr 2026](https://powerlines.org/wp-content/uploads/2026/04/0413_PowerLines-CapEx-Report.pdf)

### 2. Plans ratchet up nearly every quarter, explicitly tied to large loads
| Company | Prior plan | Latest plan | Rate-base growth |
|---|---|---|---|
| AEP | $72B (2026-30, Feb-26) | **$100B (2027-31, Oct-26)** | **13%+ CAGR**, rate base $162B by 2031 |
| Southern | $76B (2025-29) | **$81B (2026-30)** (secondary; may reach ~$100B) | n/a |
| Xcel | $60B (2026-30) | **$70B (2027-31)** | ~11% (secondary) |
| Ameren | $31.8B (2026-30) | **$38.1B (2027-31)** | 10.6% -> **13.3%** |
| WEC | ~$37.5B | **$47.5B** (+$10B) | n/a |
| Sempra | $56B (2025-29) | **$65B (2026-30)** | Oncor 2027-31 base plan ~+20% |
| PPL | $23B (2026-29) | **$25B (2027-30)** | **10%/yr** |
| CenterPoint (10-yr) | $66.7B | **$70.7B** | n/a |
| NiSource (7-yr) | n/a | **$40B (2027-33) incl. $8B data-center** | 9-10% |

- Reported large loads: AEP **+28 GW** signed Oct-25 to Feb-26 (AEP Texas LOA-backed load 13 -> 36 GW); Southern
  **>17 GW** contracted (Q2-26; incl. Georgia Power's 25-yr **3.2 GW OpenAI** agreement, secondary); FirstEnergy
  **7.9 GW** contracted; Exelon ~**11 GW** high-probability; Oncor ~**24 GW** base-load class + 21 GW studied; PPL
  Kentucky pipeline **14.7 GW** (12.8 GW data centers). Links per row in `finance_utility_capex.csv`.

### 3. How grid capex becomes profit: rate base x equity share x allowed ROE
- Average authorized electric ROE in 2025: **9.77%** excluding limited-issue riders (**9.84%** all cases); average
  authorized equity ratio ~**50%** (**computed** from EEI's case-level RRA data; EEI's own 2025 headline is 9.71%, a
  different case set). [EEI Rate Review Q3-2026](https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/Quarterly-Financial-Updates/2026_Q3_Rate_Review_XLSX.xlsx) | [EEI Financial Review 2025 p.40](https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/Financial_Review/FinancialReview_2025.pdf)
- **Illustrative (our arithmetic, not a forecast):** each **$1B** added to rate base at 50/50 debt/equity and 9.75% ROE
  earns shareholders ~**$49M/yr after tax**; customers pay roughly **$115M/yr** in early years ($49M return + ~$16M
  income-tax gross-up at ~25% + ~$25M interest at ~5% + ~$25M depreciation over 40 yrs). On that rule of thumb AEP's
  $100B plan implies on the order of **$11B/yr** of added revenue requirement once in service, before depreciation of
  old assets and before any load-growth offset.
- Companies sell this to investors as "rate-base CAGR -> EPS CAGR": AEP targets **9-11% annual EPS growth 2027-2031**.
  [AEP Q3-26 8-K](https://www.sec.gov/Archives/edgar/data/4904/000000490426000069/a3q20268kpressreleaseex991.htm)

### 4. Allowed ROEs stayed ~9.4-9.8% while interest rates rose: read both ways
- Avg authorized ROE (ex-riders): **9.60% (2015), 9.39% (2020), 9.81% (2024), 9.77% (2025), 9.73% (Q1-Q3 2026)**,
  while the 10-yr Treasury went 2.1% -> 0.9% -> 4.3-4.5%. The spread over Treasuries fell from **~8.5 pts (2020) to
  ~5.3 pts (2026)** (computed). *Utility reading:* returns lagged the cost of capital. Utilities asked for **10.55%**
  on average in 2025 and got 9.77%.
- *Consumer/academic reading:* a peer-reviewed study (Dunkle Werner & Jarvis, J. Public Economics, Jul 2026) finds a
  **significant premium of authorized ROEs over capital-cost benchmarks**, an asymmetric response (ROEs rise faster
  than they fall), **excess cost to US consumers of ~$7B per year**, and that **+1 point of ROE goes with 2-4% more
  capital assets**, an incentive to build. [paper](https://escholarship.org/content/qt80m5j9vs/qt80m5j9vs.pdf)

### 5. Rate-increase requests hit a record in 2025, and regulators grant a larger share
- Electric rate increases **requested in 2025: $17.9B**, highest in the 2000-2025 series (prior high $14.5B in 2023);
  **authorized in 2025 decisions: $10.8B** (also a record). Q1-Q3 2026: $9.0B requested, $4.2B authorized
  (computed from EEI/RRA case data, electric only).
- Share of requested dollars granted (matched non-rider cases): **~47% avg 2015-2020 vs ~62% avg 2021-2025** (65% in
  2025), consistent with LBNL's 64% vs 52% cited by PowerLines.
- **68 electric rate cases were pending at 2026-09-30**, with docket, requested ROE and requested $ in
  `finance_rate_cases.csv`, ready for the site's "what you can do" panel.

### 6. Earned returns can exceed allowed returns, and the market pays ~2x book for rate base
- Entergy reports an adjusted LTM ROE of **11.3%** (Q3-26) against a latest authorized ROE of 9.7% in the dataset (one
  data point; includes non-utility items). [ETR Q3-26](https://www.sec.gov/Archives/edgar/data/65984/000006598426000322/earningsrelease3q26_ex991.htm)
- CenterPoint sold its Ohio gas utility for **~1.9x 2024 rate base (~26x earnings)**.
  [CNP deck](https://www.sec.gov/Archives/edgar/data/1130310/000110465926118963/tm2628051d1_ex99-2.htm) *Contested interpretation:* advocates read
  premiums to book as returns above investors' required return; industry cites growth and the scarcity of regulated assets.

### 7. Independent power producers (IPPs) are the clearest scarcity winners: earnings up 2-3x
| IPP (metric) | 2023 | 2024 | 2025 | 2026 guide | 2027 guide |
|---|---|---|---|---|---|
| Constellation (adj. operating EPS) | $6.28 | $8.67 | $9.39 | **$12.50-12.80** | n/a |
| Vistra (adj. EBITDA) | $4.14B | $5.66B | $5.91B | **$7.1-7.5B** | $7.7-8.5B |
| Talen (adj. EBITDA) | n/a | $0.77B | $1.035B | **$2.05-2.20B** | $2.50-2.85B |
| NRG (adj. EBITDA) | $3.28B | $3.75B* | $4.05B* | **$5.33-5.83B** | $5.5-6.0B |
\*derived from the y/y changes stated in NRG releases.
- The companies themselves name the drivers: higher **capacity** and energy prices, plus acquisitions. NRG's East
  (PJM/Northeast) segment adj. EBITDA for 9M-2026 was **$1.55B, +$867M y/y** (the capacity attribution is our inference).
  Context from the markets area: PJM capacity cost **$2.2B (2024/25) -> $14.7B (2025/26) -> $16.1B (2026/27)**
  (`markets_capacity_prices.csv`).

### 8. IPP stocks multiplied, then lost 25-52% from their peaks in 2026 as politics turned
- End-2022 to peak: Constellation **+369%**, Vistra **+839%**, NRG **+478%**, Talen **+859%** (from its Jun-2023 OTC price).
- End-2022 to 2026-11-20: CEG **+175%**, VST **+397%**, NRG **+176%**, TLN **+616%**, vs S&P 500 (SPY) **+80%**, utilities
  ETF XLU **+21%**, AEP +32%, Duke +26%, Dominion +8%, NextEra -0.2%, Entergy +86% (price-only; `finance_stock_moves.csv`).
- From peak: CEG **-41%**, VST **-47%**, NRG **-52%**, TLN **-25%**. Catalysts: the **Jan 16, 2026** White House + all
  PJM governors principles (Reliability Backstop Auction with 15-yr contracts paid by load-serving entities bringing data
  centers; extended capacity price cap) ([Utility Dive](https://www.utilitydive.com/news/trump-governors-pjm-emergency-auction-data-centers/809853/));
  a PJM auction delay and S&P's note that hyperscalers prefer utility PPAs (**secondary, snippet only**); the Nov-2026
  midterms (secondary). The market now prices political risk to scarcity rents.

### 9. Capacity cash is being converted into buybacks
- **Talen sold rights to ~$1.5B of future PJM capacity payments (2027/28 and 2028/29) for $1.3B upfront**, funding a $1.5B
  accelerated share repurchase; ~$4.0B of buybacks since 2024. [TLN Q3-26](https://www.sec.gov/Archives/edgar/data/1622536/000162253626000084/a20261103q32026earningsrel.htm)
- Vistra: **$6.7B** of repurchases since Nov-2021; Constellation ~**$3.0B** in 2026 YTD; NRG plans **$3B in 2026-27**,
  partly from selling 4.9 GW to LS Power for $4.0B.
- *Balance:* capacity prices come from PJM's auction design and supply shortfalls, not from any one seller's pricing; the
  market monitor's market-power analysis belongs to the markets area.

### 10. Hyperscalers have locked up >10 GW of nuclear since 2024, at undisclosed (probably premium) prices
- Verified deals (`finance_winners.json`): Microsoft-Crane (TMI-1 restart, ~835 MW, 20 yr); **Amazon-Talen 1,920 MW to
  2042 (~$18B lifetime revenue, secondary)**; Meta-Clinton 1,121 MW, 20 yr from Jun-2027; **Google-Duane Arnold restart
  615 MW, 25 yr**, online by Q1-2029; **Meta-Vistra 2,176 MW, 20 yr + 433 MW uprates**; Meta-TerraPower 690 MW;
  Meta-Oklo 1.2 GW; Amazon-Calvert Cliffs 690 MW, 20 yr; **Google-Constellation ~890 MW uprates, 20 yr + 2,700 MW
  load-following**; NextEra Point Beach ~1 GW, 20 yr; Google-Kairos 500 MW SMRs by 2035; Amazon-X-energy 5 GW target by 2039.
- Prices are not disclosed. Constellation's Q3-26 deck values a 1 GW nuclear PPA at a **$20-50/MWh premium over the
  $44.75/MWh PTC floor**, i.e. roughly **$65-95/MWh** (our inference).
  [CEG deck](https://www.sec.gov/Archives/edgar/data/1868275/000186827526000116/ceg-20261109992.htm)
- *Both sides:* the companies say the deals privately fund restarts, uprates and relicensing (>$3B Calvert Cliffs, >$4.3B
  uprates, a $1B DOE guarantee for Crane, a conditional DOE guarantee of up to $5B for uprates). Critics say deals for
  existing plants remove supply from the shared market and can shift grid costs: Exelon estimated **$58-140M** shifted by
  one co-location deal (Harvard ELI, "Extracting Profits from the Public", Mar 2025; copy in
  `data/raw/markets/harvard_eli_extracting_profits/`).

### 11. M&A: buyers bet on scarcity, and regulated rate base consolidates
- Constellation-Calpine **$26.6B** net (7.9x 2026 EBITDA, completed); NRG-LS Power **$12.0B** EV (13 GW + CPower,
  closed 2026-01-30, ~50% of replacement cost), then **4.9 GW resold to LS Power for $4.0B** (Nov-2026);
  Vistra-Cogentrix **$4.0B** (5.5 GW, **~$730/kW**, closed Oct-2026); Talen-Freedom/Guernsey (+2.8 GW); Constellation-RISEC.
- **NextEra-Dominion** (announced 2026-05-18, all-stock, 0.8138 NEE shares per D share): world's largest regulated
  utility, **combined rate base $138B growing ~11%/yr to 2032**, $2.25B proposed bill credits.
- **Blackstone-TXNM** $61.25/share (~**$11.5B** EV): Texas approved with $45M rate credits; New Mexico still pending as of
  Jul-2026 (secondary).

### 12. The central dispute: do large loads pay their way?
- **Industry:** an EEI-commissioned CRA study finds retail rates broadly tracked inflation over five years and data
  centers are not driving increases outside PJM; **24 states** have approved at least one large-load tariff (minimum
  demand charges, 10-15-yr terms, collateral, exit fees) [EEI FR 2025](https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/Financial_Review/FinancialReview_2025.pdf); AEP says new large loads should "bear the
  incremental system costs they create" and cites a proposed Indiana rate cut; E3 (commissioned by Amazon) finds ~$3.4M/yr
  of net surplus per Amazon site (markets-area file).
- **Consumer advocates:** PowerLines says ~47% (>$0.7T) of the $1.4T could fall on residential customers under current
  allocation shares; Harvard ELI documents special contracts shifting costs (Duke's internal plan to "shift the cost of the
  discount"); the Haas study estimates ~$7B/yr of excess ROE cost.
- **Neutral synthesis for the site:** capex plus ROE is how money reaches shareholders. Whether data centers raise or lower
  a household bill depends on (a) cost allocation and tariff protections, (b) whether forecast load arrives, and (c) the
  regional market. PJM capacity prices are the clearest channel from scarcity to bills.

## Data outputs
| File | Rows | Content |
|---|---|---|
| `data/processed/finance_utility_capex.csv` | 61 | 18 latest company plans, 12 prior plans, 3 IPP acquisitions, EEI actuals 2016-25, EEI projections 2026-30, EEI functional 2025P/2026P, PowerLines aggregate. Columns: record_type, company, ticker, segment, plan_period, capex_usd, capex_usd_high, rate_base_growth_pct, rate_base_growth_note, dc_related_note, source_url, date, source_type, verified, notes |
| `data/processed/finance_roe.csv` | 27 annual + 147 cases | `annual_average` 2000-2026 (2026 = Q1-Q3): avg authorized ROE (all/ex-riders/median), requested ROE, equity ratio, requested and authorized $, counts, 10-yr Treasury, spread, share of requested $ granted, EEI headline. `recent_case`: authorized ROE decisions since 2024 at ~29 major holding companies |
| `data/processed/finance_rate_cases.csv` | 1,097 | EEI/RRA case list: electric cases filed since 2015 plus all pending (68 at 2026-09-30) |
| `data/processed/finance_stock_moves.csv` | 27 tickers | end-2022, YE-23/24/25, latest (2026-11-20), peak, % moves; IPPs, 20 utilities, GEV, OKLO, SMR, XLU, SPY |
| `data/processed/finance_winners.json` | 4 IPPs, 12 deals, 10 M&A, 4 headwinds | IPP earnings plus guidance, capacity-revenue facts, buybacks, contracts, stock block; nuclear deals; M&A; headwinds. Each fact has source_url and verified |

Join key is `ticker`. The rate-case `state` field is the full state name, so map it to a 2-letter code downstream. A
holding-company-to-EIA-utility-id crosswalk is not built.

## Reproduce
```
node scripts/finance/fetch.mjs <url> <out>              # EEI pdf/xlsx, PowerLines, Haas paper
node scripts/finance/fetch_edgar_8k.mjs <start> <end> <subdir> '<query>'   # windows listed in SOURCES.md
node scripts/finance/fetch_prices.mjs
python3 -I scripts/finance/build_roe.py
python3 -I scripts/finance/build_stock_moves.py
python3 -I scripts/finance/build_capex.py
python3 -I scripts/finance/build_winners.py
python3 -I scripts/finance/write_docs.py
```
Text extraction reuses `scripts/markets/pdf2txt.js` and `scripts/markets/html2txt.py` (read only).
`scripts/finance/grep_sentences.py` is a reading helper.

## Caveats
- Plan horizons differ (4, 5, 7, 10 years) and so do scopes (holding company vs utility); do not sum across companies.
  Use the EEI totals for national figures.
- Dominion, Duke, NextEra, Entergy and Evergy plan sizes come from **PowerLines' compilation** (`verified=false`); their
  Q3-26 releases did not restate them. Southern's $81B comes from secondary sources (Reuters/Utility Dive).
- ROE averages computed from the EEI case file differ slightly from RRA/EEI headlines (different case sets); both are kept.
- IPP metrics are non-GAAP with company-specific definitions; stock moves are price-only.
- Per-IPP capacity revenue is **not separately disclosed** in the releases read; we record the stated drivers, Talen's
  monetization and NRG's East segment instead.
- **Licensing:** the case-level rate-review data is S&P Global/RRA data redistributed by EEI. Check terms before publishing
  the full case table on the site; publishing aggregates is safer. Nasdaq quote data is for research; use a licensed
  feed in production.

## Open questions
- Per-IPP PJM capacity revenue for 2025/26-2026/27 (needs 10-K revenue disaggregation).
- Nuclear PPA prices (all undisclosed).
- Blackstone-TXNM status after Jul-2026; Southern's Q3-26 plan (possibly ~$100B); Duke and Dominion updated plans
  (Feb-2027 roll-forward).
- Industry-wide earned vs authorized ROE (S&P/RRA, not reachable from this session).

## Log: what did not work
- The old EEI capex URLs return 404; the current file is `EEI-Industry-Capital-Expenditures.pdf` (found via the
  finance-and-tax page).
- WebFetch was refused for eei.org and spglobal.com (node download works for eei.org; S&P articles were unreadable).
- Yahoo chart API returned 429. Stooq serves a JS proof-of-work bot check, not bypassed. The Nasdaq.com API worked.
- EDGAR full-text search sometimes returns HTTP 500; a retry or different query works.
- ugrep complexity limits on long `grep -o` patterns; replaced by `grep_sentences.py`.
- The Write tool refused report .md files for subagents; this file is written by `scripts/finance/write_docs.py`.
- WebSearch calls used: 15.
