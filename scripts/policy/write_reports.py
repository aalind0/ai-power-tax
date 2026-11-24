"""Write research/policy/FINDINGS.md and research/policy/SOURCES.md.

The report text lives in this script because the research agent could not write .md files directly.
Run from ai-power-tax/:  python3 -I scripts/policy/write_reports.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTDIR = os.path.join(ROOT, 'research', 'policy')

FINDINGS = r'''# Policy area: who pays, state by state, and what a resident can do

Research date: 2026-11-23. Scope: large-load (data-center) tariffs, data-center tax incentives, 2025-26 legislation,
recent base-rate cases at large residential utilities, national rate-request totals, and a resident action guide.
Every number below has a citation; anything not checked against a live source this session is tagged UNVERIFIED.
Sources are listed in full in `SOURCES.md`.

## Outputs (for the website)

| File | What it holds | Rows |
|---|---|---|
| `data/processed/policy_states.json` | 50 states + DC: RTO, large-load tariff (status, utilities, key terms, year, source), data-center tax incentive (type, est. annual cost, 2026 status), 2025-26 bills/orders, PUC, consumer advocate, CBPP 2026 subsidy-bill outcome, notes, `verified` flag | 51 |
| `data/processed/policy_rate_cases.json` | `national_rate_requests` (PowerLines totals 2024 to Q3 2026) + `cases`: 37 recent electric base-rate cases at large residential utilities (docket, filed date, requested/approved $, ROE, residential impact, hearings, data-center mentions, status, links) | 37 cases |
| `data/processed/policy_rate_requests_powerlines.csv` | Every utility rate request listed in the PowerLines Q1-Q3 2026 appendices (state, utility, region, customers, electric/gas, month, $bn rounded to 0.1) | 193 |

Field notes:
- `large_load_tariff.status`: `adopted` = at least one large-load tariff, rule or commission-ordered rate schedule in force or ordered;
  `proposed` = filed, pending, or required by statute but not yet approved; `none` = none found in the EEI Oct 2026 list or other sources.
- `dc_tax_incentive.est_annual_cost_usd`: most recent figure found, with `cost_year` and `cost_basis`. Figures are not comparable across states
  (some state-only, some state + local, some projections). `null` = not disclosed or not found.
- `subsidy_restriction_bills_2026_cbpp`: CBPP map (as of July 2026): `passed` / `failed` / `active` / `none_reported`.
- `policy_rate_cases.json`: amounts are annual revenue-requirement changes from the EEI Rate Review workbook (S&P Global RRA data, as of 9/30/2026).
  EEI's status "Settled" means the case concluded (settled or decided). For multi-year plans the approved figure may be first year only.
  Decisions after 9/30/2026 (Duke NC, PSO, We Energies, TEP) come from news sources; their impacts are in `requested_pct_residential` where dollar totals were not available.
- Join key: `state` (2-letter). Utility names follow EEI; EIA utility ids are not attached yet (open item).

Scripts (run from `ai-power-tax/`): `node scripts/policy/fetch.mjs <folder> <url>` (downloads into data/raw/policy/<folder>/),
`python3 -I scripts/policy/pdf_text.py <pdf> <txt>` (PDF text), `python3 -I scripts/policy/parse_powerlines.py <txtdir> data/processed/policy_rate_requests_powerlines.csv`,
`python3 -I scripts/policy/build_policy_states.py`, `python3 -I scripts/policy/build_policy_rate_cases.py`, `node scripts/policy/check_urls.mjs` (link check),
`python3 -I scripts/policy/write_reports.py` (this file).

## Key findings

**1. Utilities asked for record rate increases, and regulators grant a bit more than half.**
Investor-owned electric and gas utilities requested nearly $31B in rate increases in 2025, more than double about $15B in 2024, touching 81M
people; the South accounted for $14.3B ([PowerLines 2025 review](https://powerlines.org/wp-content/uploads/2026/01/0126_PowerLines_Rising-Utility-Bills-Q4-Update-FINAL.pdf);
[E&E News](https://www.eenews.net/articles/utilities-sought-a-record-31b-in-rate-increases-last-year/)). Through Q3 2026 the total is $23.1B
($9.4B Q1, a record $9.2B Q2, $4.5B Q3) ([PowerLines Q3 2026](https://powerlines.org/utilities-request-23-1-billion-in-rate-increases-through-third-quarter-of-2026/)).
PowerLines says about 58% of requested dollars were approved over two years. Our own sample agrees: in the 15 concluded cases in
`policy_rate_cases.json` with both figures, regulators approved $5.57B of $9.54B requested (58%).
*Caveat:* PowerLines is a consumer-advocacy nonprofit; its totals mix electric and gas, base cases and riders, and count requests, not approvals.

**2. Large-load tariffs went from rare to normal in about 18 months.**
By our count 25 states have at least one adopted large-load tariff or commission-ordered data-center rate schedule, 9 more have one proposed or
required by statute, and 17 (mostly low-growth or public-power states) have none (`policy_states.json`, built largely from the
[EEI large-load list, Oct 9, 2026](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs), industry source).
Berkeley Lab finds the median eligibility threshold is 25 MW and the median minimum contract rose from 5 years (tariffs before 2025) to
12 years (since 2025) ([LBNL/Brattle, Aug 2026](https://eta-publications.lbl.gov/sites/default/files/2026-08/rate_designs_large_loads_2026.08.10.pdf)).
LBNL webinar slides cite SEPA data: 39 tariffs approved and 13 pending as of Aug 6, 2026 (search snippet; slides not opened).

**3. The strongest written protections are in Ohio, Virginia, Oregon, Michigan, Missouri, Wisconsin and Indiana.**
- Ohio (AEP Ohio Schedule DCT, July 2025): data centers >25 MW pay for at least 85% of contracted capacity for up to 4 ramp years + 8 years,
  post collateral of 50% of all minimum charges, and reimburse 100% of build-out if they cancel ([AEP Ohio](https://www.aepohio.com/company/about/rates/data-center-tariff)).
- Virginia: new GS-5 class for >=25 MW with a 14-year minimum term (SCC order Nov 25, 2025), and since July 31, 2026 a mandatory
  contribution-in-aid-of-construction for direct-connect substations and lines; a new allocator cut the typical residential transmission-rider
  increase from $2.90 to $0.94/month ([Utility Dive](https://www.utilitydive.com/news/dominion-energy-scc-transmission-costs-data-center/827693/)).
- Oregon: the POWER Act (HB 3546) requires a separate class for >20 MW; OPUC Order 26-154 makes large loads pay 100% of distribution upgrades
  ([OPUC](https://apps.puc.state.or.us/orders/2026ords/26-154.pdf)).
- Michigan (Consumers: >=100 MW, 15 years, proof before each connection) ([MPSC](https://www.michigan.gov/mpsc/commission/news-releases/2025/11/06/mpsc-approves-terms-of-service-between-consumers-energy-and-data-centers));
  Missouri SB 4 (12-year minimum; Ameren loads pay 100% of direct interconnection up front) ([MO PSC](https://psc.mo.gov/General/Utility_Tariffs_for_Large_Load_Customers));
  Wisconsin (We Energies VLC, 15 years) ([PSC WI](https://content.govdelivery.com/accounts/WIPSC/bulletins/4147a70));
  Indiana (I&M 12 years + ramp; NIPSCO GenCo ring-fences ~$7B of Amazon-funded generation) ([IURC order 46322](https://www.in.gov/iurc/files/ord_46322_061726.pdf)).

**4. Where costs still get spread to everyone: regional grids, direct connections and confidential contracts.**
State tariffs cannot touch costs set in regional markets. New Jersey's governor acknowledged data-center tariffs have limited effect because
capacity prices are set across PJM's 13 states ([NJ Monitor](https://newjerseymonitor.com/2026/07/07/sherrill-signs-three-bills-to-lower-nj-electricity-costs/)).
Union of Concerned Scientists counted $4.36B of 2024 PJM transmission projects built to connect individual data centers; over 95% were recovered
from all customers through formula rates ([UCS, Sept 2025](https://www.ucs.org/sites/default/files/2025-09/PJM%20Data%20Center%20Issue%20Brief%20-%20Sep%202025.pdf); advocacy; verified by the markets agent).
Maryland's People's Counsel filed a complaint over PJM regional transmission cost allocation on May 7, 2026
([OPC](https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf)).
Harvard's Electricity Law Initiative found confidential special contracts let costs shift to captive customers
([Harvard ELI, Mar 2025](https://eelp.law.harvard.edu/wp-content/uploads/2025/03/Harvard-ELI-Extracting-Profits-from-the-Public.pdf)); a Georgia PSC spokesperson said the PSC cannot review large-load contracts.
States with real data-center activity but no general large-load protection: Nevada (clean-supply tariff only), Mississippi (special contracts),
Tennessee (TVA, not state-regulated), Nebraska (public power).

**5. Data-center tax breaks are among the costliest state subsidies, and 2026 brought the first rollbacks.**
At least 10 states lose more than $100M a year ([Good Jobs First, Apr 2025](https://goodjobsfirst.org/cloudy-with-a-loss-of-spending-control-how-data-centers-are-endangering-state-budgets/), advocacy).
Largest figures found: Virginia about $1.6B (FY2025, per the Senate budget chair; JLARC put FY2023 at $928.6M), Ohio about $1.5B actual in 2025 against
$136M projected ([WOSU](https://www.wosu.org/2026-05-27/gov-dewine-freezes-controversial-data-center-tax-break-for-now)), Texas $1.02B (FY2025;
projected $1.7B in 2030), Illinois $371M (2023), Georgia $296M (FY2025). In 2026 at least 25 states introduced bills to curb these breaks and 8 passed
([CBPP](https://www.cbpp.org/blog/states-began-scaling-back-expensive-subsidies-for-data-centers-in-this-years-legislative)). Maine fully repealed (LD 713);
Arizona passed a 3-year moratorium; governors paused programs in Illinois, Ohio and Massachusetts; New Jersey paused its $500M AI credit; Pennsylvania attached
conditions by executive order; North Carolina repealed the electricity exemption ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/091126-where-states-stand-on-data-center-sales-tax-exemptions-ahead-of-us-midterms)).
Virginia kept its exemption but added a first-of-its-kind tax on data-center electricity use ([Bloomberg Law](https://news.bloomberglaw.com/environment-and-energy/virginia-lawmakers-approve-data-center-energy-tax-in-budget-deal)).
*Other side:* the Data Center Coalition argues the revenue "loss" assumes the projects would have been built anyway, and points to Colorado, which has no exemption and
little development (S&P). Tax breaks hit state budgets, not electricity bills directly.

**6. Two of the biggest markets paused new data centers in 2026.**
New York's governor signed the first state moratorium (July 14, 2026): no state environmental permits for new data centers of 50 MW or more for up to a year
([Utility Dive](https://www.utilitydive.com/news/behind-the-new-york-data-center-pause-is-legislation-that-could-impact-exis/826369/)).
Texas's governor ordered an audit of every data center in the ERCOT queue (about 474 GW of requests, roughly 90% data centers), and ERCOT delayed its first
large-load study batch ([Utility Dive](https://www.utilitydive.com/news/texas-hits-pause-data-center-interconnections/827046/)). Texas SB 6 (2025) already requires
loads of 75 MW or more to disclose backup generation, post financial security and accept curtailment in emergencies.

**7. Speculative forecasts are the core risk, and exit terms are the regulators' answer.**
Georgia's PSC certified about 10 GW for Georgia Power (Dec 2025); staff warned much of the forecast was speculative, and the utility backstops costs only through 2031
([AJC](https://www.ajc.com/business/2026/02/georgia-regulators-wont-revisit-approval-of-new-power-plants-for-data-centers)). Contracts now include exits:
Amazon can cut 1,200 MW from its NIPSCO deal by March 2029; Indiana requires commission approval for reductions over 20% at I&M; AEP Ohio lets customers reassign up to 25%.
Who pays if those exits are used is the question to watch.

**8. Regulators are trimming the 2026 wave, often while creating a data-center rate class in the same order.**
North Carolina cut Duke's residential ask from about 18% over two years to about 9.5% and ordered a data-center schedule for >50 MW
([Axios](https://www.axios.com/local/raleigh/2026/11/17/nc-regulators-approve-duke-energy-rate-increase)); Oklahoma approved 3.55% for PSO versus about 15% requested,
and created a large-load tariff ([report](https://gcn.com/?p=23300)); Wisconsin approved 3.9% and 3.5% versus 4.6% and 4.5% for We Energies
([Wisconsin Watch](https://wisconsinwatch.org/2026/11/wisconsin-we-energies-customers-another-rate-hike-but-smaller-public-service-commission-regulators-utility/)).
In 17 of our 37 cases the utility, regulator or intervenors explicitly tie the case to data-center load or tariffs (4 do not; 16 not checked).

**9. The industry case: big new customers can lower everyone's rates if they pay their way.**
Alliant says data-center growth supports a 5-year residential base-rate freeze in Iowa; AES Indiana claims $770M of savings over 15 years from its Google contract;
NIPSCO claims about $1B for existing customers; Georgia Power's base rates are frozen through 2028 (EEI list; all industry claims). An Amazon-funded E3 study found
Amazon facilities pay more than their incremental cost (verified by the markets agent). Berkeley Lab found states with the fastest load growth in 2019-2024 generally saw
real prices fall, with PJM the exception. *Caveat:* these benefits depend on the tariff terms in findings 3-4 holding, and none covers regional capacity-price effects.

**10. Politics moved fastest where bills rose fastest.**
Two challengers won Georgia PSC seats in Nov 2025 on affordability; governors in Pennsylvania, Ohio, Illinois, Massachusetts, Nebraska, New York and Texas acted by executive
order in 2026; 36 governors were on the Nov 2026 ballot (S&P). Michigan's attorney general called DTE's offer to pause rate cases if its data center comes online a "ransom note"
([Michigan AG](https://www.michigan.gov/ag/news/press-releases/2026/08/28/ag-nessel-seeks-to-slash-dtes-474-million-rate-hike-request-by-71)).

**11. Six states have no official residential utility advocate.**
Georgia, Idaho, Louisiana, North Dakota, South Dakota and Nebraska (public power) have no state-funded residential advocate for electricity
([NASUCA member list](https://www.nasuca.org/members/)); residents there rely on commission staff or nonprofits (e.g. Georgia Watch, Alliance for Affordable Energy).

**12. Proceedings still open where residents can weigh in (as of Nov 23, 2026).**
APS rate case (Arizona; Commission vote due by Dec 31, 2026), DTE Electric (Michigan; order expected ~late Feb 2027), Consumers Energy (Michigan), Ameren Missouri
(~+$13/month; decision ~May 2027), Puget Sound Energy (Washington; ~+17.75% residential proposed for 2027), JCP&L (New Jersey), BGE and Potomac Edison (Maryland),
Maryland large-load tariffs (PSC Case PC72), New Jersey BPU large-load rules (due by July 2027), Indiana Michigan Power, OG&E (Oklahoma), Portland General Electric (Oregon),
PG&E 2027 GRC (California), NYSEG (New York), CL&P (Connecticut), PECO (Pennsylvania).

## Which states shield residents best, and which spread costs (both sides)

Stronger on paper: OH, VA, OR, MI, MO, WI, IN, and now NC; TX for grid-reliability terms (SB 6). Common features: separate class or schedule, 12-15 year terms,
minimum-demand charges of 80-85%, collateral, exit fees, and direct assignment of connection costs.
Weaker or untested: states with no tariff and active data-center growth (NV, MS, NY before its moratorium, TN via TVA, NE via public power), states relying on confidential
special contracts (Georgia contracts, Louisiana's Meta deal), and every PJM state for regional transmission and capacity costs that state tariffs cannot reach.
Counterpoint: utilities and industry argue load growth spreads fixed costs and has kept rates flat in some places (Iowa, Georgia base rates, Indiana claims), and Berkeley Lab's
2019-2024 data mostly support that outside PJM. Whether it holds depends on whether the forecast load shows up and pays under these contracts.

## What you can do (plain-English guide)

1. **Find your case.** Look up your utility on your state commission's site (`puc.url` in `policy_states.json`) and search the docket number
   from `policy_rate_cases.json`, or call the commission's consumer line. Utilities also post a "rate case" page.
2. **File a public comment.** Anyone can, usually online, and it becomes part of the record. Say who you are, which case, how the increase affects you,
   and what you want (for example: "make data centers pay for the lines built for them"). Examples:
   Arizona ACC [e-docket](https://edocket.azcc.gov/) (APS, until the Dec 2026 vote),
   Missouri PSC [EFIS case 105725](https://efis.psc.mo.gov/Case/Display/105725) (Ameren Missouri),
   Washington UTC [docket 260005](https://www.utc.wa.gov/casedocket/2026/260005) (PSE),
   Michigan PSC [site](https://www.michigan.gov/mpsc) (DTE U-22046, Consumers U-22070),
   Virginia SCC [docket search](https://www.scc.virginia.gov/docketsearch) (each case page has a public-comment link).
3. **Speak at a public hearing.** Commissions hold evening "public witness" or "field" hearings in rate cases; dates are posted on the docket and in bill inserts.
   You can speak for a few minutes without a lawyer.
4. **Contact your consumer advocate.** They represent residential customers in major cases and use specific stories:
   e.g. Maryland [Office of People's Counsel](https://opc.maryland.gov/), Ohio [Consumers' Counsel](https://www.occ.ohio.gov/),
   Indiana [OUCC](https://www.in.gov/oucc/), New Jersey [Rate Counsel](https://www.nj.gov/rpa/), Pennsylvania [OCA](https://www.oca.pa.gov/),
   Texas [OPUC](https://www.opuc.texas.gov/), Illinois [CUB](https://www.citizensutilityboard.org/), Arizona [RUCO](https://ruco.az.gov/),
   Virginia [AG Division of Consumer Counsel](https://www.oag.state.va.us/). All states: [NASUCA members](https://www.nasuca.org/members/).
5. **Intervene (bigger step).** Becoming a formal party lets you file testimony and question witnesses. It needs a petition by an early deadline and often a lawyer;
   residents usually do this through a group (consumer, environmental, low-income or business associations).
6. **Ask about bill help now.** Utilities and states run low-income discounts, budget billing and LIHEAP; ask your utility or dial 211.
7. **Watch who decides.** Commissioners are appointed by governors in 36 states and elected in 10 (PowerLines Q3 2026). Large-load tariffs and data-center tax
   breaks are set by commissions and legislatures, which take public comment too.

## Caveats and open questions
- 20 of 51 state records are `verified: false` (AK, AR, CA, CT, DC, HI, ID, KS, KY, MS, ND, NH, NM, NV, RI, SC, SD, UT, VT, WV);
  their incentive and legislation fields are incomplete and tagged UNVERIFIED.
- Not confirmed against order or statute text: Virginia GS-5 minimum-demand split, Maryland and New Jersey statutory terms, Wisconsin VLC threshold
  (reports conflict: 500 MW proposal vs 100 MW final), Indiana HB 1007's reported 80% rule, Virginia's data-center energy-tax rate ($0.011/kWh reported). All tagged.
- Tax-incentive costs are not comparable (state-only vs state + local; projected vs actual) and many states disclose nothing (GJF: 12 of 32 programs; CBPP: at least 14 states).
  S&P lists Minnesota as a 2026 repeal; CBPP says Minnesota's 2026 bill failed (Minnesota repealed only the electricity exemption, in 2025). Our record follows CBPP and notes the conflict.
- Residential % impacts come from utilities, advocates or press and use different usage levels (500, 800, 1,000 kWh).
- AEP Ohio distribution case: EEI/RRA shows $320M authorized while EEI's own project list says the settlement lowers residential distribution charges ~$1.22/month; check the order.
- Not done: EIA utility ids on rate cases; per-state comment-portal URLs; Nebraska repeal bill number; PG&E 2027 GRC and Consumers U-22070 residential impacts;
  whether I&M Cause 46454 cites data centers.

## Log: what did not work
- `WebFetch` was refused for every domain tried (powerlines.org, utilitydive.com, eenews.net, aepohio.com, stateline.org); used the in-app browser (own tab) instead.
- No PDF tools installed (no pdftotext/poppler, PyPDF2, pdfminer) and `Read` cannot render PDFs. Wrote `scripts/policy/pdf_text.py` (zlib + ToUnicode CMaps + object streams).
  It loses some digits in the EEI and LBNL PDFs, so counts from those came from search snippets.
- PowerLines 2025 quarterly appendices use different layouts and were not parsed; only the Q1-Q3 2026 appendices are in the CSV
  (parsed totals: Q1 $9.3B of $9.4B, Q2 $8.7B of $9.2B, Q3 $4.5B of $4.5B; amounts rounded to $0.1B so small requests show as 0.0).
- `pandas.read_excel` needs `engine='openpyxl'` for .xlsx with this pandas/xlrd version.
- NARUC commission-list URLs returned 404; PUC/advocate URLs were checked with `check_urls.mjs` (21 of 96 returned HTTP 403 or certificate-chain errors to Node,
  typical of state sites blocking scripts; only the RI and AK advocate links were changed).
- WebSearch used: 38 of the ~40 budget.
'''

SOURCES = r'''# Policy area: sources

Access date for all items: 2026-11-23 unless noted. "Raw" = local copy under `data/raw/policy/`. Advocacy and industry sources are labelled.
Licence/terms: government documents are public records; news, think-tank and trade-association items are copyrighted and used for facts and short citations only.

## Datasets and reports downloaded

| Name | Publisher (type) | URL | Date | Granularity | Raw copy / notes |
|---|---|---|---|---|---|
| Rate Review 2026 Q3 workbook ("All Rate Cases" sheet) | Edison Electric Institute, data from S&P Global RRA (industry) | https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/Quarterly-Financial-Updates/2026_Q3_Rate_Review_XLSX.xlsx | as of 2026-09-30 | case-level: state, company, docket, case type, request/decision dates, $M, ROE | `eei_rate_review_2026q3/` (912 KB). Backbone of `policy_rate_cases.json`. EEI terms of use apply. |
| Large Load Projects and Tariffs | EEI (industry) | https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs | updated 2026-10-09 | state/utility tariff list + example projects | `eei_large_load_tariff_list/` (PDF). Main source for tariff status by state; industry framing. |
| Electricity Rate Designs for Large Loads: 2026 Update | Lawrence Berkeley National Lab & Brattle (government/consultant) | https://eta-publications.lbl.gov/sites/default/files/2026-08/rate_designs_large_loads_2026.08.10.pdf | Aug 2026 | tariff design elements across ~55 tariffs | `lbnl_large_load_rate_designs_2026/`. Median threshold 25 MW; median contract 5 -> 12 years. |
| Utility Bills Are Rising: Q1 2025, Q2 2025, Q3 2025, 2025 Review (Q4), Q1 2026, Q2 2026, Q3 2026 + Q4 2025 one-pager | PowerLines (consumer-advocacy nonprofit) | https://powerlines.org/reports/ (PDF links in `_fetch_log.json` of each folder) | Apr 2025 - Oct 2026 | national/regional totals; per-request appendices | `powerlines_q*_20*/` (1-33 MB each). 2026 appendices parsed to `policy_rate_requests_powerlines.csv`. |
| 2026 State Bills to Restrict Data Center Subsidies (map) | Center on Budget and Policy Priorities (progressive think tank) | https://www.cbpp.org/blog/states-began-scaling-back-expensive-subsidies-for-data-centers-in-this-years-legislative | 2026-08-07 | state: passed / failed / active | `cbpp_2026_dc_subsidy_map/` (PNG, read visually). |
| PUC / advocate link check | this project | `scripts/policy/check_urls.mjs` | 2026-11-23 | URL status codes | `url_check/url_check.json` |

## Web pages and documents read (not downloaded)

National / multi-state
- Good Jobs First, "Cloudy with a Loss of Spending Control" (Apr 2025; advocacy) - state cost table (TX $1.0156B FY25, VA $732.8M FY24 state-only, IL $370.6M 2023, GA $296M FY25, IA $151.1M 2020, NV $140.0M FY24, OH $127.4M, MN $114.2M, WA $112.1M, TN $103.6M) - https://goodjobsfirst.org/cloudy-with-a-loss-of-spending-control-how-data-centers-are-endangering-state-budgets/
- S&P Global, "Where states stand on data center sales tax exemptions ahead of US midterms" (2026-09-11) - https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/091126-where-states-stand-on-data-center-sales-tax-exemptions-ahead-of-us-midterms
- PowerLines Q3 2026 press release (2026-10-07) - https://powerlines.org/utilities-request-23-1-billion-in-rate-increases-through-third-quarter-of-2026/
- Utility Dive, "US electric, gas utility rate requests spike to $4.5B in Q3" (2026-10-09) - https://www.utilitydive.com/news/q3-electric-gas-rate-requests-powerlines-analysis/832609/
- E&E News, "Utilities sought a record $31B in rate increases last year" (2026-01-29) - https://www.eenews.net/articles/utilities-sought-a-record-31b-in-rate-increases-last-year/
- NASUCA member directory (consumer advocates by state) - https://www.nasuca.org/members/
- Cited via the markets area (verified there, same session): UCS PJM connection-costs brief (Sept 2025, advocacy) https://www.ucs.org/sites/default/files/2025-09/PJM%20Data%20Center%20Issue%20Brief%20-%20Sep%202025.pdf ;
  Harvard ELI "Extracting Profits from the Public" (Mar 2025, academic) https://eelp.law.harvard.edu/wp-content/uploads/2025/03/Harvard-ELI-Extracting-Profits-from-the-Public.pdf ;
  E3/Amazon "Tailored for Scale" (Dec 2025, industry-funded) https://www.ethree.com/wp-content/uploads/2025/12/RatepayerStudy.pdf ;
  LBNL/Brattle retail price drivers (Jan 2026) https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf

State primary and secondary sources
- Ohio: AEP Ohio Data Center Tariff page (terms, PUCO order 7/9/2025) https://www.aepohio.com/company/about/rates/data-center-tariff ; WOSU on DeWine pause and $1.4B underestimate (2026-05-27) https://www.wosu.org/2026-05-27/gov-dewine-freezes-controversial-data-center-tax-break-for-now
- Virginia: SCC final order PUR-2025-00058 (2025-11-25) https://npr.brightspotcdn.com/b6/ac/706130b64d2b8eee6a9832b97e48/20251125-virginiascc-dominionenergyruling.pdf ; Utility Dive on SCC Rider T-1 order (2026-08-12) https://www.utilitydive.com/news/dominion-energy-scc-transmission-costs-data-center/827693/ ; Virginia Mercury via Patch, 2026 session bills (2026-03-17) https://patch.com/virginia/across-va/data-center-bills-dominated-years-general-assembly-heres-what-passed ; Bloomberg Law on HB 30 energy tax (2026-06-22) https://news.bloomberglaw.com/environment-and-energy/virginia-lawmakers-approve-data-center-energy-tax-in-budget-deal ; Cardinal News on base-rate impact https://cardinalnews.org/2025/11/26/regulators-approve-dominion-energy-rate-increase/
- Maryland: PSC PC72 notice https://www.psc.state.md.us/wp-content/uploads/Notice_LargeLoadCust-PC72.pdf ; HB 1532 (Ch. 353, 2026) https://mgaleg.maryland.gov/2026RS/Chapters_noln/CH_353_hb1532e.pdf ; SB 937 (Ch. 625, 2025) https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_625_sb0937e.pdf ; OPC RTEP complaint (2026-05-07) https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf (search snippets; documents not opened)
- Pennsylvania: PUC final order on model large-load tariff (2026-05-13) https://www.puc.pa.gov/press-release/2026/puc-releases-final-order-establishing-first-of-its-kind-large-load-model-tariff-framework-05132026 (search snippet)
- New Jersey: Governor's office (2026-07-07) https://www.nj.gov/governor/news/2026/20260707a.shtml ; New Jersey Monitor https://newjerseymonitor.com/2026/07/07/sherrill-signs-three-bills-to-lower-nj-electricity-costs/ (search snippets)
- Illinois: CBS Chicago on Pritzker pause https://www.cbsnews.com/chicago/news/gov-jb-pritzker-suspends-data-center-tax-breaks/ (search snippet)
- Indiana: IURC orders 46322/46362 (2026-06-17) https://www.in.gov/iurc/files/ord_46322_061726.pdf ; 46183 (2025-09-24) https://www.in.gov/iurc/files/ord_46183_092425.pdf ; I&M settlement coverage https://www.utilitydive.com/news/indiana-iurc-large-load-interconnection-data-center-aep-amazon-google/740452/ ; IURC hearing lists (Oct 2026) (search snippets)
- Georgia: PSC data-center rule advisory (2025-01-23) https://psc.ga.gov/site/assets/files/8617/media_advisory_data_centers_rule_1-23-2025.pdf ; AJC (2026-02) https://www.ajc.com/business/2026/02/georgia-regulators-wont-revisit-approval-of-new-power-plants-for-data-centers ; PSC storm/fuel stipulation advisory (2026-05-28) https://psc.ga.gov/site/assets/files/9488/media_advisory_5_28_26_fuel_storm_stip_approval.pdf ; Inside Climate News on Helene costs https://insideclimatenews.org/news/26022026/hurricane-helene-recovery-georgia-power-bills/
- Texas: Utility Dive on Abbott audit (2026-08-05) https://www.utilitydive.com/news/texas-hits-pause-data-center-interconnections/827046/ ; White & Case on PUCT rule (search snippet) https://www.whitecase.com/insight-alert/puct-sets-financial-commitments-data-center-interconnection-governor-pauses-permit
- Oregon: OPUC Order 26-154 https://apps.puc.state.or.us/orders/2026ords/26-154.pdf (search snippet)
- New York: Utility Dive on Hochul EO and A11560 (2026-07-28) https://www.utilitydive.com/news/behind-the-new-york-data-center-pause-is-legislation-that-could-impact-exis/826369/
- North Carolina: Axios Raleigh on NCUC Duke order (2026-11-17) https://www.axios.com/local/raleigh/2026/11/17/nc-regulators-approve-duke-energy-rate-increase
- Arizona: ACC "What's next in the APS rate case" (2026-07-10) https://azcc.gov/news/home/2026/07/10/what-s-next-in-the-aps-rate-case ; KOLD on TEP decision https://kold.com/2026/11/18/tep-customers-pay-more-after-acc-approves-rate-increase
- Michigan: MPSC Consumers data-center tariff (2025-11-06) https://www.michigan.gov/mpsc/commission/news-releases/2025/11/06/mpsc-approves-terms-of-service-between-consumers-energy-and-data-centers ; MPSC DTE order (2026-02-19) https://www.michigan.gov/mpsc/commission/news-releases/2026/02/19/commission-approves-additional-242m-for-dte-electric-grid-upgrades ; AG Nessel on U-22046 (2026-08-28) https://www.michigan.gov/ag/news/press-releases/2026/08/28/ag-nessel-seeks-to-slash-dtes-474-million-rate-hike-request-by-71
- Missouri: PSC large-load tariff page https://psc.mo.gov/General/Utility_Tariffs_for_Large_Load_Customers ; Ameren release (2026-06-26) https://ameren.mediaroom.com/2026-06-26-Storm-hardening,-electric-grid-upgrades-and-new-generation-underpin-request-to-update-electric-rates-in-mid-2027
- Wisconsin: PSC release on We Energies VLC (2026-04-24) https://content.govdelivery.com/accounts/WIPSC/bulletins/4147a70 ; Wisconsin Watch on 5-UR-112 (2026-11) https://wisconsinwatch.org/2026/11/wisconsin-we-energies-customers-another-rate-hike-but-smaller-public-service-commission-regulators-utility/
- Oklahoma: PSO order coverage (2026-11) https://gcn.com/?p=23300 (search snippet)
- Washington: PSE 2026 GRC page https://www.pse.com/en/pages/rates/pending-utc-filings/2026-general-rate-case (search snippet)
- Louisiana: Louisiana Illuminator on LPSC Meta approval (2025-08-20) https://lailluminator.com/2025/08/20/entergy-meta/ (search snippet)
- Maine / Nebraska: Brownstein data-center tracker https://www.bhfs.com/data-center-tracker/maine/ (search snippet)
- Minnesota: EY tax alert on HF 9 (2025-06-24) https://taxnews.ey.com/news/2025-1349 ; HF 5125 (2026) https://www.revisor.mn.gov/bills/94/2026/0/HF/5125/

## Verification levels
- Opened and read in a browser this session: AEP Ohio tariff page; NASUCA members; GJF report; CBPP blog + map; S&P article; Utility Dive (Q3 PowerLines, Dominion Rider T-1, Texas pause, NY pause);
  PowerLines reports page and Q3 press release; E&E News; Patch/Virginia Mercury; Bloomberg Law (lede only); Axios NC; ACC APS page; WOSU; RI PUC site.
- Downloaded and parsed: EEI workbook, EEI large-load list, LBNL brief, PowerLines PDFs, CBPP map.
- Search-snippet only (marked as such above): treat as secondary until the primary document is opened.
'''

os.makedirs(OUTDIR, exist_ok=True)
for name, text in (('FINDINGS.md', FINDINGS), ('SOURCES.md', SOURCES)):
    with open(os.path.join(OUTDIR, name), 'w', encoding='utf-8') as f:
        f.write(text)
    print('wrote', os.path.join(OUTDIR, name), len(text), 'chars')
