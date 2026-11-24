"""Build data/processed/bills_anatomy.json: what a 1,000 kWh/month residential bill is made of, for ~12 large utilities.

Run from project root: python3 -I scripts/bills/build_anatomy.py
Every input number below is typed in from a cited source (tariff sheet, commission page, or OpenEI URDB record that
was downloaded to data/raw/bills/openei_urdb_2026-11-23/). Derived numbers are marked derived=True and say how.
'verified' means: checked against the live source in this research session (2026-11-23). URDB = OpenEI Utility Rate
Database (NREL/DOE), which transcribes utility tariffs; URDB-only numbers are verified=False unless cross-checked.
Taxes/franchise fees are generally NOT in these tariff sums unless listed; see each utility's notes.
"""
import json
import os

import pandas as pd

ROOT = os.getcwd()
KWH = 1000
URDB = 'https://apps.openei.org/IURDB/rate/view/'

# PJM residential capacity cost rule of thumb (estimate): PJM IMM/LBNL all-load wholesale capacity cost per kWh.
# LBNL July 2026 data file, tab "PJM capacity prices": 2024 0.361, 2025 1.276, 2026 (est) 1.957 cents/kWh (nominal),
# weighted auction prices $45.57 (24/25) -> $296.98 (25/26) -> $329.17 (26/27) -> $333.44/MW-day (27/28).
PJM_CAP_CENTS = {'2024': 0.361, '2025': 1.276, '2026_est': 1.957}
LBNL_DATA = 'https://emp.lbl.gov/sites/default/files/2026-07/Retail%20Price%20Trends_2026%20edition_%20JulyUpdate_Data%20File.xlsx'


def line(category, label, cents_per_kwh=None, fixed_usd=None, source=None, verified=False, derived=False, note=None):
    usd = (fixed_usd or 0) + (cents_per_kwh or 0) * KWH / 100
    return {'category': category, 'label': label, 'cents_per_kwh': cents_per_kwh, 'fixed_usd_per_month': fixed_usd,
            'usd_at_1000kwh': round(usd, 2), 'source': source, 'verified': verified, 'derived': derived, 'note': note}


def blended(blocks, kwh=KWH):
    """blocks = [(upper_kwh or None, cents)], cumulative tiers -> average cents/kWh at `kwh`."""
    tot, prev = 0.0, 0.0
    for upper, c in blocks:
        hi = kwh if upper is None else min(upper, kwh)
        if hi > prev:
            tot += (hi - prev) * c
            prev = hi
    return tot / kwh


def annualized(by_period, months):
    """by_period = {period: blocks}; months = list of 12 period ids (Jan..Dec) -> annual average cents/kWh at 1,000 kWh."""
    return sum(blended(by_period[m]) for m in months) / 12


U = []

# ---------------------------------------------------------------- PECO (PA, PJM) default service
peco_tariff = 'https://azure-na-assets.contentstack.com/v3/assets/blt1b5616c79bacadb4/bltef2bb157cc587eac/695440f39dd7d11ce0542224/Pages_52_Rate_R_from_clean_up_pages_for_ICUS_FARS_Supp_no._21_eff_Jan_1_2026.pdf'
pa_puc = 'https://www.puc.pa.gov/press-release/2026/puc-alerts-consumers-to-june-1-electric-price-changes-and-higher-summer-energy-costs-5-20-26'
U.append({
    'utility': 'PECO Energy Co', 'eia_utility_id': 14940, 'state': 'PA', 'rto_iso': 'PJM', 'market': 'restructured (retail choice); default service',
    'rate': 'Rate R (residence service) + default service (Price to Compare)', 'effective': 'distribution 2026-01-01; PTC 2026-06-01 to 2026-11-30',
    'lines': [
        line('fixed', 'Fixed distribution service charge', fixed_usd=11.30, source=peco_tariff, verified=True),
        line('distribution', 'Variable distribution service charge', 10.276, source=peco_tariff, verified=True),
        line('riders', 'Riders: USF, EE&C (Act 129), DSIC, NBT, consumer-ed, COVID uncollectible, fiber surcharge',
             round(1.371 - 0.787, 3), source=URDB + '69e650226746522c70079989', derived=True,
             note='URDB adjustments 1.371 c/kWh (Jan 2026) minus the transmission estimate below; approximate'),
        line('transmission', 'Transmission Service Charge (inside the Price to Compare)', 0.787, source=pa_puc, derived=True,
             note='PTC 11.572 c (PA PUC, June 1 2026, marked "estimated") minus default-service generation rate 10.785 c (PUC filing, UNVERIFIED)'),
        line('supply', 'Default-service generation (GSA), incl. PJM capacity', 10.785, source='https://www.puc.pa.gov/pcdocs/1923196.pdf', verified=False,
             note='UNVERIFIED: figure from search snippet of PECO default-service filing; PTC 11.572 c verified on PA PUC press release'),
    ],
    'capacity_note': 'PJM capacity is embedded in the generation (GSA) rate; PECO buys default supply via laddered full-requirements auctions, so June 2025/2026 capacity jumps flowed in over ~2 years.',
    'taxes_note': 'PA gross receipts tax is embedded in rates; no sales tax on residential electricity.',
})

