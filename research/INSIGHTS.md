# AI Power Tax: what the research says

Synthesis of the eight research areas (bills, markets, grid, load, policy, finance, households, geo), 2026-11-23.
Every number is in the area FINDINGS.md files with its source link. ⚠️ marks figures the agents could only partly verify.

## The story in one line
**Across the US, electricity is about flat after inflation over the last decade. Where data centers cluster, and
above all inside the PJM grid, bills are now jumping, and households are paying for capacity and power lines built
largely for data-center load.** Elsewhere the evidence is mixed, and fast load growth has often lowered rates.

## 1. Your bill: national calm, regional shock
- US residential price in 2025: **17.24¢/kWh**, only **+0.3% above 2015 after inflation** (bills).
- The last 12 months (to Aug 2026): **+6.5%**, against **3.4% inflation**.
- **23.7% of utilities are up 10% or more** in 2026, against 11.4% in 2025.
- PJM utilities rose **+10.4% in 2025**, against **+5%** for utilities outside any regional grid market.
- Jan–Aug 2026: Dominion **+20%**, BGE **+16%**, PG&E **−11%**.
- Real change 2020–2025: DC **+40%**, Maine **+32%**, while **22 of 51** jurisdictions fell.

## 2. What's inside the bill, and which part rose
- **Capacity** (PJM's charge for reserve power) went from **0.36¢ to about 1.96¢/kWh** between 2024 and 2026. That's about **$20/month** on a 1,000 kWh bill, hitting each **June 1** (bills, markets).
- **Transmission**'s slice of the average US price went from **0.93¢ (2013) to 1.89¢/kWh (2025)**. Utility spending on transmission and distribution (T&D) rose from **$18.5B to $100.1B**, 3.3× after inflation (grid).
- PJM transmission rates are **2.2× their 2015 level** in the median zone, **3.4× at AEP** and **2.0× at Dominion**.
- PJM wholesale cost rose **+$32.42/MWh** (Jan–Sep 2026 against 2025): **energy 69%**, capacity 27%, transmission 3%.
- Fuel and riders are **52%** of a Dominion bill.

## 3. How much is data centers?
- **Load today:** 192 TWh, **4.7%** of US electricity (2024), projected at **11.8%** by 2030 (LBNL). Virginia: **~26–28%** of Dominion's sales. Virginia and Texas account for **46%** of US commercial sales growth 2019–25. NOVEC's sales rose **+150%** (load).
- **Capacity:** the PJM market monitor attributes **$29.4B** across four auctions to data-center load ($9.33B, $7.27B, $6.50B, $6.27B). Its words: "**no shortfall but for the forecast data center load**." The price went from $28.92 to $325–333/MW-day, the cap. Uncapped, 2028/29 would have been $554.72 (markets).
- **Transmission:** **$4.36B** of 2024 single-data-center hookups in PJM states, **>95% socialized** (UCS). About **$23B** of PJM regional lines are mainly data-center driven per PJM's own reports. Maryland's share is **$2.0B**, about **$345 per household** over 10 years (grid, markets).

## 4. The other side (what the site must show)
- **LBNL/Brattle:** the fastest-load-growth states mostly saw *real price declines* in 2019–24. Extra load spreads fixed costs.
- **E3** (funded by data-center groups): load growth explains only **~50%** of PJM's capacity jump; market design and retirements explain the rest.
- Part of the jump is a **rebound from abnormally low** 2022–24 capacity prices. Per MWh, capacity cost is about **1.5×** its 2015–18 level, not 5–9×.
- **CRA/EEI:** no data-center-driven rate increases outside PJM. **Georgia** froze base rates through 2028. Virginia's **JLARC** found **no historic cost shift** yet.
- **Synthesis: both can be true.** With spare capacity and a cost-covering tariff, data centers can lower rates. With scarce supply in a uniform-price market (PJM) and socialized transmission, households pay.

## 5. Who pays, who gains
- **Rate requests:** about **$31B** across gas and electric utilities in 2025 (PowerLines, double 2024) and **$23.1B** through Q3 2026. Electric requests alone hit a record **$17.9B** in 2025 (S&P via EEI). Regulators grant about **58–62%** of requested dollars, up from ~47% in 2015–20 (policy, finance).
- **Utility capex:** EEI projects **$1.36T** for 2026–30, almost as much as the whole previous decade. AEP raised its plan from **$72B to $100B** in one year. Excess allowed returns cost customers about **$7B a year** (peer-reviewed 2026 study) (finance).
- **Winners:** Constellation's earnings per share roughly doubled from 2023 to 2026 guidance. Vistra and Talen stocks rose **~840–860%** to their peaks before falling 25–52% in 2026. Talen sold about $1.5B of future PJM capacity payments to fund buybacks ⚠️.
- **Tax breaks:** Virginia about **$1.6B a year**. Ohio about **$1.5B, against $136M projected**. Texas **$1.02B**. In 2026, 8 of at least 25 states curbed their breaks, and **Maine repealed** its break.
- **Protections:** **25 states** have adopted large-load tariffs; minimum contract terms rose from 5 to **12 years**. But **state tariffs can't reach PJM regional capacity and transmission costs**, and that gap is where households are exposed.

## 6. Who hurts
- **Energy burden:** households below 30% of area median income spend **16%** of income on energy, against **1.4%** above 150%. County-level data covers 3,222 counties.
- **Shutoffs:** **13.4M** electric shutoffs in 2024 (first federal count). Dominion Virginia ran **15.5 per 100 customers**, about 2.5× the investor-owned-utility average.
- **Debt:** about **1 in 6** households is behind on bills; arrears total about **$25B**.
- **New campuses land in poorer places:** Loudoun's average energy burden is 1.3%; Richland Parish, Louisiana (Meta Hyperion) has a **13.7%** low-income burden.
- **Opinion:** opposition to a nearby data center went from about 4 in 10 to **7 in 10** in a year; **76%** of 2026 voters opposed one ⚠️ (some polls unverified).

## 7. What a resident can do (the site's call to action)
Find your utility's open rate case and its comment deadline, contact your state consumer advocate (6 states have no
residential advocate), file a PUC comment, and know your state's large-load-tariff status. Links are in `policy_states.json`
and `policy_rate_cases.json`.

## Data status
- **47 processed datasets** (~158k rows) plus 2 map layers.
- **Address join:** utility areas link to prices for **94.7% of customers** (96.1% after merger fixes). ZIP and county fallbacks cover gaps. **65% of land area has overlapping territories**, so the site needs a "pick your utility" step.
- **Unverified concentrations:** bill line items (39 of 61), state policy profiles (20 of 51), utility pipelines (13 of 27), rate cases (12 of 38). The site shows a badge on these.
- **Licences to clear before publishing:** S&P-sourced rate-case details (via EEI), so publish aggregates, not the raw list. PUDL licence (check). EIA, HIFLD and DOE LEAD are public; OpenEI ZIP data is CC BY 4.0.
- **Known gaps:** territories are from 2022 (HIFLD Open shut down); no attribution study for ERCOT or the Southeast; no state data-center share for 2025; behind-the-meter use isn't counted.
