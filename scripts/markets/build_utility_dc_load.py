"""Map US data-center campuses in compute-atlas to utility and RTO/ISO.
Run: python3 -I scripts/markets/build_utility_dc_load.py
Input : ../compute-atlas/data/atlas.json (campuses[], countryCode == 'US')
Output: data/processed/markets_utility_dc_load.csv

Mapping basis:
  atlas-energy-field  -> the utility/grid is named in the atlas campus 'energy' text (best evidence)
  inferred-location   -> assigned from the campus city/county using known utility service territories (best effort,
                         UNVERIFIED this session; check EIA-861 service territory / HIFLD before relying on it)
rto values: PJM, MISO, SPP, ERCOT, CAISO, NYISO, ISO-NE, or 'none (<region>)' for non-RTO areas (SERC/TVA/WECC).
"""
import csv
import io
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ATLAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'compute-atlas', 'data', 'atlas.json')  # sibling compute-atlas checkout
OUT = os.path.join(ROOT, 'data', 'processed', 'markets_utility_dc_load.csv')

E, I = 'atlas-energy-field', 'inferred-location'
# id -> (utility, rto, basis, pjm_zone_or_note)
M = {
    'google-council-bluffs': ('MidAmerican Energy', 'MISO', E, ''),
    'google-the-dalles': ('Northern Wasco County PUD', 'none (WECC/BPA)', E, ''),
    'google-pryor': ('Grand River Dam Authority', 'SPP', E, ''),
    'google-lenoir': ('Duke Energy Carolinas', 'none (SERC)', E, ''),
    'google-berkeley-county': ('Santee Cooper / Dominion Energy South Carolina', 'none (SERC)', E, ''),
    'google-douglas-county': ('Georgia Power', 'none (SERC)', E, ''),
    'google-bridgeport-al': ('TVA (local power company)', 'none (TVA/SERC)', E, ''),
    'google-clarksville': ('Clarksville Dept. of Electricity / TVA', 'none (TVA/SERC)', E, ''),
    'google-ellis-county-tx': ('Oncor', 'ERCOT', E, ''),
    'google-new-albany': ('AEP Ohio', 'PJM', E, 'AEP zone'),
    'google-papillion': ('Omaha Public Power District / Lincoln Electric System', 'SPP', E, ''),
    'google-mesa': ('Salt River Project', 'none (WECC)', E, ''),
    'google-henderson': ('NV Energy', 'none (WECC)', E, ''),
    'google-kansas-city': ('Evergy', 'SPP', E, ''),
    'google-west-memphis': ('Entergy Arkansas', 'MISO', E, ''),
    'google-haskell-county': ('co-located generation + ERCOT TDSP (unspecified)', 'ERCOT', E, ''),
    'google-armstrong-county': ('Xcel Energy (SPS) area; co-located generation', 'SPP', I, 'Texas Panhandle outside ERCOT (inferred)'),
    'cluster-northern-virginia': ('Dominion Energy Virginia', 'PJM', E, 'DOM zone'),
    'cluster-atlanta': ('Georgia Power + EMCs', 'none (SERC)', E, ''),
    'cluster-dallas-fort-worth': ('Oncor', 'ERCOT', E, ''),
    'cluster-phoenix': ('APS / Salt River Project', 'none (WECC)', E, ''),
    'cluster-chicago': ('ComEd', 'PJM', E, 'COMED zone'),
    'cluster-silicon-valley': ('Silicon Valley Power / PG&E', 'CAISO', E, ''),
    'cluster-hillsboro': ('Portland General Electric', 'none (WECC)', E, ''),
    'cluster-new-york-new-jersey': ('PSE&G / JCP&L / Con Edison', 'PJM / NYISO', E, 'PSEG and JCPL zones (NJ); NYISO Zone J (NYC)'),
    'cluster-columbus': ('AEP Ohio', 'PJM', E, 'AEP zone'),
    'cluster-reno-tric': ('NV Energy', 'none (WECC)', E, ''),
    'cluster-salt-lake-city': ('Rocky Mountain Power (PacifiCorp)', 'none (WECC)', E, ''),
    'google-lagrange': ('Georgia Power', 'none (SERC)', E, ''),
    'google-intersect-meitner': ('co-located generation; Xcel Energy (SPS) area', 'SPP', I, 'Gray & Roberts counties are outside ERCOT (inferred)'),
    'vantage-nv1': ('NV Energy', 'none (WECC)', E, ''),
    'aligned-salt-lake': ('Rocky Mountain Power (PacifiCorp)', 'none (WECC)', E, ''),
    'equinix-ashburn': ('Dominion Energy Virginia', 'PJM', E, 'DOM zone'),
    'qts-atlanta-metro': ('Georgia Power', 'none (SERC)', E, ''),
    'qts-fayetteville': ('Georgia Power', 'none (SERC)', E, ''),
    'qts-richmond': ('Dominion Energy Virginia', 'PJM', E, 'DOM zone'),
    'switch-citadel': ('NV Energy', 'none (WECC)', E, ''),
    'switch-las-vegas-core': ('NV Energy', 'none (WECC)', E, ''),
    'pw-digital-gateway': ('Dominion Energy Virginia', 'PJM', E, 'DOM zone'),
    'cluster-quincy-wa': ('Grant County PUD', 'none (WECC/BPA)', E, ''),
    'microsoft-san-antonio': ('CPS Energy', 'ERCOT', E, ''),
    'microsoft-west-des-moines': ('MidAmerican Energy', 'MISO', E, ''),
    'microsoft-boydton': ('Mecklenburg Electric Cooperative / Dominion', 'PJM', E, 'DOM zone'),
    'aws-ohio-region': ('AEP Ohio', 'PJM', E, 'AEP zone'),
    'aws-oregon-boardman': ('Umatilla Electric Cooperative / PacifiCorp', 'none (WECC/BPA)', E, ''),
    'apple-maiden': ('Duke Energy Carolinas', 'none (SERC)', E, ''),
    'apple-reno': ('NV Energy', 'none (WECC)', E, ''),
    'apple-prineville': ('Pacific Power (PacifiCorp)', 'none (WECC)', E, ''),
    'apple-waukee': ('MidAmerican Energy', 'MISO', E, ''),
    'apple-houston-ai-servers': ('CenterPoint Energy', 'ERCOT', E, 'manufacturing site, not a data center'),
    'microsoft-licking-county': ('AEP Ohio', 'PJM', I, 'AEP zone (inferred)'),
    'microsoft-caledonia': ('We Energies', 'MISO', I, ''),
    'microsoft-gaines-township': ('Consumers Energy', 'MISO', I, ''),
    'tucson-project-blue': ('Tucson Electric Power', 'none (WECC)', I, ''),
    'google-franklin-township': ('AES Indiana', 'MISO', I, ''),
    'peculiar-diode-ventures': ('Evergy', 'SPP', I, ''),
    'college-station-data-center': ('College Station Utilities', 'ERCOT', I, ''),
    'chandler-ai-data-center-rezoning': ('Salt River Project / APS', 'none (WECC)', I, ''),
    'st-charles-project-cumulus': ('Ameren Missouri', 'MISO', I, ''),
    'pittsylvania-balico': ('Dominion Energy Virginia / Appalachian Power (uncertain)', 'PJM', I, ''),
    'stargate-abilene': ('ERCOT TDSP (unspecified) + on-site gas', 'ERCOT', E, ''),
    'stargate-shackelford-frontier': ('on-site gas + ERCOT', 'ERCOT', E, ''),
    'stargate-dona-ana-jupiter': ('behind-the-meter gas microgrid (El Paso Electric area)', 'none (WECC)', E, ''),
    'stargate-lordstown': ('Ohio Edison (FirstEnergy)', 'PJM', I, 'ATSI zone (inferred)'),
    'stargate-milam-county': ('ERCOT TDSP (unspecified) + new solar/storage', 'ERCOT', E, ''),
    'stargate-saline-township': ('DTE Energy', 'MISO', E, ''),
    'stargate-port-washington': ('We Energies', 'MISO', E, ''),
    'openai-ports-pike': ('AEP Ohio area; new on-site generation', 'PJM', I, 'AEP zone (inferred)'),
    'openai-camellia-effingham': ('Georgia Power', 'none (SERC)', E, ''),
    'meta-hyperion': ('Entergy Louisiana', 'MISO', E, ''),
    'meta-prometheus': ('AEP Ohio + behind-the-meter gas', 'PJM', E, 'AEP zone'),
    'meta-el-paso': ('El Paso Electric', 'none (WECC)', E, 'El Paso is outside ERCOT'),
    'meta-lebanon-indiana': ('Boone REMC', 'MISO', E, ''),
    'microsoft-fairwater-wisconsin': ('We Energies', 'MISO', E, ''),
    'microsoft-fairwater-atlanta': ('Georgia Power', 'none (SERC)', E, ''),
    'xai-colossus-1': ('Memphis Light, Gas & Water / TVA', 'none (TVA/SERC)', E, ''),
    'xai-colossus-2': ('behind-the-meter gas (TVA area)', 'none (TVA/SERC)', E, ''),
    'aws-project-rainier-new-carlisle': ('NIPSCO', 'MISO', E, ''),
    'aws-madison-county-ms': ('Entergy Mississippi', 'MISO', E, ''),
    'aws-vicksburg-ms': ('Entergy Mississippi', 'MISO', E, ''),
    'aws-susquehanna-salem-township': ('PPL Electric Utilities zone; Talen Susquehanna nuclear PPA', 'PJM', E, 'PPL zone'),
    'aws-richmond-county-nc': ('Duke Energy Progress', 'none (SERC)', E, ''),
    'aws-butts-county-ga': ('Georgia Power', 'none (SERC)', E, ''),
    'aws-wheatfield-in': ('NIPSCO', 'MISO', E, ''),
    'aws-shreveport-la': ('SWEPCO (AEP)', 'SPP', I, ''),
    'terawulf-hawesville-anthropic': ('Kenergy / Big Rivers Electric', 'MISO', I, ''),
    'hut8-river-bend': ('Entergy Louisiana', 'MISO', E, ''),
    'terawulf-lake-mariner': ('NYPA', 'NYISO', E, 'NYISO Zone A (inferred)'),
    'terawulf-fluidstack-abernathy': ('ERCOT TDSP (unspecified)', 'ERCOT', E, ''),
    'cipher-barber-lake': ('ERCOT TDSP (unspecified)', 'ERCOT', E, ''),
    'cipher-black-pearl-aws': ('ERCOT TDSP (unspecified)', 'ERCOT', E, ''),
    'iren-childress': ('ERCOT TDSP (unspecified)', 'ERCOT', E, ''),
    'iren-sweetwater': ('Oncor', 'ERCOT', E, ''),
    'applied-digital-polaris-forge-1': ('Montana-Dakota Utilities', 'MISO', E, ''),
    'applied-digital-polaris-forge-2': ('Cass County Electric Cooperative', 'MISO', E, ''),
    'galaxy-helios': ('ERCOT TDSP (unspecified)', 'ERCOT', E, ''),
    'coreweave-lancaster': ('PPL Electric Utilities', 'PJM', E, 'PPL zone'),
    'coreweave-kenilworth': ('PSE&G', 'PJM', I, 'PSEG zone (inferred)'),
    'core-scientific-denton': ('Denton Municipal Electric', 'ERCOT', I, ''),
    'crusoe-tallgrass-cheyenne': ('behind-the-meter gas (Black Hills Energy area)', 'none (WECC)', I, ''),
    'nebius-vineland': ('Vineland Municipal Electric Utility', 'PJM', E, 'AECO zone (inferred)'),
    'nebius-kansas-city': ('Evergy', 'SPP', E, ''),
    'fermi-america-matador': ('behind-the-meter (Xcel SPS area)', 'SPP', I, 'Amarillo area is outside ERCOT (inferred)'),
    'poolside-project-horizon': ('behind-the-meter gas', 'ERCOT', I, 'Pecos County is in ERCOT (inferred)'),
    'nscale-microsoft-texas': ('ERCOT TDSP (unspecified)', 'ERCOT', E, ''),
}