# ---------------------------------------------------------------- BGE (MD, PJM) standard offer service
U.append({
    'utility': 'Baltimore Gas & Electric Co', 'eia_utility_id': 1167, 'state': 'MD', 'rto_iso': 'PJM', 'market': 'restructured; standard offer service (SOS)',
    'rate': 'Schedule R (residential) with SOS', 'effective': '2026-01-01 (URDB record); SOS resets each June 1 and Oct 1',
    'lines': [
        line('fixed', 'Customer charge', fixed_usd=10.32, source=URDB + '69a728bdd1ab4183610bb29a'),
        line('distribution', 'Delivery (distribution) energy charge', 4.859, source=URDB + '69a72480d189752a6d0863a9'),
        line('supply', 'Standard Offer Service: generation + transmission + admin charge (incl. PJM capacity)', round(21.537 - 4.859, 3),
             source=URDB + '69a728bdd1ab4183610bb29a', derived=True, note='URDB "delivery + SOS" 21.537 c minus delivery-only 4.859 c'),
        line('riders', 'Riders: EmPOWER Maryland EE charge, demand response, multi-year-plan adjustment', 1.381, source=URDB + '69a728bdd1ab4183610bb29a'),
    ],
    'capacity_note': 'BGE zone cleared at a separate, higher price in the 2025/26 PJM auction (LDA constraint). Maryland OPC (advocacy) projected ~19% higher BGE bills from that auction (pre-June-2025 estimate, via PIRG summary).',
    'taxes_note': 'Excludes local energy taxes, MD universal service and franchise charges where billed separately.',
})

# ---------------------------------------------------------------- ComEd (IL, PJM)
plugin = 'https://plugin.illinois.gov/understanding-the-price-to-compare/price-to-compare-comed.html'
U.append({
    'utility': 'Commonwealth Edison Co', 'eia_utility_id': 4110, 'state': 'IL', 'rto_iso': 'PJM', 'market': 'restructured; utility default supply procured by Illinois Power Agency',
    'rate': 'Single-family non-space-heat; delivery (RDS) + ComEd supply (BES)', 'effective': 'supply & transmission 2026-10-01 to 2027-05-31; delivery URDB record eff. 2025-01-01 (stale)',
    'lines': [
        line('fixed', 'Customer + standard metering charges', fixed_usd=19.52, source=URDB + '679c05e9addfd4b96500e1d3', note='2025 level; ComEd delivery rates step up each January under its multi-year rate plan'),
        line('distribution', 'Distribution facilities charge', 6.187, source=URDB + '679c05e9addfd4b96500e1d3', note='2025 level'),
        line('riders', 'Riders: zero-emission & carbon-free adjustments, EE, environmental, energy-transition assistance, renewable', 1.296, source=URDB + '679c05efaddfd4b96500e1d4', note='2025 level'),
        line('transmission', 'Transmission services charge', 1.69, source=plugin, verified=True),
        line('supply', 'Electric supply charge (incl. PJM capacity), non-summer', 8.413, source=plugin, verified=True),
    ],
    'capacity_note': 'ComEd supply passes PJM capacity through each June. Citizens Utility Board (advocacy) says capacity is ~20% of supply; a consumer-advocate provision turns part of it into a credit when energy prices are high (~1.3 c/kWh lower in June 2026, per CUB, UNVERIFIED). Summer (Jun-Sep 2026) PTC was 10.399 c.',
    'taxes_note': 'Excludes IL electricity excise tax and municipal utility taxes (e.g., Chicago); Plug In Illinois also lists a Renewable Energy Adjustment in Taxes & Fees.',
})

