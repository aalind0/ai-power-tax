"""Build data/processed/policy_rate_cases.json.

Backbone: EEI "Rate Review" quarterly workbook (2026 Q3; data from S&P Global RRA), downloaded by
  node scripts/policy/fetch.mjs eei_rate_review_2026q3 <url>
Enrichment (residential impact, hearings, data-center mentions, decisions after 9/30/2026) is hand-curated
from sources checked on 2026-11-23 (see research/policy/SOURCES.md). Unknown -> None.

Run from ai-power-tax/:  python3 -I scripts/policy/build_policy_rate_cases.py
"""
import csv
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, 'data', 'raw', 'policy', 'eei_rate_review_2026q3', '2026_Q3_Rate_Review_XLSX.xlsx')
PL_CSV = os.path.join(ROOT, 'data', 'processed', 'policy_rate_requests_powerlines.csv')
OUT = os.path.join(ROOT, 'data', 'processed', 'policy_rate_cases.json')
EEI_URL = 'https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/Quarterly-Financial-Updates/2026_Q3_Rate_Review_XLSX.xlsx'

df = pd.read_excel(XLSX, 'All Rate Cases 2026Q3', header=2, engine='openpyxl').iloc[:, :20]
df.columns = ['status', 'state', 'company', 'ticker', 'docket', 'service', 'case_type', 'req_date', 'req_musd', 'req_ror',
              'req_roe', 'req_eq', 'req_rb', 'auth_date', 'auth_musd', 'auth_ror', 'auth_roe', 'auth_eq', 'auth_rb', 'months']
df = df[df.service == 'Electric']


def cpuc(p):
    return 'https://apps.cpuc.ca.gov/apex/f?p=401:56::::RP,57,RIR:P5_PROCEEDING_SELECT:' + p


def nydps(c):
    return 'https://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterCaseNo=' + c


def puco(c):
    return 'https://dis.puc.state.oh.us/CaseRecord.aspx?CaseNo=' + c


