"""Build data/processed/finance_utility_capex.csv.

Two kinds of rows:
  * company plans (hand-curated from primary SEC 8-K exhibits downloaded by scripts/finance/fetch_edgar_8k.mjs into
    data/raw/finance/edgar_8k_2026q3 and edgar_8k_2025q4; PowerLines' April 2026 compilation is used only where the
    company's own Q3-2026 / Q4-2025 release did not restate the plan - flagged source_type='secondary').
  * EEI industry totals (actual + projected) parsed by hand from EEI "Industry Capital Expenditures" chart PDF
    (data/raw/finance/eei_industry_capex/EEI-Industry-Capital-Expenditures.pdf, updated March 2026 / Sept 2026).
verified=True means the number was read in the cited document during this session (2026-11-23).
Run: python3 -I scripts/finance/build_capex.py
"""
import csv
import io
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'data/processed/finance_utility_capex.csv')
E = 'https://www.sec.gov/Archives/edgar/data/'
PL = 'https://powerlines.org/wp-content/uploads/2026/04/0413_PowerLines-CapEx-Report.pdf'
EEI = ('https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/'
       'EEI-Industry-Capital-Expenditures.pdf')
B = 1e9

COLS = ['record_type', 'company', 'ticker', 'segment', 'plan_period', 'capex_usd', 'capex_usd_high',
        'rate_base_growth_pct', 'rate_base_growth_note', 'dc_related_note', 'source_url', 'date',
        'source_type', 'verified', 'notes']

rows = []


def plan(company, ticker, period, capex, rb=None, rb_note='', dc='', url='', date='', stype='primary (8-K exhibit)',
         verified=True, notes='', capex_high=None, segment='regulated utility holding co.', rtype='company_plan_latest'):
    rows.append(dict(record_type=rtype, company=company, ticker=ticker, segment=segment, plan_period=period,
                     capex_usd=None if capex is None else round(capex * B), capex_usd_high=None if capex_high is None else round(capex_high * B),
                     rate_base_growth_pct=rb, rate_base_growth_note=rb_note, dc_related_note=dc, source_url=url,
                     date=date, source_type=stype, verified=verified, notes=notes))


def prior(*a, **k):
    k['rtype'] = 'company_plan_prior'
    plan(*a, **k)


# ---------------- regulated utilities: latest plan ------------------------------------------------------------
plan('Dominion Energy', 'D', '2026-2030', 64.7, None, 'not restated in Q3-2026 release (pending NextEra merger)',
     'Dominion Energy Virginia serves Northern Virginia (largest US data-center market). NextEra+Dominion combined '
     'rate base $138B expected to grow ~11%/yr through 2032 and >130 GW large-load pipeline (NEE/D merger release 2026-05-18).',
     PL, '2026-04-13', 'secondary (PowerLines compilation of Q4-2025 earnings materials)', False,
     'Company figure not re-checked in a primary doc this session; Q3-2026 release (' + E + '715957/000119312526439883/d-ex99.htm) has no capex restatement.')
plan('Southern Company (incl. Georgia Power)', 'SO', '2026-2030', 81.0, None, '',
     '$68B of the $81B to regulated electric utilities, ~half to generation (Feb-2026). Contracted large load: 10 GW (YE-2025) -> >11 GW (Q1-2026) -> >17 GW (Q2-2026); '
     'Georgia Power 25-yr 3.2 GW electric service agreement with OpenAI near Savannah; pipeline >75 GW. Utility Dive (Q3-2026): ~$4B added; may rise to ~$100B.',
     'https://www.utilitydive.com/news/southern-co-contracted-large-load-data-centers/826919/', '2026-02-20',
     'secondary (Reuters via The Star; Utility Dive; PowerLines lists $81.2B)', True,
     'Not read in a primary deck; Q3-2026 release (' + E + '92122/000009212226000071/ex99-pressreleaseq32026.htm) does not restate the plan.')