# ---------------------------------------------------------------- AEP Ohio (OH, PJM)
U.append({
    'utility': 'Ohio Power Co (AEP Ohio)', 'eia_utility_id': 14006, 'state': 'OH', 'rto_iso': 'PJM', 'market': 'restructured; standard service offer (SSO) via auctions',
    'rate': 'RS (Ohio Power rate zone), SSO customer', 'effective': '2026-04-10 (URDB record)',
    'lines': [
        line('fixed', 'Customer charge (incl. fixed riders)', fixed_usd=18.788, source=URDB + '69dd1b5381bf8b311c0576a8'),
        line('distribution', 'Base distribution energy charge', 3.47738, source=URDB + '69dd1b5381bf8b311c0576a8'),
        line('riders', 'Transmission (BTCR) + kWh tax + riders: PIPP, enhanced reliability, distribution investment, econ. development, EE, storm, gridSMART', 5.6109,
             source=URDB + '69dd1b5381bf8b311c0576a8', note='URDB delivery-only adjustments (tier <=2000 kWh); transmission not separable from URDB'),
        line('supply', 'SSO generation: generation energy + generation capacity riders (+ auction cost)', round(13.299 - 5.6109, 4), source=URDB + '69dd1b5381bf8b311c0576a8', derived=True,
             note='URDB bundled adjustments 13.299 c minus delivery-only adjustments 5.611 c; check against PUCO Apples-to-Apples SSO price'),
    ],
    'capacity_note': 'Ohio SSO bills show a separate "Generation Capacity" rider; it resets every June 1 with the PJM delivery year.',
    'taxes_note': 'Ohio kWh excise tax is inside the riders line.',
})

# ---------------------------------------------------------------- JCP&L (NJ, PJM) BGS; PSE&G totals from BPU
jcpl = URDB + '689ad92169e023ffe701ba9d'
U.append({
    'utility': 'Jersey Central Power & Light (JCP&L)', 'eia_utility_id': 9726, 'state': 'NJ', 'rto_iso': 'PJM', 'market': 'restructured; Basic Generation Service (BGS) via annual statewide auction (3-year ladder)',
    'rate': 'Residential Service (RS), summer (June-Sept) month', 'effective': '2025-07-01 (URDB record); BGS reset 2026-06-01',
    'lines': [
        line('fixed', 'Customer charge', fixed_usd=4.27, source=jcpl),
        line('distribution', 'Distribution (summer: 2.0182 c first 600 kWh, 7.981 c above)', round((600 * 2.0182 + 400 * 7.981) / 1000, 4), source=jcpl, derived=True, note='blended for 1,000 kWh'),
        line('supply', 'BGS supply incl. transmission & PJM capacity (summer: 14.0765 c first 600 kWh, 14.999 c above)', round((600 * 14.0765 + 400 * 14.999) / 1000, 4),
             source=URDB + '689b0eb4f8eb73eda90d3bd6', derived=True, note='URDB "delivery + BGS" minus delivery-only rates; transmission not separable'),
        line('riders', 'Riders: Societal Benefits (incl. clean energy, USF), non-utility generation, RGGI, nuclear ZEC, reliability plus, LRAM, COVID', 1.31, source=jcpl),
    ],
    'official_typical_bill': {'kwh': 650, 'usd_before_june_2026': 135.24, 'usd_after_june_1_2026': 137.47, 'source': 'https://nj.gov/bpu/newsroom/2026/approved/20260212.html', 'verified': True},
    'capacity_note': 'NJ BGS buys one-third of residential supply each February for 3 years, so a PJM capacity spike is phased in over 3 auctions. BPU: 2026 BGS prices rose slightly, driven by wholesale energy and PJM capacity, damped by the PJM price collar ($175-$325/MW-day).',
    'taxes_note': 'NJ sales tax (6.625%) applies to residential electricity; BPU/URDB figures include SUT inside rates (NJ tariffs are SUT-inclusive) - UNVERIFIED.',
    'sibling_utility': {'utility': 'PSE&G', 'eia_utility_id': 15477, 'kwh': 650, 'usd_before_june_2026': 183.46, 'usd_after_june_1_2026': 180.23, 'pct_change': -1.8,
                        'source': 'https://nj.gov/bpu/newsroom/2026/approved/20260212.html', 'verified': True,
                        'note': 'Component split not obtained (URDB API rate-limited). Before Residential Universal Bill Credits ordered under Gov. Sherrill EO No. 1.'},
})