STATE = {'Alabama': 'AL', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Georgia': 'GA', 'Illinois': 'IL',
         'Indiana': 'IN', 'Iowa': 'IA', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Michigan': 'MI', 'Mississippi': 'MS',
         'Missouri': 'MO', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
         'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
         'Pennsylvania': 'PA', 'South Carolina': 'SC', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
         'Virginia': 'VA', 'Washington': 'WA', 'Wisconsin': 'WI', 'Wyoming': 'WY'}


def state_code(region):
    region = (region or '').strip()
    if region.startswith('Texas'):
        return 'TX'
    if region == 'Tennessee / Mississippi':
        return 'TN'
    return STATE.get(region, '')


atlas = json.load(io.open(ATLAS, encoding='utf-8'))
us = [c for c in atlas['campuses'] if c.get('countryCode') == 'US']
rows, missing = [], []
for c in us:
    u, r, basis, note = M.get(c['id'], ('', '', 'unmapped', ''))
    if basis == 'unmapped':
        missing.append(c['id'])
    rows.append({
        'campus_id': c['id'], 'campus_name': c['name'], 'state': state_code(c.get('region')),
        'utility': u, 'rto': r, 'powerMW': '' if c.get('powerMW') is None else c['powerMW'], 'status': c.get('status', ''),
        'is_market_cluster': 'true' if c['id'].startswith('cluster-') else 'false',
        'pjm_zone_or_note': note, 'mapping_basis': basis, 'lat': c.get('lat'), 'lng': c.get('lng'),
        'atlas_energy_text': (c.get('energy') or '')[:200]})

cols = ['campus_id', 'campus_name', 'state', 'utility', 'rto', 'powerMW', 'status', 'is_market_cluster',
        'pjm_zone_or_note', 'mapping_basis', 'lat', 'lng', 'atlas_energy_text']
with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print('rows', len(rows), 'unmapped', missing)