plan('American Electric Power', 'AEP', '2027-2031', 100.0, 13.0, '13%+ rate base CAGR through 2031; rate base to reach $162B by 2031; transmission rate base ~doubling to ~$70B',
     'Q4-2025: +28 GW of signed large-load agreements since Oct-2025; AEP Texas load backed by LOAs rose from 13 GW to 36 GW (hyperscalers/data-center developers). '
     'Q3-2026: ~$37B of the $100B plan is transmission. CEO: new large-load customers should "bear the incremental system costs they create".',
     E + '4904/000000490426000069/a3q20268kpressreleaseex991.htm', '2026-10-28')
plan('Duke Energy', 'DUK', '2026-2030', 102.8, None, '',
     'Duke Q4-2025 release: "largest regulated capital plan in the industry" with contracted demand from AI and advanced manufacturing; 5%-7% EPS growth through 2030.',
     PL, '2026-04-13', 'secondary (PowerLines compilation of Q4-2025 earnings materials)', False,
     'Dollar figure from PowerLines appendix; Duke release ' + E + '1326160/000132616026000007/er-20251231xearningsreleas.htm confirms qualitative claims only.')
plan('NextEra Energy (incl. FPL)', 'NEE', '2026-2030', 94.2, None,
     'FPL regulatory capital employed +9.2% y/y (Q3-2026); FPL 2026 capex ~$12B',
     'NEER signed 25-yr Google PPA to restart 615 MW Duane Arnold (Oct-2025); ~1 GW 20-yr Point Beach PPA (Q3-2026); pending all-stock merger with Dominion.',
     PL, '2026-04-13', 'secondary (PowerLines compilation of Q4-2025 earnings materials)', False,
     'FPL figures verified in ' + E + '753308/000075330826000077/neeq32026exhibit99.htm')
plan('Exelon', 'EXC', '2026-2029', 41.7, 7.9, '7.9% rate base growth from $41.7B of investment (4-year plan); $12-17B transmission + $3-7B storage upside beyond plan',
     'Projected data-center load: ~11 GW "high probability" (ComEd ~9 GW, Mid-Atlantic ~2 GW; ~45% of ComEd backed by FERC-approved TSAs with ~$1.2B collateral) plus ~23 GW future pipeline.',
     E + '1109357/000110935726000092/exc-20261030ex992.htm', '2026-10-30', notes='Wires-only utility (no generation).')
plan('Public Service Enterprise Group', 'PEG', '2026-2030', 22.5, 6.0, 'rate base CAGR 6%-7.5% (regulated plan $22.5B-$25.5B); total 5-yr capital $24B-$28B incl. non-regulated',
     'NJ policy: bills signed requiring large-load data-center tariffs (per Exelon Q3-2026 deck).',
     E + '788784/000119312526451864/d173995dex99.htm', '2026-11-06', capex_high=25.5,
     notes='rate_base_growth_pct = low end of 6%-7.5% range.')
plan('Entergy', 'ETR', '2026-2029', 43.5, None, '',
     'Q3-2026: industrial sales +4.9% driven by data-center and primary-metals customers; Entergy Louisiana serves Meta Hyperion. Adjusted LTM ROE (company-reported) 11.3% vs ~9.7% average authorized.',
     PL, '2026-04-13', 'secondary (PowerLines compilation of Q4-2025 earnings materials)', False,
     'Earned-ROE figure verified in ' + E + '65984/000006598426000322/earningsrelease3q26_ex991.htm')
plan('Xcel Energy', 'XEL', '2027-2031', 70.0, 11.0, '~11% rate base CAGR through 2031 (Investing.com summary of Q3-2026 slides; not re-read in primary deck)',
     'Funding: $35.8B cash from ops, $26.2B new debt, $8.0B equity. Base plan by function: renewables $21.4B, transmission $18.6B, distribution $13.7B, generation $9.2B. Q4-2025 call: data-center contracted capacity expected to double from 3 GW to 6 GW by end-2027 (PowerLines).',
     E + '72903/000007290326000178/xcelearningsreleaseq32026.htm', '2026-10-29',
     notes='Capex verified in primary; rate-base CAGR from secondary source -> treat as UNVERIFIED.')