# ---------------------------------------------------------------- Dominion Energy Virginia (VA, PJM, vertically integrated)
DOM_URDB = URDB + '6997c46543b6aa9b2a015f78'  # from USURDB bulk file (data/raw/bills/openei_usurdb_bulk_2026-11-23)
dom_months = [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1]  # period 0 = Jun-Sep
dom_base = annualized({0: [(800, 7.6602), (None, 7.9539)], 1: [(800, 7.5454), (None, 6.0261)]}, dom_months)
U.append({
    'utility': 'Virginia Electric & Power Co (Dominion Energy Virginia)', 'eia_utility_id': 19876, 'state': 'VA', 'rto_iso': 'PJM', 'market': 'vertically integrated (PJM member)',
    'rate': 'Schedule 1 residential (annualized: Jun-Sep summer blocks, other months winter blocks)', 'effective': '2026-01-01 (URDB record; after SCC biennial order)',
    'lines': [
        line('fixed', 'Basic customer charge', fixed_usd=7.58, source=DOM_URDB),
        line('base_energy', 'Base energy (distribution + generation + transmission base rates), annualized', round(dom_base, 4), source=DOM_URDB, derived=True,
             note='summer 7.6602 c first 800 kWh / 7.9539 c above; winter 7.5454 c / 6.0261 c'),
        line('riders', 'Fuel rider A + rate-adjustment-clause riders (transmission T1, CVOW offshore wind, RPS, nuclear life extension, grid transformation, undergrounding, EE, new plants, coal-ash closure)', 8.6944, source=DOM_URDB,
             note='URDB lumps fuel and all riders; riders are ~half the bill'),
    ],
    'typical_bill_1000kwh': {'2025-07-01': 149.92, 'base_rate_increase_2026': 11.24, 'base_rate_increase_2027': 2.36,
                             'source': 'https://cardinalnews.org/2025/11/26/regulators-approve-dominion-energy-rate-increase/', 'verified': True,
                             'note': 'SCC final order (biennial review), 2025-11-25; ROE 9.8%; new GS-5 class for >=25 MW loads from 2027-01-01; SCC rejected moving capacity costs from base rates into the fuel factor. Fuel factor set in a separate case.'},
    'capacity_note': 'As a vertically integrated utility Dominion recovers capacity through base rates/riders, not a June supply reset.',
    'taxes_note': 'VA consumption tax and local utility taxes extra.',
})

# ---------------------------------------------------------------- PSE&G (NJ, PJM) BGS
PSEG_SO = URDB + '69e244d8f454c9f31002aaac'
PSEG_D = URDB + '69e244d3a999a8521d0fed8c'
pseg_m = [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0]  # period 1 = Jun-Sep
U.append({
    'utility': 'Public Service Electric & Gas (PSE&G)', 'eia_utility_id': 15477, 'state': 'NJ', 'rto_iso': 'PJM', 'market': 'restructured; Basic Generation Service (3-year laddered auction)',
    'rate': 'RS residential, annualized (Jun-Sep summer)', 'effective': 'URDB record 2026-04-01 (delivery); BGS portion likely the June 2025-May 2026 BGS - UNVERIFIED',
    'lines': [
        line('fixed', 'Service charge', fixed_usd=6.00, source=PSEG_D),
        line('distribution', 'Distribution charges (winter 4.7989 c; summer 8.2602 c first 600 kWh, 8.6677 c above), annualized',
             round(annualized({0: [(None, 4.7989)], 1: [(600, 8.2602), (None, 8.6677)]}, pseg_m), 4), source=PSEG_D, derived=True),
        line('supply', 'BGS supply + transmission (incl. PJM capacity), annualized',
             round(annualized({0: [(None, 24.658 - 4.7989)], 1: [(600, 27.8394 - 8.2602), (None, 29.1817 - 8.6677)]}, pseg_m), 4), source=PSEG_SO, derived=True,
             note='URDB "delivery + BGS + transmission" minus delivery-only rate'),
        line('riders', 'Societal Benefits, non-utility generation, solar pilot, green programs, nuclear ZEC, CIP, infrastructure (IIP) charges, tax adjustment credit',
             round(annualized({0: [(None, 1.2178)], 1: [(600, 1.2339), (None, 1.234)]}, pseg_m), 4), source=PSEG_D, derived=True),
    ],
    'official_typical_bill': {'kwh': 650, 'usd_before_june_2026': 183.46, 'usd_after_june_1_2026': 180.23, 'pct_change': -1.8,
                              'source': 'https://nj.gov/bpu/newsroom/2026/approved/20260212.html', 'verified': True, 'note': 'before Residential Universal Bill Credits (Gov. Sherrill EO No. 1)'},
    'capacity_note': 'One-third of BGS supply is re-auctioned each February for 3 years, so PJM capacity changes phase in over 3 years from each June 1.',
    'taxes_note': 'NJ tariffs are quoted including 6.625% sales and use tax (UNVERIFIED for URDB values).',
})