# docket (as in EEI) -> enrichment
E = {
    'D-20250011-EI': dict(utility='Florida Power & Light', state='FL', data_center_cited=True,
        dc_note='Case created Large Load Contract Service tariffs (LLCS-1/2) for >=50 MW, >=85% load factor customers.',
        docket_url='https://www.floridapsc.com/', residential=None, hearings=None, verified=True),
    'C-25-E-0072': dict(utility='Consolidated Edison (electric)', state='NY', data_center_cited=False, docket_url=nydps('25-E-0072'),
        residential=None, notes='EEI/RRA authorized figure is the first-year increase of a multi-year plan.', verified=True),
    'D-UE-260005': dict(utility='Puget Sound Energy (electric)', state='WA', data_center_cited=None, docket_url='https://www.utc.wa.gov/casedocket/2026/260005',
        residential='PSE: overall electric +15.15% ($625.3M net) from Jan 2027; typical residential +17.75% / ~+$28/month at 800 kWh in 2027, ~+$7 in 2028, ~+$16 in 2029',
        hearings='UTC has up to 11 months from Feb 27, 2026 filing (decision due ~Jan 2027); public comment hearing noticed by PSE (date UNVERIFIED)',
        notes='EEI lists $1,236M requested (multi-year/total); PSE notice-of-intent docket UE-260005 was consolidated into a parent case (Apr 20, 2026).',
        source='https://www.pse.com/en/pages/rates/pending-utc-filings/2026-general-rate-case', verified=True),
    'A-25-05-009 (Elec)': dict(utility='Pacific Gas & Electric (2027 GRC, electric)', state='CA', data_center_cited=None, docket_url=cpuc('A2505009'),
        notes='Residential impact not checked this session.', verified=False),
    'C-PUR-2025-00058': dict(utility='Dominion Energy Virginia (biennial review)', state='VA', data_center_cited=True,
        dc_note='Order created GS-5 large-load class (>=25 MW) with 14-year contracts and minimum demand charges, effective 2027.',
        residential='Base rates: +$11.24/month in 2026 and +$2.36/month in 2027 for the average household (separate fuel factor + securitization adds ~$7.97 + $2.26/month from July 2026)',
        docket_url='https://www.scc.virginia.gov/docketsearch', source='https://cardinalnews.org/2025/11/26/regulators-approve-dominion-energy-rate-increase/', verified=True),
    'D-E-2 Sub 1380': dict(utility='Duke Energy Progress (NC)', state='NC', data_center_cited=True,
        dc_note='NCUC order (Nov 17, 2026) requires a new rate schedule for data centers >50 MW and upfront payments for infrastructure.',
        residential='Settlement: +3.7% (yr1) and +3.1% (yr2) average across classes (NC DOJ: ~9.3% for residential over two years); typical 1,000 kWh bill +$9.62/month in 2027 and +$5.89 in 2028',
        hearings='Evidentiary hearing Aug 2026; decided Nov 17, 2026', decided='2026-11-17', status_override='Decided (approved per settlement)',
        source='https://www.axios.com/local/raleigh/2026/11/17/nc-regulators-approve-duke-energy-rate-increase', verified=True),
    'D-E-7 Sub 1329': dict(utility='Duke Energy Carolinas (NC)', state='NC', data_center_cited=True,
        dc_note='Same Nov 17, 2026 order: data-center rate schedule >50 MW; Duke says data centers will pay for delivering service to their sites.',
        residential='Settlement cut residential request from ~18% over two years (11.9% + 4%) to ~9.5% (5.9% + 3.6%); typical 1,000 kWh bill +$6.53/month in 2027 and +$4.66 in 2028',
        hearings='Settlement hearing July 2026; decided Nov 17, 2026', decided='2026-11-17', status_override='Decided (approved per settlement)',
        source='https://www.axios.com/local/raleigh/2026/11/17/nc-regulators-approve-duke-energy-rate-increase', verified=True),
    'D-58306': dict(utility='Oncor Electric Delivery (wires-only TDU)', state='TX', data_center_cited=True,
        dc_note='Oncor cites load growth incl. data centers; a separate ~$1.2B request (Apr 2026, PowerLines) tied to a $45B 5-year T&D plan for Permian oil/gas and data-center demand.',
        docket_url='https://interchange.puc.texas.gov/search/dockets/?UtilityType=A&ControlNumber=58306', verified=True),
    'D-E-01345A-25-0105': dict(utility='Arizona Public Service', state='AZ', data_center_cited=True,
        dc_note='Proposes >45% increase for data centers via Extra High Load Factor (XHLF) changes and new cost allocation; also a Formula Rate Adjustment Mechanism.',
        residential='APS: net base increase ~$579.5M (~14%); Consumer Reports estimated ~16% residential (~$240/year)',
        hearings='Hearing May 18-July 7, 2026 (31 days); ALJ recommended order due late Nov 2026; Commission vote deadline Dec 31, 2026; new rates early 2027',
        comment_deadline='Public comments accepted until the Commission votes (by Dec 31, 2026)',
        source='https://azcc.gov/news/home/2026/07/10/what-s-next-in-the-aps-rate-case', docket_url='https://edocket.azcc.gov/', verified=True),
    'Ca-PUD2025-000075': dict(utility='Public Service Co. of Oklahoma (AEP)', state='OK', data_center_cited=True,
        dc_note='Order creates a new large-load tariff for data centers and other big users (details under study).',
        residential='Requested ~15% (~$25/month average residential); Commission approved 3.55% (2-1), rejecting a settlement that would have held residential to ~1%',
        decided='2026-11-05', status_override='Decided', source='https://gcn.com/?p=23300', verified=True),
    'C-U-21860': dict(utility='DTE Electric (2025 case)', state='MI', data_center_cited=False,
        residential='+$4.93/month (4.6%) for a typical 500 kWh customer', source='https://www.michigan.gov/mpsc/commission/news-releases/2026/02/19/commission-approves-additional-242m-for-dte-electric-grid-upgrades', verified=True),
    'C-U-22046': dict(utility='DTE Electric (2026 case)', state='MI', data_center_cited=True,
        dc_note='DTE offered to pause rate requests for 2 years if the case is "constructive" and its Saline Twp. data center (Oracle/OpenAI) is online by end-2027; AG called it a "ransom note". Case excludes data-center contract costs.',
        residential='DTE: ~9.7% typical residential; AG Nessel proposes cap of $134.5M (~2% residential)', hearings='Final order expected ~late Feb 2027',
        source='https://www.michigan.gov/ag/news/press-releases/2026/08/28/ag-nessel-seeks-to-slash-dtes-474-million-rate-hike-request-by-71', verified=True),
    'C-U-21870': dict(utility='Consumers Energy (2025 case)', state='MI', data_center_cited=None, verified=True),
    'C-U-22070': dict(utility='Consumers Energy (2026 case)', state='MI', data_center_cited=True,
        dc_note='Cost allocation to large loads such as AI data centers expected to be scrutinized (Consumers\' 100 MW / 15-year data-center tariff approved Nov 2025).', verified=False),
    'D-25AL-0494E': dict(utility='Public Service Co. of Colorado (Xcel)', state='CO', data_center_cited=None,
        docket_url='https://www.dora.state.co.us/pls/efi/EFI.Show_Docket?p_session_id=&p_docket_id=25AL-0494E', verified=True),
    'C-25-0392-EL-AIR': dict(utility='AEP Ohio (Ohio Power) distribution case', state='OH', data_center_cited=True,
        dc_note='Data-center costs handled in separate Schedule DCT; EEI says the settlement lowers average residential distribution charges ~$1.22/month (industry claim, conflicts with EEI/RRA authorized $320M figure - check order).',
        docket_url=puco('25-0392-EL-AIR'), verified=False),
    'D-R-2026-3060859': dict(utility='PECO Energy (electric)', state='PA', data_center_cited=None, docket_url='https://www.puc.pa.gov/docket/R-2026-3060859',
        status_override='Pending (EEI lists an Apr 30, 2026 action with no amount - likely the PUC suspension order; verify)', verified=False),
    'D-R-2025-3057164': dict(utility='PPL Electric Utilities', state='PA', data_center_cited=True,
        dc_note='Settlement included a large-load tariff (EEI).', docket_url='https://www.puc.pa.gov/docket/R-2025-3057164', verified=True),
    'D-ER26080420': dict(utility='Jersey Central Power & Light (FirstEnergy)', state='NJ', data_center_cited=False,
        residential='~8.8% average residential total-bill increase (incl. $476M deferred storm costs over 10 years); offsets keep impact off bills until 2028',
        notes='Largest Q3 2026 request nationally per PowerLines; NJ regulators under governor directive to consider pausing increases.',
        source='https://www.utilitydive.com/news/q3-electric-gas-rate-requests-powerlines-analysis/832609/', verified=True),
    'C-9888': dict(utility='Baltimore Gas & Electric (electric)', state='MD', data_center_cited=None, docket_url='https://webpscxb.psc.state.md.us/DMS/case/9888', verified=False),
    'C-9820': dict(utility='Pepco (Maryland)', state='MD', data_center_cited=None, docket_url='https://webpscxb.psc.state.md.us/DMS/case/9820', verified=False),
    'C-ER-2026-0291': dict(utility='Ameren Missouri (Union Electric)', state='MO', data_center_cited=True,
        dc_note='A state lawmaker asked the PSC to ensure residents do not subsidize data centers; Ameren sought confidentiality for forthcoming data-center customers and says data centers are not driving the increase.',
        residential='~+$13.00/month for average residential customer (~1,011 kWh)', hearings='PSC typically decides within 11 months of the June 26, 2026 filing (~May 2027); local public hearings held (dates UNVERIFIED)',
        docket_url='https://efis.psc.mo.gov/Case/Display/105725', source='https://ameren.mediaroom.com/2026-06-26-Storm-hardening,-electric-grid-upgrades-and-new-generation-underpin-request-to-update-electric-rates-in-mid-2027', verified=True),
    'D-5-UR-112 (Elec)': dict(utility='Wisconsin Electric Power (We Energies)', state='WI', data_center_cited=True,
        dc_note='Utility says data centers will pay ~$1.9B in 2027-28 for infrastructure and energy; PSC blocked adding data-center costs on top of ~$1B retired-plant debt (Wisconsin Watch).',
        residential='PSC approved base electric +3.9% (2027) and +3.5% (2028) vs 4.6%/4.5% requested; ROE cut 9.9% -> 9.5%; residential bills ~+$7-8/month (2027) and ~+$6-7 (2028)',
        decided='2026-11-05', status_override='Decided', docket_url='https://apps.psc.wi.gov/APPS/dockets/content/detail.aspx?id=5&case=UR&num=112',
        source='https://wisconsinwatch.org/2026/11/wisconsin-we-energies-customers-another-rate-hike-but-smaller-public-service-commission-regulators-utility/', verified=True),
    'Ca-46454': dict(utility='Indiana Michigan Power (AEP)', state='IN', data_center_cited=None,
        hearings='IURC hearing set Oct 8, 2026 and technical conference Oct 19, 2026 (IURC hearing lists); OUCC appeared Aug 31, 2026',
        notes='I&M is a major data-center growth utility (Amazon, Google, Microsoft settlement in Cause 46097); whether the case cites data-center load was not checked.',
        docket_url='https://iurc.portal.in.gov/', verified=True),
    'Ca-46258': dict(utility='AES Indiana', state='IN', data_center_cited=None, docket_url='https://iurc.portal.in.gov/', verified=True),
    'Ca-PUD2026-000067': dict(utility='Oklahoma Gas & Electric', state='OK', data_center_cited=True,
        dc_note='OG&E separately proposed an Extra Large Power tariff for large loads (June 17, 2026).', verified=False),
    'D-2025-325-E': dict(utility='Dominion Energy South Carolina', state='SC', data_center_cited=None, verified=True),
    'D-25-02016': dict(utility='Nevada Power (NV Energy)', state='NV', data_center_cited=None, verified=True),
    'D-25-EKCE-294-RTS (EKC/EKS)': dict(utility='Evergy Kansas Central', state='KS', data_center_cited=None, verified=True),
    'C-25-E-0375': dict(utility='New York State Electric & Gas', state='NY', data_center_cited=None, docket_url=nydps('25-E-0375'), verified=False),
    'D-26-05-10': dict(utility='Connecticut Light & Power (Eversource)', state='CT', data_center_cited=False, verified=False),
    'C-2025-00113': dict(utility='Kentucky Utilities', state='KY', data_center_cited=True,
        dc_note='Rate case approved an Extremely High Load Factor service tariff for large loads (Feb 2026).', docket_url='https://psc.ky.gov/Case/ViewCaseFilings/2025-00113', verified=True),
    'D-E-01933A-25-0103': dict(utility='Tucson Electric Power', state='AZ', data_center_cited=None,
        residential=None, notes='ACC approved ~10% net revenue increase on Nov 17, 2026 (KOLD).', decided='2026-11-17', status_override='Decided',
        source='https://kold.com/2026/11/18/tep-customers-pay-more-after-acc-approves-rate-increase', verified=True),
    'D-UE-473': dict(utility='Portland General Electric', state='OR', data_center_cited=True,
        dc_note='Filed after OPUC created Schedule 96 for >20 MW loads under the POWER Act.', verified=False),
    'C-26-0347-EL-AIR (OE)': dict(utility='FirstEnergy Ohio - Ohio Edison', state='OH', data_center_cited=None, docket_url=puco('26-0347-EL-AIR'), verified=False),
    'C-26-0347-EL-AIR (CEI)': dict(utility='FirstEnergy Ohio - Cleveland Electric Illuminating', state='OH', data_center_cited=None, docket_url=puco('26-0347-EL-AIR'), verified=False),
}