plan('Sempra (incl. Oncor)', 'SRE', '2026-2030', 65.0, None, '',
     'Record plan, >95% regulated (Texas + California). +$9B potential incremental capex mostly Oncor. Q3-2026: Oncor 2027-31 base plan ~+20% vs 2026-30; Oncor peak 33.3 GW; ~24 GW large load classified base load (10 GW energized) + 21 GW studied.',
     E + '1032208/000103220826000008/ex99_1x20251231xearningsta.htm', '2026-02-26')
plan('CenterPoint Energy', 'CNP', '2026-2035', 70.7, None, '10-year plan; raised by $4.0B in Q3-2026 and $1.5B pulled into 2026-2030; EPS growth 7-9% through 2035',
     'Plan increase tied to accelerating demand in Greater Houston; >=$10B further opportunities identified.',
     E + '1130310/000110465926118963/tm2628051d1_ex99-1.htm', '2026-10-27',
     notes='10-year horizon, not comparable to 5-year plans. PowerLines 5-yr (2026-2030) = $33.1B before the Q3-2026 acceleration.')
plan('PPL', 'PPL', '2027-2030', 25.0, 10.0, 'average annual rate base growth of 10% 2026-2030',
     '+$2B vs prior plan mainly for an extra gas combined-cycle for large loads in Kentucky; KY pipeline 14.7 GW through 2032 (12.8 GW data centers), 2.3 GW under signed reimbursement agreements; ~2 GW Invitium/QTS supply terms in PA.',
     E + '922224/000092222426000050/ppl-9302026exhibit991.htm', '2026-11-06')
plan('FirstEnergy', 'FE', '2026-2030', 36.0, None, 'Q3-2026 actual: total rate base +9.9% y/y, transmission rate base +14.0% y/y',
     '7.9 GW contracted large-load (data-center) demand, nearly doubled in 2026; ~4 GW more in active negotiations.',
     E + '1031296/000103129626000142/ex991-q32026newsrelease.htm', '2026-10-27',
     notes='Energize365 plan; PowerLines lists $36.2B with $19B transmission.')
plan('NiSource', 'NI', '2027-2033', 40.0, 9.0, '9%-10% consolidated investment-base growth 2027-2033 (base-plan rate base 8%-10%)',
     '$8.0B of the $40.0B is data-center investment (GenCo serving large loads) on top of $32.0B base plan.',
     E + '1111711/000111171126000099/ni-ex991_20260930.htm', '2026-10-28',
     notes='7-year plan. rate_base_growth_pct = low end of range.')
plan('Evergy', 'EVRG', '2026-2030', 21.6, None, '',
     'Q3-2026: three amendments to existing electric service agreements plus LOI with Digital Realty for a 1.4 GW expansion (KS/MO).',
     PL, '2026-04-13', 'secondary (PowerLines compilation of Q4-2025 earnings materials)', False,
     'Q3-2026 release ' + E + '1711269/000119312526448521/d193466dex991.htm does not restate capex.')
plan('WEC Energy Group', 'WEC', '2027-2031', 47.5, None, 'asset base $72.8B by 2031E (2025 average $34.2B)',
     'Plan raised by $10.0B; part of transmission, WI LNG and WI gas distribution to be paid by Very Large Customers (VLC, i.e. data centers such as Microsoft Mount Pleasant); $13.7B regulated renewables.',
     E + '783325/000078332526000109/a112026november.htm', '2026-11-06')
plan('Ameren', 'AEE', '2027-2031', 38.1, 13.3, '~13.3% rate base CAGR 2026-2031',
     '', E + '1002910/000100291026000030/q32026ex991earningsrelease.htm', '2026-11-05',
     notes='plan_period inferred as 2027-2031 from the 2026-2031 CAGR window.')
plan('Pinnacle West (APS)', 'PNW', '2025-2028', 10.35, None, '',
     '2026 IRP: customers annual electricity needs projected to more than double by 2041 (~+42,000 GWh).',
     E + '764622/000076462226000055/novemberinvestordeck.htm', '2026-11-06', notes='APS only; 4-year plan.')