# ---------------------------------------------------------------- Pepco DC (PJM) SOS
PEP_SO = URDB + '68b399e19d10ce4ee705c572'
PEP_D = URDB + '68b397ff25d85a1c070f0a0d'
pep_m = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1]  # period 0 = Jun-Oct
U.append({
    'utility': 'Potomac Electric Power Co (Pepco) - District of Columbia', 'eia_utility_id': 15270, 'state': 'DC', 'rto_iso': 'PJM', 'market': 'restructured; standard offer service (SOS)',
    'rate': 'Schedule R with SOS, annualized (Jun-Oct summer)', 'effective': '2025-08-01 (URDB record; SOS from June 1 2025 - superseded June 1 2026)',
    'lines': [
        line('fixed', 'Customer charge', fixed_usd=17.09, source=PEP_D),
        line('distribution', 'Distribution (1.715 c first 400 kWh; 4.895 c summer / 3.419 c winter above), annualized',
             round(annualized({0: [(400, 1.715), (None, 4.895)], 1: [(400, 1.715), (None, 3.419)]}, pep_m), 4), source=PEP_D, derived=True),
        line('supply', 'SOS generation + transmission + procurement cost adjustment (incl. PJM capacity), annualized',
             round(annualized({0: [(30, 0.0), (400, 16.582 - 1.715), (None, 19.726 - 4.895)], 1: [(30, 0.0), (400, 13.964 - 1.715), (None, 15.667 - 3.419)]}, pep_m), 4),
             source=PEP_SO, derived=True, note='URDB with-SOS minus delivery-only; URDB shows no supply rate on the first 30 kWh (transcription quirk)'),
        line('riders', 'DC delivery tax, public space occupancy, residential aid discount, sustainable energy & energy assistance trust funds, undergrounding riders', 1.696, source=PEP_D),
    ],
    'capacity_impact_2025_26': {'residential_cents_per_kwh': 1.7, 'usd_per_month': 10, 'pct': 9,
                                'source': 'https://opc-dc.gov/wp-content/uploads/2025/05/PJM-Capacity-Market-Report-FINAL-OPC-Synapse.pdf', 'verified': True,
                                'publisher': "Synapse Energy Economics for DC Office of the People's Counsel (consumer advocate)"},
    'capacity_note': 'SOS is procured in laddered tranches; June 1 resets carry PJM capacity costs.',
    'taxes_note': 'DC delivery tax is inside the riders line.',
})