records = []
for dk, e in E.items():
    rows = df[df.docket == dk]
    if rows.empty:
        raise SystemExit('docket not found in EEI sheet: ' + dk)
    r = rows.iloc[0]
    status = e.get('status_override') or r.status
    decided = e.get('decided') or (r.auth_date.strftime('%Y-%m-%d') if pd.notnull(r.auth_date) else None)
    rec = {
        'utility': e['utility'], 'state': e['state'], 'eei_company_name': r.company, 'ticker': r.ticker,
        'docket': dk, 'case_type': r.case_type,
        'filed_date': r.req_date.strftime('%Y-%m-%d') if pd.notnull(r.req_date) else None,
        'requested_increase_usd': round(float(r.req_musd) * 1e6) if pd.notnull(r.req_musd) else None,
        'requested_roe_pct': float(r.req_roe) if pd.notnull(r.req_roe) else None,
        'requested_pct_residential': e.get('residential'),
        'approved_increase_usd': round(float(r.auth_musd) * 1e6) if pd.notnull(r.auth_musd) else None,
        'approved_roe_pct': float(r.auth_roe) if pd.notnull(r.auth_roe) else None,
        'decision_date': decided,
        'status': status,
        'hearings_and_deadlines': e.get('hearings'),
        'public_comment_deadline': e.get('comment_deadline'),
        'docket_url': e.get('docket_url'),
        'data_center_cited': e.get('data_center_cited'),
        'data_center_note': e.get('dc_note'),
        'notes': e.get('notes'),
        'sources': [s for s in [EEI_URL, e.get('source')] if s],
        'verified': bool(e.get('verified')),
    }
    records.append(rec)

