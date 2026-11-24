"""Build data/processed/policy_states.json (50 states + DC).

Run from ai-power-tax/:  python3 -I scripts/policy/build_policy_states.py

All content is hand-curated from the sources listed in research/policy/SOURCES.md.
Rules: unknown -> None; anything not checked against a live source in the research session -> verified False
and a note in `verification_notes`. Facts marked "(UNVERIFIED)" inside text fields come from prior knowledge only.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'data', 'processed', 'policy_states.json')
CHECKED = '2026-11-23'

# ---------------------------------------------------------------- shared sources
GJF = 'https://goodjobsfirst.org/cloudy-with-a-loss-of-spending-control-how-data-centers-are-endangering-state-budgets/'
CBPP = 'https://www.cbpp.org/blog/states-began-scaling-back-expensive-subsidies-for-data-centers-in-this-years-legislative'
SPG = 'https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/091126-where-states-stand-on-data-center-sales-tax-exemptions-ahead-of-us-midterms'
EEI_LL = 'https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs'
LBNL = 'https://eta-publications.lbl.gov/sites/default/files/2026-08/rate_designs_large_loads_2026.08.10.pdf'
NASUCA = 'https://www.nasuca.org/members/'

# CBPP map (2026 sessions, as of July 2026): bills to restrict data-center subsidies
CBPP_PASSED = {'WA', 'OR', 'AZ', 'NE', 'AL', 'ME', 'NJ', 'DE'}
CBPP_FAILED = {'ID', 'SD', 'MN', 'IA', 'KS', 'WI', 'IL', 'IN', 'NY', 'PA', 'WV', 'VA', 'NC', 'SC', 'GA', 'MD', 'CT'}
CBPP_ACTIVE = {'MI', 'OH'}

# ---------------------------------------------------------------- base table
# state: (name, rto list, puc name, puc url, advocate office, advocate url)
BASE = {
    'AL': ('Alabama', ['None (SERC / Southern Co.)', 'TVA (north)'], 'Alabama Public Service Commission', 'https://psc.alabama.gov/', 'Office of the Attorney General (utility consumer interests)', 'https://www.alabamaag.gov/'),
    'AK': ('Alaska', ['None'], 'Regulatory Commission of Alaska', 'https://rca.alaska.gov/', 'Attorney General - Regulatory Affairs & Public Advocacy Section', 'https://law.alaska.gov/department/civil/civil.html'),
    'AZ': ('Arizona', ['None (WECC; CAISO Western EIM participants)'], 'Arizona Corporation Commission', 'https://www.azcc.gov/', 'Residential Utility Consumer Office (RUCO)', 'https://ruco.az.gov/'),
    'AR': ('Arkansas', ['MISO', 'SPP'], 'Arkansas Public Service Commission', 'https://apsc.arkansas.gov/', 'Office of the Attorney General (Public Protection / utilities)', 'https://www.arkansasag.gov/'),
    'CA': ('California', ['CAISO'], 'California Public Utilities Commission', 'https://www.cpuc.ca.gov/', 'Public Advocates Office (CPUC)', 'https://www.publicadvocates.cpuc.ca.gov/'),
    'CO': ('Colorado', ['None (WECC); parts of SPP'], 'Colorado Public Utilities Commission', 'https://puc.colorado.gov/', 'Office of the Utility Consumer Advocate', 'https://uca.colorado.gov/'),
    'CT': ('Connecticut', ['ISO-NE'], 'Public Utilities Regulatory Authority (PURA)', 'https://portal.ct.gov/pura', 'Office of Consumer Counsel', 'https://portal.ct.gov/OCC'),
    'DE': ('Delaware', ['PJM'], 'Delaware Public Service Commission', 'https://depsc.delaware.gov/', 'Division of the Public Advocate', 'https://publicadvocate.delaware.gov/'),
    'DC': ('District of Columbia', ['PJM'], 'Public Service Commission of the District of Columbia', 'https://dcpsc.org/', "Office of the People's Counsel", 'https://opc-dc.gov/'),
    'FL': ('Florida', ['None (FRCC)'], 'Florida Public Service Commission', 'https://www.floridapsc.com/', 'Office of Public Counsel', 'https://www.floridaopc.gov/'),
    'GA': ('Georgia', ['None (SERC / Southern Co.)'], 'Georgia Public Service Commission', 'https://psc.ga.gov/', None, None),
    'HI': ('Hawaii', ['None'], 'Hawaii Public Utilities Commission', 'https://puc.hawaii.gov/', 'Division of Consumer Advocacy (DCCA)', 'https://cca.hawaii.gov/dca/'),
    'ID': ('Idaho', ['None (WECC)'], 'Idaho Public Utilities Commission', 'https://puc.idaho.gov/', None, None),
    'IL': ('Illinois', ['PJM (ComEd)', 'MISO (Ameren Illinois)'], 'Illinois Commerce Commission', 'https://www.icc.illinois.gov/', 'Citizens Utility Board (statutory nonprofit) and Attorney General Public Utilities Bureau', 'https://www.citizensutilityboard.org/'),
    'IN': ('Indiana', ['MISO', 'PJM (Indiana Michigan Power)'], 'Indiana Utility Regulatory Commission', 'https://www.in.gov/iurc/', 'Office of Utility Consumer Counselor (OUCC)', 'https://www.in.gov/oucc/'),
    'IA': ('Iowa', ['MISO', 'SPP'], 'Iowa Utilities Commission', 'https://iuc.iowa.gov/', 'Office of Consumer Advocate (Attorney General)', 'https://www.iowaattorneygeneral.gov/for-consumers/office-of-consumer-advocate-utilities/'),
    'KS': ('Kansas', ['SPP'], 'Kansas Corporation Commission', 'https://kcc.ks.gov/', "Citizens' Utility Ratepayer Board (CURB)", 'https://curb.kansas.gov/'),
    'KY': ('Kentucky', ['PJM (Kentucky Power, Duke KY, EKPC)', 'None (LG&E/KU)', 'TVA (west)'], 'Kentucky Public Service Commission', 'https://psc.ky.gov/', 'Office of the Attorney General - Office of Rate Intervention', 'https://www.ag.ky.gov/'),
    'LA': ('Louisiana', ['MISO', 'SPP (northwest)'], 'Louisiana Public Service Commission', 'https://lpsc.louisiana.gov/', None, None),
    'ME': ('Maine', ['ISO-NE'], 'Maine Public Utilities Commission', 'https://www.maine.gov/mpuc/', 'Office of the Public Advocate', 'https://www.maine.gov/meopa/'),
    'MD': ('Maryland', ['PJM'], 'Maryland Public Service Commission', 'https://www.psc.state.md.us/', "Office of People's Counsel (OPC)", 'https://opc.maryland.gov/'),
    'MA': ('Massachusetts', ['ISO-NE'], 'Department of Public Utilities', 'https://www.mass.gov/orgs/department-of-public-utilities', 'Attorney General - Office of Ratepayer Advocacy', 'https://www.mass.gov/orgs/office-of-the-attorney-general'),
    'MI': ('Michigan', ['MISO', 'PJM (southwest MI, I&M)'], 'Michigan Public Service Commission', 'https://www.michigan.gov/mpsc', 'Attorney General (utility intervention); Citizens Utility Board of Michigan (nonprofit)', 'https://www.michigan.gov/ag/'),
    'MN': ('Minnesota', ['MISO'], 'Minnesota Public Utilities Commission', 'https://mn.gov/puc/', 'Department of Commerce (Energy Resources) and Attorney General Residential Utilities Division', 'https://mn.gov/commerce/'),
    'MS': ('Mississippi', ['MISO (Entergy MS)', 'None (Mississippi Power / SERC)', 'TVA (north)'], 'Mississippi Public Service Commission', 'https://www.psc.ms.gov/', 'Mississippi Public Utilities Staff (independent agency)', 'https://www.mpus.ms.gov/'),
    'MO': ('Missouri', ['MISO (Ameren Missouri)', 'SPP (Evergy, Liberty)'], 'Missouri Public Service Commission', 'https://psc.mo.gov/', 'Office of the Public Counsel', 'https://opc.mo.gov/'),
    'MT': ('Montana', ['None (WECC)', 'MISO (MDU, east)'], 'Montana Public Service Commission', 'https://psc.mt.gov/', 'Montana Consumer Counsel', 'https://leg.mt.gov/occ/'),
    'NE': ('Nebraska', ['SPP'], 'Nebraska Power Review Board (all-public-power state; utility boards set their own rates)', 'https://powerreview.nebraska.gov/', None, None),
    'NV': ('Nevada', ['None (WECC; CAISO Western EIM)'], 'Public Utilities Commission of Nevada', 'https://puc.nv.gov/', 'Attorney General - Bureau of Consumer Protection', 'https://ag.nv.gov/About/Consumer_Protection/Bureau_of_Consumer_Protection/'),
    'NH': ('New Hampshire', ['ISO-NE'], 'New Hampshire Public Utilities Commission', 'https://www.puc.nh.gov/', 'Office of the Consumer Advocate', 'https://www.oca.nh.gov/'),
    'NJ': ('New Jersey', ['PJM'], 'New Jersey Board of Public Utilities', 'https://www.nj.gov/bpu/', 'Division of Rate Counsel', 'https://www.nj.gov/rpa/'),
    'NM': ('New Mexico', ['None (WECC)', 'SPP (east, SPS)'], 'New Mexico Public Regulation Commission', 'https://www.prc.nm.gov/', 'Office of the Attorney General', 'https://www.nmag.gov/'),
    'NY': ('New York', ['NYISO'], 'New York Public Service Commission (Department of Public Service)', 'https://dps.ny.gov/', 'Utility Intervention Unit, Department of State', 'https://dos.ny.gov/utility-intervention-unit'),
    'NC': ('North Carolina', ['None (Duke Energy)', 'PJM (Dominion NC)'], 'North Carolina Utilities Commission', 'https://www.ncuc.gov/', 'Public Staff of the NC Utilities Commission', 'https://publicstaff.nc.gov/'),
    'ND': ('North Dakota', ['MISO', 'SPP'], 'North Dakota Public Service Commission', 'https://www.psc.nd.gov/', None, None),
    'OH': ('Ohio', ['PJM'], 'Public Utilities Commission of Ohio (PUCO)', 'https://puco.ohio.gov/', "Office of the Ohio Consumers' Counsel (OCC)", 'https://www.occ.ohio.gov/'),
    'OK': ('Oklahoma', ['SPP'], 'Oklahoma Corporation Commission', 'https://oklahoma.gov/occ.html', 'Office of the Attorney General - Utility Regulation Unit', 'https://www.oag.ok.gov/'),
    'OR': ('Oregon', ['None (WECC; BPA)'], 'Oregon Public Utility Commission', 'https://www.oregon.gov/puc/', 'Citizens\' Utility Board of Oregon (statutory nonprofit)', 'https://oregoncub.org/'),
    'PA': ('Pennsylvania', ['PJM'], 'Pennsylvania Public Utility Commission', 'https://www.puc.pa.gov/', 'Office of Consumer Advocate', 'https://www.oca.pa.gov/'),
    'RI': ('Rhode Island', ['ISO-NE'], 'Rhode Island Public Utilities Commission', 'https://ripuc.ri.gov/', 'Division of Public Utilities and Carriers (advocacy section)', 'https://ripuc.ri.gov/general-information/division'),
    'SC': ('South Carolina', ['None (Duke, Dominion SC, Santee Cooper)'], 'Public Service Commission of South Carolina', 'https://psc.sc.gov/', 'Office of Regulatory Staff (ORS)', 'https://ors.sc.gov/'),
    'SD': ('South Dakota', ['SPP', 'MISO'], 'South Dakota Public Utilities Commission', 'https://puc.sd.gov/', None, None),
    'TN': ('Tennessee', ['None (TVA; not state rate-regulated)'], 'Tennessee Public Utility Commission (investor-owned only; TVA sets its own rates)', 'https://www.tn.gov/tpuc.html', 'Attorney General - Consumer Advocate Division', 'https://www.tn.gov/attorneygeneral.html'),
    'TX': ('Texas', ['ERCOT', 'SPP (Panhandle)', 'MISO (southeast)'], 'Public Utility Commission of Texas', 'https://www.puc.texas.gov/', 'Office of Public Utility Counsel (OPUC)', 'https://www.opuc.texas.gov/'),
    'UT': ('Utah', ['None (WECC)'], 'Utah Public Service Commission', 'https://psc.utah.gov/', 'Office of Consumer Services', 'https://ocs.utah.gov/'),
    'VT': ('Vermont', ['ISO-NE'], 'Vermont Public Utility Commission', 'https://puc.vermont.gov/', 'Department of Public Service (Public Advocacy Division)', 'https://publicservice.vermont.gov/'),
    'VA': ('Virginia', ['PJM'], 'State Corporation Commission (SCC)', 'https://www.scc.virginia.gov/', 'Office of the Attorney General - Division of Consumer Counsel', 'https://www.oag.state.va.us/'),
    'WA': ('Washington', ['None (WECC; BPA)'], 'Washington Utilities and Transportation Commission', 'https://www.utc.wa.gov/', 'Attorney General - Public Counsel Unit', 'https://www.atg.wa.gov/'),
    'WV': ('West Virginia', ['PJM'], 'Public Service Commission of West Virginia', 'https://www.psc.state.wv.us/', 'Consumer Advocate Division (PSC)', 'http://www.cad.state.wv.us/'),
    'WI': ('Wisconsin', ['MISO'], 'Public Service Commission of Wisconsin', 'https://psc.wi.gov/', 'Citizens Utility Board of Wisconsin (statutory nonprofit)', 'https://cubwi.org/'),
    'WY': ('Wyoming', ['None (WECC)', 'SPP (east, partial)'], 'Wyoming Public Service Commission', 'https://psc.wyo.gov/', 'Office of Consumer Advocate', 'https://oca.wyo.gov/'),
}

ADVOCATE_NOTES = {
    'GA': 'No state-funded residential utility advocate (the Consumers\' Utility Counsel was abolished, UNVERIFIED year); PSC Public Interest Advocacy Staff participates in cases; nonprofit Georgia Watch (https://www.georgiawatch.org/) intervenes.',
    'ID': 'No separate state consumer advocate; Idaho PUC staff represent the public interest; residents comment directly to the PUC.',
    'LA': 'No separate state consumer advocate; LPSC staff and outside counsel represent the public; nonprofit Alliance for Affordable Energy intervenes.',
    'NE': 'Nebraska is entirely public power (OPPD, NPPD, LES, etc.); rates are set by elected utility boards, not a state PUC. The Nebraska Public Advocate covers natural gas only.',
    'ND': 'No separate state consumer advocate; PSC staff represent the public interest.',
    'SD': 'No separate state consumer advocate; PUC staff represent the public interest.',
}


def llt(status, utilities=None, threshold=None, min_demand=None, years=None, exit_fees=None, collateral=None,
        other=None, year=None, url=None):
    return {'status': status, 'utilities': utilities or [],
            'key_terms': {'eligibility_threshold': threshold, 'minimum_demand_or_take_or_pay': min_demand,
                          'contract_years': years, 'exit_fees': exit_fees, 'collateral': collateral, 'other': other},
            'year': year, 'source_url': url}


def inc(itype, cost=None, cost_year=None, cost_basis=None, enacted=None, status_2026=None, notes=None, url=None):
    return {'type': itype, 'est_annual_cost_usd': cost, 'cost_year': cost_year, 'cost_basis': cost_basis,
            'year_enacted': enacted, 'status_2026': status_2026, 'notes': notes, 'source_url': url}


def bill(b, summary, status, url=None):
    return {'bill': b, 'summary': summary, 'status': status, 'url': url}


# ---------------------------------------------------------------- detailed entries
D = {}

D['VA'] = dict(
    large_load_tariff=llt(
        'adopted', ['Dominion Energy Virginia (Rate Schedule GS-5)', 'Appalachian Power (Large Power Service revisions)'],
        threshold='>=25 MW and >=75% load factor (GS-5); class effective Jan 1, 2027',
        min_demand='Minimum demand charges for T&D and generation (reported as 85% T&D / 60% generation - UNVERIFIED split)',
        years='14-year minimum contract (GS-5, per LBNL 2026)',
        exit_fees='Yes (exit/termination provisions) - details UNVERIFIED',
        collateral='Yes (financial-security requirements) - details UNVERIFIED',
        other=('SCC order of July 31, 2026 (Rider T-1 case) requires a mandatory contribution-in-aid-of-construction for '
               'direct-connect substations and transmission lines serving large loads, and cut the typical residential '
               'Rider T-1 increase from $2.90 to $0.94/month via a 12CP allocator with minimum-demand adjustment.'),
        year=2025, url='https://npr.brightspotcdn.com/b6/ac/706130b64d2b8eee6a9832b97e48/20251125-virginiascc-dominionenergyruling.pdf'),
    dc_tax_incentive=inc(
        'Retail sales & use tax exemption on data-center computer equipment and enabling software',
        cost=1_600_000_000, cost_year='FY2025',
        cost_basis='~$1.6B per year cited by Senate budget chair Lucas (Virginia Mercury, Mar 2026) and The Register (Jan 2026); '
                   'state-only ACFR figure $732.8M (FY2024); JLARC: $928.6M state+local+regional (FY2023).',
        enacted=2008, status_2026='kept',
        notes=('2026 budget (HB 30, passed June 22, 2026) kept the exemption after the Senate tried to repeal it, and added a '
               'first-of-its-kind tax on data-center electricity consumption (rate reported as $0.011/kWh - UNVERIFIED). '
               'Program equals ~42% of all Virginia economic-development incentive spending (GJF).'),
        url='https://news.bloomberglaw.com/environment-and-energy/virginia-lawmakers-approve-data-center-energy-tax-in-budget-deal'),
    legislation_2025_2026=[
        bill('HB 30 (2026 budget)', 'Keeps sales-tax exemption; imposes new energy-consumption tax on data centers.', 'enacted (June 2026)', 'https://news.bloomberglaw.com/environment-and-energy/virginia-lawmakers-approve-data-center-energy-tax-in-budget-deal'),
        bill('SB 253 (2026)', 'Lets the SCC shift PJM capacity-auction costs and financing costs of distribution lines/substations mainly serving data centers onto the data-center class; extends low-income weatherization.', 'passed; governor amended (critics say weakened) - final text UNVERIFIED', 'https://patch.com/virginia/across-va/data-center-bills-dominated-years-general-assembly-heres-what-passed'),
        bill('SB 94 / HB 153 (2026)', 'Site-assessment report required for rezonings for >100 MW "high load users".', 'passed (signature UNVERIFIED)', 'https://patch.com/virginia/across-va/data-center-bills-dominated-years-general-assembly-heres-what-passed'),
        bill('HB 507 (2026)', 'DEQ must deny new data-center generator air permits after July 2026 unless Tier IV or equivalent.', 'passed (signature UNVERIFIED)', 'https://patch.com/virginia/across-va/data-center-bills-dominated-years-general-assembly-heres-what-passed'),
        bill('SB 553 (2026)', 'Water utilities report aggregate data-center water use.', 'passed (signature UNVERIFIED)', 'https://patch.com/virginia/across-va/data-center-bills-dominated-years-general-assembly-heres-what-passed'),
    ],
    notes=('SCC final order in Dominion biennial review (PUR-2025-00058, Nov 25, 2025) approved a smaller base-rate increase than '
           'requested (EEI/RRA: $963M requested, $776M authorized) and created GS-5. JLARC (2024) estimated a typical Dominion '
           'residential bill could rise $14-$37/month by 2040 (real) from generation and transmission costs driven by demand growth, '
           'while also finding data centers were currently paying their cost of service.'),
    verified=True)

D['MD'] = dict(
    large_load_tariff=llt(
        'proposed', ['BGE', 'Pepco', 'Delmarva Power', 'Potomac Edison', 'SMECO'],
        threshold='Statute: originally >=100 MW and 80% load factor (Next Generation Energy Act 2025); lowered to >=25 MW and 60% load factor by the Utility RELIEF Act (HB 1532, Ch. 353 of 2026)',
        min_demand='Required by statute (specific % UNVERIFIED)', years='Minimum contract term required by statute (length UNVERIFIED)',
        exit_fees='Required by statute', collateral='Required by statute',
        other='Utilities filed large-load rate schedules Sept 1, 2026 in PSC Case PC72; OPC asks for mandatory curtailment in emergencies and binding commitments before load is sent to PJM.',
        year=2026, url='https://www.psc.state.md.us/wp-content/uploads/Notice_LargeLoadCust-PC72.pdf'),
    dc_tax_incentive=inc('Sales & use tax exemption for qualified data-center equipment', enacted=None, status_2026='kept (2026 restriction bills failed per CBPP)',
                         notes='Enactment year and cost not checked this session (UNVERIFIED).', url=CBPP),
    legislation_2025_2026=[
        bill('SB 937 / HB 1035 (2025) Next Generation Energy Act', 'Requires utilities to file specific rate schedules for large loads with minimum terms, collateral and exit fees.', 'enacted 2025 (Ch. 625)', 'https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_625_sb0937e.pdf'),
        bill('HB 1532 (2026) Utility RELIEF Act', 'Lowers the large-load threshold to 25 MW / 60% load factor; keeps tariff filing requirement.', 'enacted 2026 (Ch. 353)', 'https://mgaleg.maryland.gov/2026RS/Chapters_noln/CH_353_hb1532e.pdf'),
    ],
    notes=('Maryland imports a large share of its power and pays PJM capacity and transmission costs set regionally; '
           'OPC filed a complaint over PJM regional transmission (RTEP) cost allocation on May 7, 2026 and has argued Maryland customers '
           'pay for transmission built for data centers in other states.'),
    verified=True)

D['PA'] = dict(
    large_load_tariff=llt(
        'adopted', ['Model tariff (nonbinding) for all EDCs', 'PPL Electric (large-load tariff in rate-case settlement)'],
        threshold='>=50 MW individually or >=100 MW aggregate (utility discretion below 50 MW)',
        min_demand='Model includes minimum-bill / demand provisions (values UNVERIFIED)', years='UNVERIFIED',
        exit_fees='Included in model framework (values UNVERIFIED)', collateral='Included in model framework (values UNVERIFIED)',
        other='Final Order May 12, 2026 adopts a "but-for" approach: large loads pay for network upgrades that would not be needed without them; utilities must file their own tariffs.',
        year=2026, url='https://www.puc.pa.gov/press-release/2026/puc-releases-final-order-establishing-first-of-its-kind-large-load-model-tariff-framework-05132026'),
    dc_tax_incentive=inc('Sales & use tax exemption for computer data-center equipment', enacted=2016, status_2026='restricted by executive order',
                         notes='Aug 2026: Gov. Shapiro executive order limits the exemption to operators meeting "GRID" requirements (power, sustainability, labor, community engagement). Enactment year UNVERIFIED (Act 84 of 2016).',
                         url=SPG),
    legislation_2025_2026=[bill('2026 bills to restrict subsidies', 'Bills to restrict data-center subsidies considered.', 'failed (CBPP)', CBPP)],
    notes='PA PUC model large-load tariff is guidance; reconsideration petitions were filed (May-June 2026).',
    verified=True)

D['NJ'] = dict(
    large_load_tariff=llt(
        'proposed', ['PSE&G', 'JCP&L', 'Atlantic City Electric', 'Rockland Electric'],
        threshold='Data centers >50 MW', min_demand='Bill text: cover at least 85% of requested service (UNVERIFIED in final law)',
        years='Bill text: at least 10 years (UNVERIFIED in final law)', exit_fees='Deposits / stranded-cost protections required',
        collateral='Deposits required', other='BPU must adopt rules within 12 months of July 7, 2026; requirements can be waived if the data center provides operational flexibility or brings its own new energy and capacity.',
        year=2026, url='https://newjerseymonitor.com/2026/07/07/sherrill-signs-three-bills-to-lower-nj-electricity-costs/'),
    dc_tax_incentive=inc('Next NJ - AI data-center tax credit program (up to $500M)', enacted=2024, status_2026='paused',
                         notes='Program paused in 2026 before launch; many expect elimination (S&P). CBPP lists NJ among states where restriction legislation passed.',
                         url=SPG),
    legislation_2025_2026=[
        bill('S731 / A796 (2026)', 'Requires utilities to create tariffs for data centers >50 MW that protect other ratepayers.', 'signed July 7, 2026', 'https://www.nj.gov/governor/news/2026/20260707a.shtml'),
        bill('S1673 (2026)', 'Repeals utility ROE adder; ends payments to utilities for PJM membership (per Sierra Club summary).', 'signed July 2026', 'https://www.sierraclub.org/new-jersey/blog/2026/07/nj-sierra-club-applauds-gov-sherrill-signing-energy-affordability-bills'),
        bill('S3379 / A4096 (2026)', 'Data centers must report energy and water use every six months.', 'signed Aug 27, 2026', 'https://nj.gov/governor/news/2026/approved/20260827a.shtml'),
    ],
    notes=('Gov. Sherrill acknowledged data-center tariffs have limited effect on bills because capacity prices are set across PJM\'s '
           '13-state market; JCP&L filed a $253M distribution case plus $476M deferred storm costs (Aug 2026), ~8.8% residential bill impact from 2028.'),
    verified=True)

D['OH'] = dict(
    large_load_tariff=llt(
        'adopted', ['AEP Ohio (Schedule DCT)', 'FirstEnergy Ohio utilities (DCT proposed June 2026)', 'Duke Energy Ohio (Rate DC proposed)', 'AES Ohio (DCT in proposed settlement)'],
        threshold='New data centers >25 MW (AEP Ohio)',
        min_demand='Greater of 85% of highest demand in prior 11 months or contract-based minimum (25-75 MW: 15 MW + 85% above 25 MW; >75 MW: 57.5 MW + 100% above 75 MW), capped at 85% of contract capacity',
        years='Load ramp up to 4 years (50/65/80/90%) + 8 years (up to 12 total)',
        exit_fees='Exit fee on cancellation/reduction; up to 25% of capacity may be reassigned to another DCT customer in lieu of exit fee; Letter of Agreement requires 100% reimbursement of build-out costs if project is cancelled or delayed >12 months',
        collateral='50% of total minimum charges for the full term unless customer has A-/A3 ratings and cash >10x the requirement; surety bonds not accepted',
        other='PUCO order July 9, 2025 (Case 24-508-EL-ATA); effective July 23, 2025; new requests studied in tranches (next tranche Oct 1, 2026).',
        year=2025, url='https://www.aepohio.com/company/about/rates/data-center-tariff'),
    dc_tax_incentive=inc('100% sales-tax exemption on data-center construction materials/equipment (Tax Credit Authority)', cost=1_500_000_000, cost_year='2025',
                         cost_basis='Actual 2025 cost ~ $1.5B vs ~$136M projected (Signal Ohio data via WOSU/Fortune, May 2026); GJF had used the $127.4M budget estimate',
                         enacted=None, status_2026='paused (executive, May 27, 2026)',
                         notes='Legislature repealed the exemption in the 2025 budget; Gov. DeWine vetoed that repeal (override threatened, not confirmed). On May 27, 2026 DeWine froze new requests while a Joint Data Center Committee studies the issue.',
                         url='https://www.wosu.org/2026-05-27/gov-dewine-freezes-controversial-data-center-tax-break-for-now'),
    legislation_2025_2026=[
        bill('HB 15 (2025)', 'Energy law ending OVEC coal-plant subsidies and reforming utility electric security plans (UNVERIFIED detail).', 'enacted 2025 (UNVERIFIED)', None),
        bill('2026 subsidy restriction bills', 'Bills to restrict data-center subsidies.', 'still active as of July 2026 (CBPP)', CBPP),
    ],
    notes='Ohio Consumers\' Counsel published "Data Centers in Ohio" reports (2026). AEP Ohio says a pending distribution settlement lowers average residential distribution charges ~$1.22/month (EEI, industry claim).',
    verified=True)

D['IL'] = dict(
    large_load_tariff=llt(
        'adopted', ['ComEd (Rider DE and General Terms & Conditions revisions; FERC-approved Transmission Security Agreements)', 'Ameren Illinois (UNVERIFIED)'],
        threshold='UNVERIFIED', min_demand='UNVERIFIED', years='UNVERIFIED', exit_fees='UNVERIFIED',
        collateral='Transmission Security Agreements require large loads to secure transmission costs (industry description, EEI)',
        other='Service-rule changes rather than a full large-load rate class (per EEI list Oct 2026).', year=None, url=EEI_LL),
    dc_tax_incentive=inc('Data Center Investment Program: sales/use tax exemptions and credits', cost=370_609_085, cost_year='2023',
                         cost_basis='Illinois DCEO annual reports, via Good Jobs First (cost grew ~3,600% from 2020)', enacted=2019,
                         status_2026='paused (executive)',
                         notes='Gov. Pritzker stopped processing new agreements effective July 1, 2026 (two-year suspension proposed) after the legislature did not act in spring session.',
                         url='https://www.cbsnews.com/chicago/news/gov-jb-pritzker-suspends-data-center-tax-breaks/'),
    legislation_2025_2026=[bill('2026 spring session data-center bills', 'Proposals to pause incentives and require clean power / curtailment.', 'failed in spring session (CBPP); governor said he would revisit in veto session', CBPP)],
    notes='ComEd residential customers pay PJM capacity prices; Illinois CUB has attributed part of 2025-26 bill increases to the PJM capacity auction.',
    verified=True)

D['IN'] = dict(
    large_load_tariff=llt(
        'adopted', ['Indiana Michigan Power (Tariff I.P. modifications)', 'NIPSCO / NIPSCO GenCo (special contract with Amazon)', 'AES Indiana (Google agreement)'],
        threshold='I&M: >=70 MW single site or 150 MW aggregate (UNVERIFIED)', min_demand='I&M: 80% minimum demand (UNVERIFIED)',
        years='I&M: minimum 12 years + optional load ramp up to 5 years (IURC Cause 46097, approved Feb 2025); IURC must approve any reduction >20% of contracted capacity; NIPSCO-Amazon: 15-year special contract from Jan 2027',
        exit_fees='Yes; Amazon must pay defined costs if it terminates', collateral='Yes (UNVERIFIED details)',
        other=('IURC approved NIPSCO GenCo structure Sept 24, 2025 (Cause 46183) and the Amazon special contract + GenCo PPA on June 17, 2026 '
               '(Causes 46322/46362): two 1.3 GW gas combined-cycle units + 400 MW battery (~$7B) funded by Amazon; NIPSCO claims ~$1B savings '
               'for existing customers; Amazon has a one-time option to cut 1,200 MW by Mar 31, 2029.'),
        year=2025, url='https://www.in.gov/iurc/files/ord_46322_061726.pdf'),
    dc_tax_incentive=inc('Sales/use tax exemption (and property-tax eligibility) for qualified data-center equipment', enacted=2019,
                         status_2026='kept (2026 restriction bills failed per CBPP)',
                         notes='Indiana does not disclose foregone revenue ("dark" state per GJF); LSA called the cost indeterminable but "significant".',
                         url=GJF),
    legislation_2025_2026=[bill('HB 1007 (2025)', 'Requires large-load customers to cover a large share (reported 80%) of costs of new generation/transmission built for them (UNVERIFIED).', 'enacted 2025 (UNVERIFIED)', None)],
    notes='AES Indiana says its Google agreement will save existing customers $770M over 15 years (EEI, industry claim). PowerLines Q3 2026 spotlighted Indiana customers complaining about riders.',
    verified=True)

D['GA'] = dict(
    large_load_tariff=llt(
        'adopted', ['Georgia Power'],
        threshold='Expected peak demand >=100 MW', min_demand='Minimum billing requirements allowed', years='Longer contract terms (up to 15 years reported - UNVERIFIED)',
        exit_fees='Customer pays utility costs if it terminates', collateral='UNVERIFIED',
        other=('PSC rule adopted Jan 23, 2025. Dec 19, 2025: PSC certified ~10 GW of new resources (Dockets 56298/56310, ~$16B) with a stipulation '
               'that Georgia Power backstops 2029-2031 costs if data-center contracts do not materialize; PSC kept power to revisit certification. '
               'Base rates frozen through 2028 (2025 stipulation).'),
        year=2025, url='https://psc.ga.gov/site/assets/files/8617/media_advisory_data_centers_rule_1-23-2025.pdf'),
    dc_tax_incentive=inc('Sales & use tax exemption for high-technology data-center equipment', cost=296_000_000, cost_year='FY2025',
                         cost_basis='Georgia State Univ. Fiscal Research Center tax-expenditure report (state+local; local share $136M), via GJF',
                         enacted=2018, status_2026='kept',
                         notes='HB 1192 (2024) to pause the exemption was vetoed by Gov. Kemp; 2026 repeal bills failed.', url=GJF),
    legislation_2025_2026=[bill('2026 repeal bills', 'Several bills to eliminate the statutory sales-tax exemption.', 'failed', SPG)],
    notes='Two PSC challengers (Alicia Johnson, Peter Hubbard) won Nov 2025 elections on affordability; a Feb 2026 motion to reopen the 10 GW certification failed. PSC staff warned much of the load forecast was speculative.',
    verified=True)

D['TX'] = dict(
    large_load_tariff=llt(
        'adopted', ['Statewide ERCOT rules under SB 6 (all TDUs)', 'El Paso Electric (Schedules 33A/33B; Schedule 27 proposed)', 'SWEPCO (ES-LL contract proposed)', 'Xcel/SPS (proposed)'],
        threshold='New or expanded load >=75 MW at one site',
        min_demand='Not a take-or-pay tariff; financial-security and disclosure requirements instead',
        years=None, exit_fees=None,
        collateral='Financial commitment / security required for interconnection studies (study fee proposed $100k for 75-249 MW, $300k for >=250 MW)',
        other=('SB 6 (2025): disclosure of duplicate requests and on-site backup generation; new large loads interconnected after 2025 can be '
               'curtailed/remotely disconnected in firm load shed; PUCT to review transmission cost allocation. PUCT adopted large-load '
               'interconnection rule 16 TAC 25.194 (Project 58481) Sept 18, 2026 (per White & Case; UNVERIFIED against order). '
               'Aug 3, 2026: Gov. Abbott ordered an audit of all data centers in the ERCOT queue (~474 GW of requests, ~90% data centers); ERCOT delayed its "Batch Zero" study.'),
        year=2025, url='https://www.utilitydive.com/news/texas-hits-pause-data-center-interconnections/827046/'),
    dc_tax_incentive=inc('Sales & use tax exemption for qualifying data centers (incl. electricity)', cost=1_015_600_000, cost_year='FY2025',
                         cost_basis='Texas Comptroller "Tax Exemptions & Tax Incidence" (Jan 2025), via GJF; projected $1.7B in 2030',
                         enacted=2013, status_2026='kept', notes='Comptroller raised its FY2025 estimate from ~$130M (2023 report) to $1B within 23 months. Local taxes excluded from the state exemption (CBPP).', url=GJF),
    legislation_2025_2026=[bill('SB 6 (2025)', 'Large-load interconnection standards, curtailment, cost-allocation review.', 'enacted June 2025', 'https://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=SB6')],
    notes='ERCOT is an energy-only market with retail choice; transmission costs are allocated by 4CP, which SB 6 asked the PUCT to revisit. Oncor requested $1.2B (2026) citing Permian oil/gas and data-center load.',
    verified=True)

D['AZ'] = dict(
    large_load_tariff=llt(
        'proposed', ['Arizona Public Service (XHLF tariff changes in rate case E-01345A-25-0105)', 'Tucson Electric Power (UNVERIFIED)', 'SRP (public power; not ACC-regulated)'],
        threshold='Extra-high load factor customers (UNVERIFIED MW)', other='APS proposed a ~2,000 MW gas plant partly offered to large loads under a subscription model (EEI).',
        year=2025, url=EEI_LL),
    dc_tax_incentive=inc('Computer Data Center program: sales tax exemption on qualified equipment', cost=19_000_000, cost_year='FY2024',
                         cost_basis='Arizona Dept. of Revenue tax-expenditure report, via GJF (up from $1.4M in 2020)', enacted=2017,
                         status_2026='paused (3-year moratorium)', notes='State budget signed by Gov. Hobbs includes a three-year moratorium on the exemption (S&P, 2026).', url=SPG),
    legislation_2025_2026=[bill('FY2027 budget (2026)', 'Three-year moratorium on the data-center sales-tax exemption.', 'enacted 2026', SPG)],
    notes='APS seeks ~$580M net (~14%; ~16% residential per Consumer Reports) incl. >45% increase for data centers; ALJ recommendation due late Nov 2026, ACC vote by Dec 31, 2026. ACC approved ~10% for TEP on Nov 17, 2026.',
    verified=True)

D['OR'] = dict(
    large_load_tariff=llt(
        'adopted', ['Portland General Electric (Schedule 96)', 'PacifiCorp (Schedule 401 proposed, UE 463)'],
        threshold='>20 MW (HB 3546 POWER Act)', min_demand='UNVERIFIED', years='Multi-year contracts required by statute (length UNVERIFIED)',
        exit_fees='UNVERIFIED', collateral='UNVERIFIED',
        other=('OPUC Order 26-154 (UM 2377, May 7, 2026): large loads pay 100% of distribution network upgrades; interconnection tied to '
               'availability of clean resources under HB 2021; PGE estimated +29% for data-center class with decreases for other classes (filed proposal).'),
        year=2026, url='https://apps.puc.state.or.us/orders/2026ords/26-154.pdf'),
    dc_tax_incentive=inc('Local enterprise-zone property tax abatements (incl. long-term rural enterprise zones)', enacted=None,
                         status_2026='paused pending study (CBPP)', notes='Oregon has no sales tax; 2026 legislation paused subsidies pending study (CBPP). Details UNVERIFIED.', url=CBPP),
    legislation_2025_2026=[bill('HB 3546 (2025) POWER Act', 'Creates a separate rate class for >20 MW loads so costs are not shifted to residents.', 'enacted June 2025', 'https://olis.oregonlegislature.gov/liz/2025R1/Measures/Overview/HB3546')],
    notes='First state law requiring a separate large-load class; OPUC 2026 POWER Act report says a related investigation should conclude late 2026.',
    verified=True)

D['NV'] = dict(
    large_load_tariff=llt('none', ['NV Energy (Clean Transition Tariff - opt-in clean-supply tariff, not a cost-protection large-load tariff)'],
                          other='No general large-load cost-protection tariff found in EEI Oct 2026 list.', year=2025, url=EEI_LL),
    dc_tax_incentive=inc('Partial sales/use and property tax abatements for data centers (GOED)', cost=139_968_442, cost_year='FY2024',
                         cost_basis='Nevada Dept. of Taxation tax-expenditure report, via GJF', enacted=2015, status_2026='kept',
                         notes='Enactment year UNVERIFIED.', url=GJF),
    legislation_2025_2026=[],
    notes='Nevada Power base case: $203.5M requested, $118.2M authorized (Sept 2025, EEI/RRA).',
    verified=False)

D['NC'] = dict(
    large_load_tariff=llt('adopted', ['Duke Energy Carolinas', 'Duke Energy Progress'], threshold='Data centers >50 MW',
                          other=('NCUC order of Nov 17, 2026 in rate cases E-7 Sub 1329 / E-2 Sub 1380 requires Duke to establish a new rate schedule for '
                                 'data centers >50 MW plus upfront payments for infrastructure upgrades, building on a stipulated large-load tariff; detailed terms pending compliance filing.'),
                          year=2026, url='https://www.axios.com/local/raleigh/2026/11/17/nc-regulators-approve-duke-energy-rate-increase'),
    dc_tax_incentive=inc('Sales-tax exemptions for qualifying data centers (electricity and equipment)', cost=20_000_000, cost_year='annual (electricity portion)',
                         cost_basis='NC Dept. of Commerce estimate of electricity-related exemption, via S&P', enacted=None,
                         status_2026='partially repealed (electricity exemption)',
                         notes='2026: legislature repealed the exemption on data-center electricity (now taxed at combined 7%); Gov. Stein called for full repeal at end of 2032. CBPP lists the broader repeal bill as failed/rewritten. NC is a non-disclosing state (GJF).',
                         url=SPG),
    legislation_2025_2026=[bill('2026 data-center electricity sales-tax repeal', 'Ends sales-tax exemption on electricity bought by data centers.', 'enacted 2026', SPG)],
    notes='NCUC approved Duke Energy Carolinas/Progress base increases on Nov 17, 2026 (~4.7%/yr residential over two years; ~9.5% total for DEC vs ~18% originally sought).',
    verified=True)

D['SC'] = dict(
    large_load_tariff=llt('proposed', ['Duke Energy Carolinas', 'Duke Energy Progress', 'Dominion Energy SC (UNVERIFIED)', 'Santee Cooper (UNVERIFIED)'],
                          threshold='>=50 MW (generic docket scope)', other='Large-load stipulations in 2025 rate cases led to a generic PSC docket on new large loads (EEI).',
                          year=2025, url=EEI_LL),
    dc_tax_incentive=inc('Sales-tax exemption for data-center equipment and electricity (UNVERIFIED scope)', status_2026='kept (2026 restriction bills failed per CBPP)', url=CBPP),
    legislation_2025_2026=[bill('H.3309 (2025) Energy Security Act', 'Omnibus energy law incl. new gas generation; large-load provisions UNVERIFIED.', 'enacted 2025 (UNVERIFIED)', None)],
    notes='', verified=False)

D['LA'] = dict(
    large_load_tariff=llt('adopted', ['Entergy Louisiana (Large Load High Load Factor Power Service)'],
                          threshold='>=70 MW firm load and >=80% average monthly load factor', years='Minimum contract 5 years (LBNL)',
                          other=('LPSC approved (4-1, Aug 20, 2025, Docket U-37425) three gas plants totaling 2,262 MW (~$3.2B) plus a 500-kV line for Meta\'s Richland Parish campus; '
                                 'PSC staff say Meta minimum bills cover 100% of the three generators; Alliance for Affordable Energy disputes that residents are shielded.'),
                          year=2025, url='https://lailluminator.com/2025/08/20/entergy-meta/'),
    dc_tax_incentive=inc('Sales/use tax rebate for large data-center investments (Act 730 of 2024 - UNVERIFIED)', status_2026='kept (UNVERIFIED)'),
    legislation_2025_2026=[], notes='Approval was fast-tracked ahead of the ALJ recommendation, drawing objections from ratepayer groups.', verified=True)

D['MS'] = dict(
    large_load_tariff=llt('none', ['Special contracts only (RPP Rule 27, PSC approval)'], other='Large-load terms handled via PSC-approved special contracts.', url=EEI_LL),
    dc_tax_incentive=inc('Sales/use and property tax exemptions; income-tax exemption for data-center profits (GJF)', status_2026='kept (UNVERIFIED)', url=GJF),
    legislation_2025_2026=[], notes='', verified=False)

D['WI'] = dict(
    large_load_tariff=llt('adopted', ['We Energies (Very Large Customer + Bespoke Resources tariffs, Docket 6630-TE-113)', 'Xcel/NSP-W (proposed)', 'Madison Gas & Electric (proposed)', 'Wisconsin Power & Light (Cp-3 proposed)'],
                          threshold='Conflicting reports: proposal >500 MW (250-500 MW opt-in); Clean Wisconsin says PSC lowered to 100 MW mandatory (UNVERIFIED)',
                          years='15 years (PSC extended from 10)', other='PSC approved with modifications Apr 24, 2026; added charges when data centers exceed subscribed capacity.',
                          year=2026, url='https://content.govdelivery.com/accounts/WIPSC/bulletins/4147a70'),
    dc_tax_incentive=inc('Sales/use tax exemption for qualified data-center equipment (2023 Act 19 - UNVERIFIED)', status_2026='kept (2026 restriction bills failed per CBPP)', url=CBPP),
    legislation_2025_2026=[], notes='PSC approved We Energies base electric increases of 3.9% (2027) and 3.5% (2028) on Nov 5, 2026 (requested 4.6%/4.5%); utility says data centers will pay ~$1.9B in 2027-28.', verified=True)

D['MN'] = dict(
    large_load_tariff=llt('adopted', ['Xcel/NSP (Large General Time of Day Service, >=100 MW)', 'Minnesota Power (Very Large Power class proposed July 2026)', 'Otter Tail Power (Tier III HPC proposed May 2026)'],
                          threshold='>=100 MW (Xcel)', other='2025 state law required new large-customer classes (UNVERIFIED citation).', year=None, url=EEI_LL),
    dc_tax_incentive=inc('Sales/use tax exemption for data-center equipment and software', cost=114_200_000, cost_year='2025',
                         cost_basis='Minnesota DOR tax-expenditure budget, via GJF', enacted=None, status_2026='scaled back (electricity exemption repealed 2025)',
                         notes='HF 9 (signed June 14, 2025) repealed the exemption for electricity after June 30, 2025 and kept/extended equipment exemption; 2026 full-repeal bill (HF 5125) did not pass (CBPP lists MN as failed; S&P lists MN as repealed - conflict).',
                         url='https://taxnews.ey.com/news/2025-1349'),
    legislation_2025_2026=[bill('HF 9 (2025)', 'Omnibus tax law: repeals data-center electricity exemption; modifies equipment exemption.', 'enacted June 2025', 'https://taxnews.ey.com/news/2025-1349'),
                           bill('HF 5125 (2026)', 'Would repeal data-center exemption entirely.', 'introduced; not enacted', 'https://www.revisor.mn.gov/bills/94/2026/0/HF/5125/')],
    notes='', verified=True)

D['IA'] = dict(
    large_load_tariff=llt('adopted', ['Alliant/Interstate Power & Light (Rider Individual Customer Rate agreements, e.g. QTS, Vulpine)'], url=EEI_LL),
    dc_tax_incentive=inc('Sales/use tax refunds and property-tax exemptions for data centers', cost=151_100_000, cost_year='2020',
                         cost_basis='Iowa DOR 2020 tax-expenditure study (pre-AI boom), via GJF', status_2026='kept (2026 restriction bills failed; reporting bill proposed)', url=GJF),
    legislation_2025_2026=[], notes='Alliant says data-center growth supports a 5-year base-rate freeze in Iowa (EEI, industry claim).', verified=True)

D['NE'] = dict(
    large_load_tariff=llt('none', ['Public power districts set terms (OPPD, NPPD, LES) - no state PUC tariff'], other='No state-level large-load tariff; check local utility board rate schedules.'),
    dc_tax_incentive=inc('Data-center sales-tax exemptions (Nebraska Advantage / ImagiNE Act)', status_2026='repealed (2026) + governor blocked access via ImagiNE',
                         notes='S&P lists Nebraska among states that repealed data-center sales-tax exemptions (May-Aug 2026), though one source says the repeal covers only equipment for out-of-state facilities; a July 2026 executive order by Gov. Pillen ended data-center access to ImagiNE Nebraska Act incentives. Bill number UNVERIFIED.', url=SPG),
    legislation_2025_2026=[bill('2026 repeal (bill number and scope UNVERIFIED)', 'Repeals a data-center sales-tax exemption.', 'enacted 2026', SPG),
                           bill('Executive order (July 2026)', 'Ends data-center access to ImagiNE Nebraska Act incentives.', 'in effect', CBPP)],
    notes=ADVOCATE_NOTES['NE'], verified=True)

D['WY'] = dict(
    large_load_tariff=llt('adopted', ['Black Hills Energy / Cheyenne Light (Large Power Contract Service, LPCS)'],
                          other='Approved 2016 with Microsoft: dedicated energy procurement (market + PPAs); customers cover capacity (customer- or utility-owned backup generation) and fund incremental T&D.',
                          year=2016, url=EEI_LL),
    dc_tax_incentive=inc('Sales/use tax exemption for data-center equipment', cost=22_600_000, cost_year='2023 (local share only)',
                         cost_basis='Wyoming LSO one-time memo (May 2024), via GJF', status_2026='kept (UNVERIFIED)', url=GJF),
    legislation_2025_2026=[], notes='', verified=True)

D['NY'] = dict(
    large_load_tariff=llt('none', [], other='No large-load tariff found in EEI list; NYISO large-load queue grew to 48 proposals (~12 GW) by end-2025.',
                          url='https://www.utilitydive.com/news/behind-the-new-york-data-center-pause-is-legislation-that-could-impact-exis/826369/'),
    dc_tax_incentive=inc('No data-center-specific sales-tax exemption (general programs such as Excelsior apply - UNVERIFIED)', status_2026='2026 restriction/cap bills failed (CBPP)'),
    legislation_2025_2026=[
        bill('Executive Order (July 14, 2026)', 'Pauses state environmental permits for new data centers >=50 MW for up to one year pending a DPS Generic Environmental Impact Statement.', 'in effect', 'https://www.utilitydive.com/news/behind-the-new-york-data-center-pause-is-legislation-that-could-impact-exis/826369/'),
        bill('A11560 Responsible Data Center Development Act', 'Renewable procurement (>=1/3 by 2030 for >=5 MW), efficiency standards, host-community benefits for large new data centers.', 'passed legislature June 4, 2026; unsigned as of July 28, 2026', 'https://www.utilitydive.com/news/behind-the-new-york-data-center-pause-is-legislation-that-could-impact-exis/826369/'),
    ],
    notes='First state moratorium on new hyperscale data centers. Con Edison case: $1.61B requested, $222M first-year increase authorized (Jan 2026, EEI/RRA).', verified=True)

D['DE'] = dict(
    large_load_tariff=llt('proposed', ['Delmarva Power (General Service Large Load, >=50 MW)'], threshold='>=50 MW',
                          other='Filed in line with a Nov 2025 PSC order; Aug 2026 law creates a separate rate class for large energy-use facilities with bring-your-own-generation.',
                          year=2026, url=EEI_LL),
    dc_tax_incentive=inc('No data-center-specific exemption; 2026 law bars large energy users from job-creation business tax credits', status_2026='restricted', url=SPG),
    legislation_2025_2026=[bill('Aug 2026 consumer-protection package (bill numbers UNVERIFIED)', 'Large users pay own infrastructure; separate rate class; bring-your-own-generation; no job-creation tax credits.', 'signed Aug 2026', SPG)],
    notes='Triggered by a multi-GW data-center proposal (UNVERIFIED name).', verified=True)

D['ME'] = dict(
    large_load_tariff=llt('none'),
    dc_tax_incentive=inc('Data-center tax subsidies (incl. business equipment tax exemption)', status_2026='repealed (2026)', notes='Only state to fully repeal all available data-center tax subsidies in 2026 (CBPP).', url=CBPP),
    legislation_2025_2026=[bill('LD 713 (2026)', 'Removes new data centers from eligibility for state tax incentives (incl. business equipment tax exemption).', 'signed Apr 23, 2026 (per Brownstein tracker)', 'https://www.bhfs.com/data-center-tracker/maine/'),
                           bill('LD 307 (2026)', 'Statewide data-center moratorium.', 'vetoed Apr 24, 2026', 'https://www.bhfs.com/data-center-tracker/maine/')], notes='', verified=True)

D['WA'] = dict(
    large_load_tariff=llt('none'),
    dc_tax_incentive=inc('Sales/use tax exemptions for data centers (urban and rural programs)', cost=112_130_000, cost_year='2025',
                         cost_basis='WA DOR 2024 Tax Exemption Study, via GJF (local share $26M)', status_2026='restricted (2026 legislation passed per CBPP; details UNVERIFIED)', url=CBPP),
    legislation_2025_2026=[bill('2026 subsidy restriction (bill number UNVERIFIED)', 'Restricts data-center subsidies.', 'enacted 2026 (CBPP)', CBPP)],
    notes='Gov. Ferguson created a data-center workgroup in 2025. Puget Sound Energy requested ~$1.24B (Feb 2026, EEI/RRA).', verified=True)

D['AL'] = dict(
    large_load_tariff=llt('adopted', ['Alabama Power (Rate BTAL modification: >30 MW customers via special contract)'], threshold='>30 MW', year=2025, url=EEI_LL,
                          other='APSC approved Jan 7, 2025; contract terms (minimum bills, exit fees, collateral) set case by case.'),
    dc_tax_incentive=inc('Data-processing-center tax abatements (UNVERIFIED scope)', status_2026='tightened (2026: shorter time limits to use subsidies, CBPP)', url=CBPP),
    legislation_2025_2026=[bill('2026 subsidy time-limit law (bill number UNVERIFIED)', 'Tightens time limits for using data-center subsidies.', 'enacted 2026 (CBPP)', CBPP)], notes='', verified=True)

D['FL'] = dict(
    large_load_tariff=llt('adopted', ['FPL (LLCS-1 and LLCS-2)', 'Duke Energy Florida (proposal under SB 484)', 'Tampa Electric (LLCS proposed Sept 30, 2026)', 'Florida Public Utilities (proposed)'],
                          threshold='>=50 MW new/incremental load and >=85% load factor (FPL)', min_demand='Take-or-pay requirements', years='Minimum terms',
                          exit_fees='Yes', collateral='Yes', other='Effective Jan 1, 2026; 2026 law SB 484 (s. 366.043, F.S.) requires utilities to have large-load tariffs.', year=2025, url=EEI_LL),
    dc_tax_incentive=inc('Sales-tax exemption for data-center property (UNVERIFIED details)', status_2026='kept (UNVERIFIED)'),
    legislation_2025_2026=[bill('SB 484 (2026)', 'Requires large-load tariffs (s. 366.043, F.S.).', 'enacted 2026', EEI_LL)],
    notes='FPL 2025 case: $2.47B requested, settled at $1.65B (Nov 2025, EEI/RRA).', verified=True)

D['MI'] = dict(
    large_load_tariff=llt('adopted', ['Consumers Energy (approved Nov 6, 2025)', 'Indiana Michigan Power (Tariff LP)', 'DTE Electric (D11 revisions proposed; special contracts approved)'],
                          threshold='>=100 MW single or aggregated (Consumers)', years='15-year contract term (Consumers)',
                          other=('Before each data center connects, Consumers must show its costs are not paid by other customers. MPSC approved DTE contracts for the Saline Twp. '
                                 'data center (Dec 2025, under appeal) and a Google data center (Oct 1, 2026).'),
                          year=2025, url='https://www.michigan.gov/mpsc/commission/news-releases/2025/11/06/mpsc-approves-terms-of-service-between-consumers-energy-and-data-centers'),
    dc_tax_incentive=inc('Sales/use tax exemption for data-center equipment (2024 law - UNVERIFIED)', status_2026='restriction legislation still active (CBPP)', url=CBPP),
    legislation_2025_2026=[], notes='DTE ($474M) and Consumers ($481M) filed new base cases in 2026 shortly after prior cases were decided (EEI/RRA); AG Nessel seeks to cut DTE request by 71%.', verified=True)

D['MO'] = dict(
    large_load_tariff=llt('adopted', ['Ameren Missouri (approved Nov 2025)', 'Evergy Metro / Missouri West (LLPS, >=75 MW)', 'Liberty/Empire (TS-LL in progress)'],
                          threshold='Statute: >100 MW projected peak for utilities with >250,000 customers (Ameren tariff reportedly 75 MW after settlement)',
                          years='Minimum 12-year service term (PSC fact sheet)', other='Ameren: new large loads pay 100% of direct interconnection costs up front.',
                          year=2025, url='https://psc.mo.gov/General/Utility_Tariffs_for_Large_Load_Customers'),
    dc_tax_incentive=inc('Sales/use tax exemption for data-center equipment and electricity (UNVERIFIED)', status_2026='kept (UNVERIFIED)'),
    legislation_2025_2026=[bill('SB 4 (2025)', 'Omnibus utility law; requires large utilities to file large-load schedules for customers projected to exceed 100 MW.', 'signed Apr 9, 2025', 'https://psc.mo.gov/General/Utility_Tariffs_for_Large_Load_Customers')],
    notes='Ameren Missouri requested ~$343M (June 2026), ~+$13/month for the average residential customer; decision due ~May 2027.', verified=True)

D['KS'] = dict(
    large_load_tariff=llt('adopted', ['Evergy Kansas Central / Metro (Large Load Power Service)'], url=EEI_LL),
    dc_tax_incentive=inc('Sales-tax exemption for large data-center investments (2025 law - UNVERIFIED)', enacted=2025, status_2026='kept (2026 restriction bills failed per CBPP)', url=CBPP),
    legislation_2025_2026=[], notes='', verified=False)

D['KY'] = dict(
    large_load_tariff=llt('adopted', ['Kentucky Utilities / LG&E (Extremely High Load Factor Service, Feb 2026)'], year=2026, url=EEI_LL),
    dc_tax_incentive=inc('UNVERIFIED'), legislation_2025_2026=[], notes='', verified=False)

D['CO'] = dict(
    large_load_tariff=llt('proposed', ['Xcel/Public Service Co. of Colorado (26AL-0137E, >=50 MW)', 'Black Hills Energy (economic-development tariff approved)'], threshold='>=50 MW', year=2026, url=EEI_LL),
    dc_tax_incentive=inc('None', status_2026='none (2026 bill to create a 100% exemption failed)', url=SPG),
    legislation_2025_2026=[], notes='Data Center Coalition cites Colorado as a state with no exemption and little development (industry argument).', verified=True)

D['CA'] = dict(
    large_load_tariff=llt('adopted', ['PG&E (Electric Rule 30, interim, A.24-11-007)'], other='Applicants who fund transmission upfront get accelerated connection.', url=EEI_LL),
    dc_tax_incentive=inc('None (no data-center-specific state exemption - UNVERIFIED)'), legislation_2025_2026=[], notes='', verified=False)

D['ID'] = dict(large_load_tariff=llt('adopted', ['Idaho Power (Schedule 20, speculative high-density loads, 2024)'], year=2024, url=EEI_LL),
               dc_tax_incentive=inc('UNVERIFIED', status_2026='2026 restriction bill failed (CBPP)', url=CBPP), legislation_2025_2026=[], notes='', verified=False)
D['ND'] = dict(large_load_tariff=llt('adopted', ['Montana-Dakota Utilities (High Density Contracted Demand Response Tariff, >=10 MW, >=85% LF)', 'Otter Tail Power (proposed)'], threshold='>=10 MW (MDU)', url=EEI_LL),
               dc_tax_incentive=inc('UNVERIFIED'), legislation_2025_2026=[], notes='', verified=False)
D['SD'] = dict(large_load_tariff=llt('proposed', ['Otter Tail Power (HPC schedule, >=75 MW)'], threshold='>=75 MW', url=EEI_LL),
               dc_tax_incentive=inc('UNVERIFIED', status_2026='2026 restriction bill failed (CBPP)', url=CBPP), legislation_2025_2026=[], notes='', verified=False)
D['MT'] = dict(large_load_tariff=llt('proposed', ['NorthWestern Energy (Large New Load Tariff, filed Mar 2026, >=5 MW)'], threshold='>=5 MW',
                                     exit_fees='>=3 years of minimum demand + energy billing', collateral='At least equal to exit fee', year=2026, url=LBNL),
               dc_tax_incentive=inc('UNVERIFIED'), legislation_2025_2026=[], notes='', verified=True)
D['NM'] = dict(large_load_tariff=llt('proposed', ['El Paso Electric (two large-load tariffs in rate case)'], url=EEI_LL),
               dc_tax_incentive=inc('No data-center-specific exemption; local industrial revenue bonds used (UNVERIFIED)'), legislation_2025_2026=[], notes='', verified=False)
D['OK'] = dict(large_load_tariff=llt('adopted', ['PSO (large-load tariff created in Nov 5, 2026 rate order; details under study)', 'OG&E (Extra Large Power proposed June 17, 2026)'],
                                     year=2026, url='https://gcn.com/?p=23300'),
               dc_tax_incentive=inc('UNVERIFIED'), legislation_2025_2026=[],
               notes='OCC approved a 3.55% PSO increase (2-1) on Nov 5, 2026 vs ~15% requested; OG&E ($395M) case pending (EEI/RRA).', verified=True)
D['UT'] = dict(large_load_tariff=llt('none'), dc_tax_incentive=inc('Sales/use tax exemption for data-center equipment (UNVERIFIED); non-disclosing state per GJF', url=GJF),
               legislation_2025_2026=[bill('SB 132 (2025)', 'Large-load service: lets large loads contract for supply if the utility cannot serve (UNVERIFIED).', 'enacted 2025 (UNVERIFIED)', None)], notes='', verified=False)
D['WV'] = dict(large_load_tariff=llt('adopted', ['Appalachian Power / Wheeling Power (LCP and IP tariff revisions, Mar 2025)'], year=2025, url=EEI_LL),
               dc_tax_incentive=inc('UNVERIFIED', status_2026='2026 restriction bill failed (CBPP)', url=CBPP),
               legislation_2025_2026=[bill('HB 2014 (2025) Power Generation and Consumption Act', 'Certified microgrid districts for data centers (UNVERIFIED).', 'enacted 2025 (UNVERIFIED)', None)], notes='', verified=False)
D['TN'] = dict(large_load_tariff=llt('none', ['TVA sets terms for large loads (not state-regulated)']),
               dc_tax_incentive=inc('Sales-tax exemptions for qualified data centers', cost=103_600_000, cost_year='FY2025', cost_basis='TN F&A budget publication, via GJF (local share $27M)', status_2026='kept (UNVERIFIED)', url=GJF),
               legislation_2025_2026=[], notes='', verified=True)
D['AR'] = dict(large_load_tariff=llt('none'), dc_tax_incentive=inc('UNVERIFIED'), legislation_2025_2026=[], notes='Entergy Arkansas sought approval tied to a Google data center in West Memphis (PowerLines 2025 review).', verified=False)
D['CT'] = dict(large_load_tariff=llt('none'), dc_tax_incentive=inc('Sales/use and property tax exemptions for large data centers (2021 law - UNVERIFIED)', status_2026='kept (2026 restriction bill failed per CBPP)', url=CBPP), legislation_2025_2026=[], notes='Eversource/CL&P filed a ~$451M distribution case (July 2026, EEI/RRA).', verified=False)
D['MA'] = dict(large_load_tariff=llt('none'), dc_tax_incentive=inc('Data-center sales-tax exemption (2024 economic-development law - UNVERIFIED)', status_2026='paused (executive, Gov. Healey)', url=SPG), legislation_2025_2026=[], notes='', verified=True)

for st in ['AK', 'DC', 'HI', 'NH', 'RI', 'VT']:
    D[st] = dict(large_load_tariff=llt('none'), dc_tax_incentive=inc('None found (no state data-center incentive identified - UNVERIFIED)'),
                 legislation_2025_2026=[], notes='Low data-center exposure; included for completeness.', verified=False)


# ---------------------------------------------------------------- assemble
out = []
for st in sorted(BASE):
    name, rto, puc_name, puc_url, adv_office, adv_url = BASE[st]
    d = D.get(st)
    if d is None:
        raise SystemExit('missing detail for ' + st)
    cb = 'passed' if st in CBPP_PASSED else 'failed' if st in CBPP_FAILED else 'active' if st in CBPP_ACTIVE else 'none_reported'
    notes = d.get('notes') or ''
    if st in ADVOCATE_NOTES and ADVOCATE_NOTES[st] not in notes:
        notes = (notes + ' ' + ADVOCATE_NOTES[st]).strip()
    rec = {
        'state': st, 'name': name, 'rto': rto,
        'large_load_tariff': d['large_load_tariff'],
        'dc_tax_incentive': d['dc_tax_incentive'],
        'subsidy_restriction_bills_2026_cbpp': cb,
        'legislation_2025_2026': d['legislation_2025_2026'],
        'consumer_advocate': {'office': adv_office, 'url': adv_url, 'source': NASUCA if adv_office else None},
        'puc': {'name': puc_name, 'url': puc_url},
        'notes': notes,
        'verified': bool(d.get('verified')),
        'url_check_note': 'PUC/advocate URLs checked with scripts/policy/check_urls.mjs on ' + CHECKED + '; some state sites block scripts (HTTP 403) or present certificate-chain errors to Node but load in a browser.',
        'verification_notes': ('Key large-load / incentive facts checked against live sources on ' + CHECKED + '; items tagged UNVERIFIED were not.')
        if d.get('verified') else 'Not fully checked against a live source this session; treat tagged items as UNVERIFIED.',
        'last_checked': CHECKED,
    }
    out.append(rec)

assert len(out) == 51, len(out)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump({'generated': CHECKED, 'description': 'State-by-state who-pays policy: large-load tariffs, data-center tax incentives, 2025-26 legislation, PUC and consumer advocate. See research/policy/FINDINGS.md.',
               'status_vocab': {'large_load_tariff.status': ['adopted', 'proposed', 'none']},
               'states': out}, f, indent=1, ensure_ascii=False)
print('wrote', OUT, len(out), 'states;', sum(r['verified'] for r in out), 'verified')
from collections import Counter
print(Counter(r['large_load_tariff']['status'] for r in out))