# ---------------------------------------------------------------- Georgia Power (vertically integrated, Southeast)
gp = URDB + '677c384de1bf88853903410c'
summer = 14.00 + (650 * (8.6121 + 5.844) + 350 * (14.3047 + 6.674)) / 100
winter = 14.00 + 1000 * (8.0602 + 5.462) / 100
U.append({
    'utility': 'Georgia Power Co', 'eia_utility_id': 7140, 'state': 'GA', 'rto_iso': 'none (Southern Co. BA)', 'market': 'vertically integrated',
    'rate': 'Schedule R-30 residential (annualized: 4 summer months Jun-Sep tiered, 8 winter months flat)', 'effective': '2025-01-01 (URDB record)',
    'lines': [
        line('fixed', 'Basic service charge ($0.4603/day x 30.4)', fixed_usd=14.00, source=gp),
        line('base_energy', 'Base energy charge (generation + T&D + Vogtle NCCR in base), annualized', round((4 * (650 * 8.6121 + 350 * 14.3047) / 1000 + 8 * 8.0602) / 12, 4), source=gp, derived=True),
        line('riders', 'Fuel cost recovery + environmental compliance (ECCR) + demand-side management', round((4 * (650 * 5.844 + 350 * 6.674) / 1000 + 8 * 5.462) / 12, 4), source=gp, derived=True),
    ],
    'seasonal_usd_at_1000kwh': {'summer': round(summer, 2), 'winter': round(winter, 2)},
    'capacity_note': 'No capacity market: generation capacity (incl. Plant Vogtle units 3-4) is in base rates; new data-center-driven generation is certified by the GA PSC. GA PSC conditioned large-load service on downward pressure of $8.50/mo on residential bills in 2029-2031 (per LBNL compilation; utility/regulator claim).',
    'taxes_note': 'Excludes municipal franchise fee and local sales tax lines.',
})

# ---------------------------------------------------------------- Oncor (TX, ERCOT) + retail energy
puct = 'https://www.puc.texas.gov/industry/electric/rates/tdr/'
U.append({
    'utility': 'Oncor Electric Delivery (TDU) + competitive retail provider', 'eia_utility_id': 44372, 'state': 'TX', 'rto_iso': 'ERCOT', 'market': 'fully competitive retail (no default utility supply)',
    'rate': 'Oncor residential TDU charges + statewide average retail energy charge', 'effective': 'TDU as of 2026-11-01',
    'lines': [
        line('fixed', 'TDU customer charge + metering charge', fixed_usd=1.48 + 2.58, source=puct, verified=True),
        line('distribution', 'TDU volumetric delivery charge (distribution + transmission cost recovery riders)', 6.8673, source=puct, verified=True),
        line('supply', 'Retail energy charge (REP energy, ERCOT wholesale, REP margin) - statewide estimate', round(17.273 - 5.638, 3), derived=True,
             source='EIA-861 2025 (this repo: bills_utility_prices.csv tx_rep_all_in_price_cents_kwh 17.273 minus Oncor 2025 delivery revenue/kWh 5.638)',
             note='Estimate; actual plans vary widely - compare on PowerToChoose'),
    ],
    'official_typical_tdu_bill': {'kwh': 1000, 'usd': 72.73, 'source': puct, 'verified': True},
    'capacity_note': 'ERCOT has no capacity market (energy-only); scarcity pricing sits inside the retail energy charge.',
    'taxes_note': 'Excludes PUCT assessment, gross receipts pass-through and local sales tax (TX residential electricity is exempt from state sales tax).',
})

# ---------------------------------------------------------------- Duke Energy Carolinas (NC)
dec = URDB + '6998c205a746c90e550cb23f'
U.append({
    'utility': 'Duke Energy Carolinas, LLC (NC)', 'eia_utility_id': 5416, 'state': 'NC', 'rto_iso': 'none (Duke BA)', 'market': 'vertically integrated',
    'rate': 'Schedule RS (residential)', 'effective': '2026-01-01 (URDB record)',
    'lines': [
        line('fixed', 'Basic customer charge', fixed_usd=14.00, source=dec),
        line('base_energy', 'Energy charge (generation, transmission, distribution, base fuel)', 12.2604, source=dec),
        line('riders', 'Riders: fuel adjustment, EE/DSM, CPRE, EDIT-4, customer assistance, nuclear PTC credit', 0.4951, source=dec),
    ],
    'capacity_note': 'No capacity market; generation capacity in base rates (Carbon Plan / IRP resources approved by NCUC).',
    'taxes_note': 'NC 7% sales tax on residential electricity not included (UNVERIFIED rate).',
})