# Utilities with no 2025-26 base-rate case but big residential footprints (context rows)
records.append({
    'utility': 'Georgia Power', 'state': 'GA', 'eei_company_name': None, 'ticker': 'SO', 'docket': None, 'case_type': 'No base-rate case (base rates frozen through 2028)',
    'filed_date': '2026-02', 'requested_increase_usd': 912_000_000, 'requested_roe_pct': None,
    'requested_pct_residential': 'Storm-cost recovery ~$912M (Helene ~$800M) = +$4.42/month at 1,000 kWh, offset by fuel-rate cut; May 2026 stipulation nets ~-$4.04/month for average residential from June 2026',
    'approved_increase_usd': None, 'approved_roe_pct': None, 'decision_date': '2026-05-28', 'status': 'Decided (storm + fuel stipulation approved; amortized over 67 months)',
    'hearings_and_deadlines': None, 'public_comment_deadline': None, 'docket_url': 'https://psc.ga.gov/', 'data_center_cited': True,
    'data_center_note': 'Dec 2025 certification of ~10 GW new resources driven by data-center forecasts; Georgia Power backstops 2029-31 costs if data-center contracts fall short.',
    'notes': 'Not in EEI base-rate list; amounts from Inside Climate News / PSC media advisory.',
    'sources': ['https://psc.ga.gov/site/assets/files/9488/media_advisory_5_28_26_fuel_storm_stip_approval.pdf', 'https://insideclimatenews.org/news/26022026/hurricane-helene-recovery-georgia-power-bills/'],
    'verified': True})