# ---------------- regulated utilities: prior plans (to show escalation) ---------------------------------------
prior('American Electric Power', 'AEP', '2026-2030', 72.0, None, '', '', E + '4904/000000490426000011/a4q20258kpressreleaseex991.htm', '2026-02-12')
prior('Southern Company (incl. Georgia Power)', 'SO', '2025-2029', 76.0, None, '', '',
      'https://www.thestar.com.my/tech/tech-news/2026/02/20/southern-co-raises-spending-plan-by-7-as-data-center-power-demand-swells',
      '2026-02-20', 'secondary (Reuters via The Star)', True, 'New $81B plan described as +7% vs prior $76B.')
prior('Xcel Energy', 'XEL', '2026-2030', 60.0, None, '', '', E + '72903/000007290326000006/xcelearningsreleaseq42025.htm', '2026-02-05')
prior('Sempra (incl. Oncor)', 'SRE', '2025-2029', 56.0, None, '', '', E + '1032208/000103220826000008/ex99_1x20251231xearningsta.htm', '2026-02-26')
prior('Ameren', 'AEE', '2026-2030', 31.8, 10.6, '~10.6% rate base CAGR 2025-2030', '', E + '1002910/000100291026000005/q42025ex991earningsrelease.htm', '2026-02-11')
prior('WEC Energy Group', 'WEC', '2026-2030', 37.5, None, '', '', PL, '2026-04-13', 'secondary (PowerLines)', False, 'WEC Q3-2026 deck says new plan is +$10.0B vs prior, consistent with $37.5B.')
prior('PPL', 'PPL', '2026-2029', 23.0, None, '', '', E + '922224/000092222426000050/ppl-9302026exhibit991.htm', '2026-11-06', notes='"$2 billion higher than its prior 2026-2029 plan".')
prior('Public Service Enterprise Group', 'PEG', '2025-2029', 21.0, 6.0, 'rate base CAGR 6%-7.5%', '', E + '788784/000119312526451864/d173995dex99.htm', '2026-11-06', capex_high=24.0)
prior('Public Service Enterprise Group', 'PEG', '2024-2028', 18.0, 6.0, 'rate base CAGR 6%-7.5%', '', E + '788784/000119312526451864/d173995dex99.htm', '2026-11-06', capex_high=21.0)
prior('CenterPoint Energy', 'CNP', '2026-2035', 66.7, None, '10-year plan before Q3-2026 raise', '', E + '1130310/000110465926118963/tm2628051d1_ex99-1.htm', '2026-10-27')
prior('Exelon', 'EXC', '2025-2029', 50.5, None, '', '', PL, '2026-04-13', 'secondary (PowerLines)', False, 'PowerLines footnote: most recent 5-year Exelon plan.')
prior('FirstEnergy', 'FE', '2025-2029', 28.0, None, '', '', PL, '2026-04-13', 'secondary (PowerLines: new plan is "$8 billion or nearly 30 percent" above previous)', False, 'Derived: 36.2 - 8 = ~28.2.')

# ---------------- generation (IPPs): growth / acquisition spending -------------------------------------------
plan('NRG Energy', 'NRG', '2025-2026', 12.0, None, '', 'Acquisition of ~13 GW gas fleet + CPower (~6 GW C&I VPP) from LS Power; 7.5x 2026 EV/EBITDA; ~50% of new-build replacement cost. Nov-2026: agreed to sell 4.9 GW (6 gas plants) back to LS Power for $4.0B cash to fund $3B buybacks across 2026-27. 1.2 GW "bring-your-own-power" data-center project.',
     E + '1013871/000110465925047007/tm2514561d1_ex99-1.htm', '2025-05-12', segment='independent power producer', rtype='ipp_acquisition',
     notes='capex_usd = enterprise value of acquisition, not a capex plan.')