# ---------------------------------------------------------------- Entergy Louisiana
ell = URDB + '69a99f187cef8411ae01894b'
U.append({
    'utility': 'Entergy Louisiana LLC', 'eia_utility_id': 11241, 'state': 'LA', 'rto_iso': 'MISO', 'market': 'vertically integrated (MISO member)',
    'rate': 'Residential Service (RS), legacy ELL area', 'effective': '2026-03-02 (URDB record)',
    'lines': [
        line('fixed', 'Customer charge incl. advanced-meter charge', fixed_usd=11.99, source=ell),
        line('base_energy', 'Base energy charge', 3.762, source=ell),
        line('riders', 'Fuel adjustment + fuel stabilization + financed storm cost riders/offsets + environmental + EE + resilience plan', 4.2923, source=ell),
    ],
    'capacity_note': 'MISO capacity auction exists but most capacity is self-supplied; storm securitization (Hurricane Ida etc.) is a visible bill line (LBNL: ~1.43 c/kWh in 2025).',
    'taxes_note': 'Excludes Formula Rate Plan rider and local franchise/sales taxes; URDB fuel adjustment may lag monthly FAC - tariff sum (9.3 c/kWh) is well below EIA-861M 2026 YTD average revenue (12.7 c/kWh), so treat as partial.',
})

# ---------------------------------------------------------------- PG&E (CA) - full unbundling from tariff
PGE_TARIFF = 'https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-1.pdf'
base_kwh = 9.8 * 30.4  # Region X summer baseline (URDB record 69d93778e617cdda9b02c73c); winter 9.7 kWh/day
cia = (-4.052 * base_kwh + 4.089 * (KWH - base_kwh)) / KWH
U.append({
    'utility': 'Pacific Gas & Electric Co. (bundled, Baseline Region X)', 'eia_utility_id': 14328, 'state': 'CA', 'rto_iso': 'CAISO', 'market': 'vertically integrated IOU (CCA/DA customers buy generation elsewhere)',
    'rate': 'E-1 tiered residential, Income Tier 3 base services charge', 'effective': '2026-06-01 (Advice 7921-E, D.26-04-036)',
    'lines': [
        line('fixed', 'Base services charge (income tier 3: $0.79343/day)', fixed_usd=round(0.79343 * 30.4, 2), source=PGE_TARIFF, verified=True,
             note='New income-graduated fixed charge; tier 1 $0.19713/day, tier 2 $0.39688/day'),
        line('supply', 'Generation', 12.855, source=PGE_TARIFF, verified=True),
        line('distribution', 'Distribution', 18.042, source=PGE_TARIFF, verified=True, note='includes embedded wildfire mitigation capex/O&M'),
        line('distribution', 'Conservation incentive adjustment (tier 1 -4.052 c, tier 2 +4.089 c; blended for 1,000 kWh with ~298 kWh baseline)', round(cia, 4), source=PGE_TARIFF, verified=True, derived=True),
        line('transmission', 'Transmission + transmission rate adjustments + reliability services', round(4.638 + 0.453 + 0.013, 3), source=PGE_TARIFF, verified=True),
        line('riders', 'Wildfire Fund charge (0.591 c) + wildfire hardening charge (0.391 c)', 0.982, source=PGE_TARIFF, verified=True),
        line('riders', 'Public purpose programs, nuclear decommissioning, CTC, ECRA (recovery bond charge and credit net to zero)', round(0.614 - 0.002 + 0.027 + 0.002, 3), source=PGE_TARIFF, verified=True),
        line('riders', 'Power charge indifference adjustment (credit)', -1.011, source=PGE_TARIFF, verified=True),
    ],
    'other_credits': {'california_climate_credit_semiannual_usd': -36.18, 'annualized_usd_per_month': round(-36.18 * 2 / 12, 2), 'source': PGE_TARIFF},
    'capacity_note': 'No capacity market; CPUC resource-adequacy obligations are inside generation.',
    'taxes_note': 'Excludes local utility users taxes and the state electrical energy surcharge if billed separately. LBNL estimates wildfire mitigation and liability at ~5.0 c/kWh of PG&E 2025 prices in total (most of it inside distribution).',
    'usage_note': 'Average PG&E bundled residential use is ~450 kWh/month (EIA-861M 2026), so a 1,000 kWh bill reaches tier 2 and is not typical.',
})