# National aggregator totals (PowerLines)
national = {
    'aggregator': 'PowerLines "Utility Bills Are Rising" quarterly index (electric + gas investor-owned utility rate increase requests; 2016-2024 history from S&P RRA)',
    'totals': [
        {'period': '2024 full year', 'requested_usd': 15_000_000_000, 'note': 'approx., per PowerLines 2025 review'},
        {'period': '2025 full year', 'requested_usd': 31_000_000_000, 'customers_affected': 81_000_000, 'by_region_usd': {'South': 14.3e9, 'West': 6.5e9, 'Northeast': 6.5e9, 'Midwest': 3.2e9},
         'note': '"nearly $31 billion", a record; more than double 2024'},
        {'period': '2026 Q1', 'requested_usd': 9_400_000_000},
        {'period': '2026 Q2', 'requested_usd': 9_200_000_000, 'customers_affected': 56_000_000, 'note': 'record quarter; beat Q2 2025 ($7.3B)'},
        {'period': '2026 Q3', 'requested_usd': 4_500_000_000, 'customers_affected': 45_500_000, 'note': 'highest Q3 on record'},
        {'period': '2026 year to date (Q1-Q3)', 'requested_usd': 23_100_000_000},
    ],
    'approval_context': 'PowerLines: ~58% of requested amounts over the past two years were approved; outright rejections are rare.',
    'sources': ['https://powerlines.org/utilities-request-23-1-billion-in-rate-increases-through-third-quarter-of-2026/',
                'https://powerlines.org/wp-content/uploads/2026/10/PowerLines_UBAR-Q3-2026_.pdf',
                'https://powerlines.org/wp-content/uploads/2026/01/0126_PowerLines_Rising-Utility-Bills-Q4-Update-FINAL.pdf',
                'https://www.eenews.net/articles/utilities-sought-a-record-31b-in-rate-increases-last-year/'],
    'caveat': 'PowerLines is a consumer-education nonprofit (advocacy); totals mix electric and gas, base cases and riders, and count requests, not approvals.',
    'verified': True,
}

# per-request table parsed from the PowerLines 2026 appendices (for the national view)
pl_rows = list(csv.DictReader(open(PL_CSV, encoding='utf-8')))
pl_sum = {}
for row in pl_rows:
    pl_sum[row['report']] = pl_sum.get(row['report'], 0) + float(row['requested_increase_busd'])
national['parsed_appendix_check_busd'] = {k: round(v, 1) for k, v in sorted(pl_sum.items())}
national['parsed_appendix_file'] = 'data/processed/policy_rate_requests_powerlines.csv'

records.sort(key=lambda x: -(x['requested_increase_usd'] or 0))
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump({'generated': '2026-11-23',
               'description': 'Recent (2025-2026) electric base-rate cases at large residential utilities, plus national rate-request totals. '
                              'Amounts are annual revenue requirement changes in USD from EEI/S&P RRA unless noted; approved figures for multi-year plans may be first-year only.',
               'national_rate_requests': national, 'cases': records}, f, indent=1, ensure_ascii=False, default=str)
print('wrote', OUT, len(records), 'cases;', sum(1 for r in records if r['data_center_cited']), 'cite data centers')