plan('Vistra', 'VST', '2026', 4.0, None, '', 'Cogentrix: ~5,500 MW of gas (PJM, ISO-NE, ERCOT) at ~$730/kW net, ~7.25x 2027 EBITDA; closed Oct-2026. Earlier: Energy Harbor (~4,000 MW nuclear, Mar-2024), Lotus (~2,300 MW gas, Oct-2025). Fleet ~50 GW.',
     E + '1692819/000119312526002589/d62722dex991.htm', '2026-01-05', segment='independent power producer', rtype='ipp_acquisition',
     notes='capex_usd = net purchase price of Cogentrix.')
plan('Constellation Energy', 'CEG', '2025-2026', 26.6, None, '', 'Calpine: equity $16.4B (50M CEG shares + $4.5B cash) + ~$12.7B net debt; net purchase price $26.6B = 7.9x 2026 EV/EBITDA; completed (per Feb-2026 release). Oct-2026: conditional DOE loan guarantee up to $5.0B for nuclear uprates; >$4.3B uprate program tied to Google PPA; >$3B Calvert Cliffs investment tied to Amazon PPA.',
     E + '1868275/000186827525000006/ceg-202501108kxexh991.htm', '2025-01-10', segment='independent power producer', rtype='ipp_acquisition',
     notes='capex_usd = net purchase price of Calpine.')

# ---------------- EEI industry totals --------------------------------------------------------------------------
actual = {2016: 112.5, 2017: 113.1, 2018: 119.2, 2019: 123.8, 2020: 132.7, 2021: 134.1, 2022: 147.7, 2023: 171.9,
          2024: 178.2, 2025: 204.1}
proj = {2026: 238.8, 2027: 262.1, 2028: 275.7, 2029: 287.8, 2030: 296.3}
for y, v in actual.items():
    rows.append(dict(record_type='eei_industry_actual', company='US investor-owned electric utilities (EEI)', ticker='',
                     segment='industry', plan_period=str(y), capex_usd=round(v * B), date='2026-03',
                     source_url=EEI, source_type='primary (EEI Financial Analysis Dept.)', verified=True,
                     notes='Consolidated at parent/holding-company level; 2016-2025 total $1.44T.'))
for y, v in proj.items():
    rows.append(dict(record_type='eei_industry_projection', company='US investor-owned electric utilities (EEI)', ticker='',
                     segment='industry', plan_period=str(y), capex_usd=round(v * B), date='2026-03',
                     source_url=EEI, source_type='primary (EEI projection, March 2026)', verified=True,
                     notes='2026-2030 projection total $1.36T.'))
func = {'2025P (as of Sept 2025)': dict(total=207.9, Distribution=66.0, Transmission=37.6, Generation=63.2, **{'Gas-related': 28.5, 'Other': 12.6}),
        '2026P (as of Sept 2026)': dict(total=238.8, Distribution=72.3, Transmission=44.5, Generation=80.4, **{'Gas-related': 28.6, 'Other': 13.0})}
for p, d in func.items():
    for k, v in d.items():
        rows.append(dict(record_type='eei_functional_projection', company='US investor-owned electric utilities (EEI)',
                         ticker='', segment='industry: ' + k, plan_period=p, capex_usd=round(v * B), date='2026-09',
                         source_url=EEI, source_type='primary (EEI)', verified=True,
                         notes='Functional projections are not revised to actuals.'))
rows.append(dict(record_type='powerlines_aggregate', company='51 investor-owned utilities (PowerLines review of Q4-2025 earnings)',
                 ticker='', segment='industry', plan_period='2026-2030', capex_usd=round(1.4e12), date='2026-04-13',
                 source_url=PL, source_type='advocacy (PowerLines, consumer group)', verified=True,
                 dc_related_note='32 of 51 utilities cited data centers/load growth as a capex driver; 9 expect >5,000 MW of growth each.',
                 notes='>21% above the ~$1.1T 5-yr total outlined a year earlier; top-10 spenders = $707B (~53%).'))

with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, '') if r.get(k) is not None else '' for k in COLS})
print('rows', len(rows), '->', OUT)