# ---------------------------------------------------------------- finalize
um = pd.read_csv(os.path.join(ROOT, 'data/processed/bills_utility_monthly.csv'))
for u in U:
    tot = sum(l['usd_at_1000kwh'] for l in u['lines'])
    for l in u['lines']:
        l['pct_of_bill'] = round(l['usd_at_1000kwh'] / tot * 100, 1) if tot else None
    u['total_usd_at_1000kwh'] = round(tot, 2) if u['lines'] else None
    u['implied_cents_per_kwh'] = round(tot / 10, 2) if u['lines'] else None
    x = um[(um.eia_utility_id == u['eia_utility_id']) & (um.state == u['state']) & (um.year == 2026)]
    if len(x):
        u['eia861m_check'] = {'period': '2026-01..2026-%02d' % x.month.max(),
                              'avg_revenue_cents_per_kwh': round(x.res_revenue_thousand_usd.sum() / x.res_sales_mwh.sum() * 100, 2),
                              'avg_monthly_kwh': round(x.res_sales_mwh.sum() * 1000 / x.res_customers.mean() / x.month.nunique(), 0),
                              'note': 'EIA-861M bundled revenue/sales; includes taxes billed as revenue, CAP/low-income discounts and seasonal usage mix, so it differs from a tariff sum'}
    cats = {}
    for l in u['lines']:
        cats[l['category']] = round(cats.get(l['category'], 0) + l['usd_at_1000kwh'], 2)
    u['by_category_usd'] = cats

doc = {
    'description': 'Residential bill anatomy at 1,000 kWh/month for large US utilities, assembled from tariffs/commission pages (2025-2026). See research/bills/FINDINGS.md.',
    'generated': '2026-11-23',
    'kwh_basis': KWH,
    'categories': {'fixed': 'monthly customer/meter charges', 'distribution': 'local wires (per kWh)', 'transmission': 'high-voltage grid',
                   'supply': 'generation/energy incl. capacity (default/standard-offer service in restructured states)',
                   'base_energy': 'bundled base rate (generation+T+D) in vertically integrated utilities', 'riders': 'surcharges/adjustment clauses (fuel, EE, storm, public-purpose, nuclear support, etc.)'},
    'pjm_capacity_context': {
        'how_it_reaches_bills': [
            'PJM runs the Base Residual Auction ~3 years ahead (recently compressed); each delivery year runs June 1 - May 31.',
            'Load-serving entities pay the zonal clearing price x their customers\' peak-load contribution; for default-service customers that cost is inside the supply/Price-to-Compare/SOS/BGS rate.',
            'Restructured PJM states reset default-service prices on June 1 (PA, OH, IL, MD, NJ, DE, DC), so capacity changes show up in June bills; states that ladder procurement (NJ 3-year BGS, MD/DC/PA multi-year tranches) phase the change in over 2-3 years.',
            'Shopping customers see it when their retail contract renews; vertically integrated PJM utilities (Dominion, APCo, many co-ops) recover capacity through base rates/riders instead of a June reset.',
        ],
        'pjm_weighted_capacity_price_usd_mw_day': {'2023/24': 42.01, '2024/25': 45.57, '2025/26': 296.98, '2026/27': 329.17, '2027/28': 333.44, 'source': LBNL_DATA, 'verified': True},
        'pjm_capacity_cost_cents_per_kwh_all_load': {**PJM_CAP_CENTS, 'source': LBNL_DATA + ' (tab: PJM capacity prices; from PJM IMM Q3-2025 State of the Market)', 'verified': True},
        'rule_of_thumb': 'At ~$330/MW-day, capacity is roughly 2 c/kWh averaged over all PJM load (~$20 on a 1,000 kWh bill); residential load is peakier than average, so the residential share can be higher. Pepco DC example: +1.7 c/kWh, +$10/mo (+9%) from the 2025/26 auction (Synapse for DC OPC).',
    },
    'utilities': U,
}
out = os.path.join(ROOT, 'data/processed/bills_anatomy.json')
json.dump(doc, open(out, 'w'), indent=1)
print('wrote', out, len(U), 'utilities')
for u in U:
    print(f"{u['utility'][:40]:40s} total={u['total_usd_at_1000kwh']} c/kWh={u['implied_cents_per_kwh']} eia={u.get('eia861m_check', {}).get('avg_revenue_cents_per_kwh')} cats={u['by_category_usd']}")
