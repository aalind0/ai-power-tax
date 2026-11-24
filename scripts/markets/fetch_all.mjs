// Re-download every primary document used by the markets area and re-extract text.
// Usage (from ai-power-tax/):  node scripts/markets/fetch_all.mjs
// Then: python3 -I scripts/markets/build_capacity_prices.py
//       python3 -I scripts/markets/build_wholesale_components.py
//       python3 -I scripts/markets/build_utility_dc_load.py
// Text extraction uses macOS PDFKit via JXA (scripts/markets/pdf2txt.js); HTML pages use html2txt.py.
// Each download goes to its own folder under data/raw/markets/<name>/. Nothing downloaded is executed.
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const RAW = path.join(ROOT, 'data', 'raw', 'markets');
const TXT = path.join(RAW, '_text');
const IMM = 'https://www.monitoringanalytics.com/reports';
const PJM = 'https://www.pjm.com/-/media/DotCom';

const PDF = [
  ['pjm_bra_2028_29', `${PJM}/markets-ops/rpm/rpm-auction-info/2028-2029/2028-2029-bra-results-report.pdf`],
  ['pjm_bra_2027_28', `${PJM}/markets-ops/rpm/rpm-auction-info/2027-2028/2027-2028-bra-report.pdf`],
  ['pjm_bra_2026_27', `${PJM}/markets-ops/rpm/rpm-auction-info/2026-2027/2026-2027-bra-report.pdf`],
  ['pjm_bra_2025_26', `${PJM}/markets-ops/rpm/rpm-auction-info/2025-2026/2025-2026-base-residual-auction-report.pdf`],
  ['pjm_bra_2024_25', `${PJM}/markets-ops/rpm/rpm-auction-info/2024-2025/2024-2025-base-residual-auction-report.ashx`],
  ['pjm_bra_2023_24', `${PJM}/markets-ops/rpm/rpm-auction-info/2023-2024/2023-2024-base-residual-auction-report.ashx`],
  ['pjm_bra_2022_23', `${PJM}/markets-ops/rpm/rpm-auction-info/2022-2023/2022-2023-base-residual-auction-report.ashx`],
  ['pjm_bra_2021_22', `${PJM}/markets-ops/rpm/rpm-auction-info/2021-2022/2021-2022-base-residual-auction-report.ashx`],
  ['pjm_bra_2020_21', `${PJM}/markets-ops/rpm/rpm-auction-info/2020-2021-base-residual-auction-report.ashx`],
  ['pjm_bra_2019_20', `${PJM}/markets-ops/rpm/rpm-auction-info/2019-2020-base-residual-auction-report.ashx`],
  ['pjm_load_report_2026', `${PJM}/library/reports-notices/load-forecast/2026-load-report.pdf`],
  ['pjm_load_report_2025', `${PJM}/library/reports-notices/load-forecast/2025-load-report.pdf`],
  ['2018-som-pjm-sec5', `${IMM}/PJM_State_of_the_Market/2018/2018-som-pjm-sec5.pdf`],
  ['2025-som-pjm-sec5', `${IMM}/PJM_State_of_the_Market/2025/2025-som-pjm-sec5.pdf`],
  ['2025-som-pjm-sec1', `${IMM}/PJM_State_of_the_Market/2025/2025-som-pjm-sec1.pdf`],
  ['2025-som-pjm-sec12', `${IMM}/PJM_State_of_the_Market/2025/2025-som-pjm-sec12.pdf`],
  ['2026q3-som-pjm-sec1', `${IMM}/PJM_State_of_the_Market/2026/2026q3-som-pjm-sec1.pdf`],
  ['IMM_Analysis_of_the_20282029_RPM_Base_Residual_Auction_Part_A_20261030', `${IMM}/Reports/2026/IMM_Analysis_of_the_20282029_RPM_Base_Residual_Auction_Part_A_20261030.pdf`],
  ['IMM_Analysis_of_the_20272028_RPM_Base_Residual_Auction_Part_A_20260105', `${IMM}/Reports/2026/IMM_Analysis_of_the_20272028_RPM_Base_Residual_Auction_Part_A_20260105.pdf`],
  ['IMM_Analysis_of_the_20272028_RPM_Base_Residual_Auction_Part_B_20260709', `${IMM}/Reports/2026/IMM_Analysis_of_the_20272028_RPM_Base_Residual_Auction_Part_B_20260709.pdf`],
  ['IMM_Analysis_of_the_20262027_RPM_Base_Residual_Auction_Part_A_20251001', `${IMM}/Reports/2025/IMM_Analysis_of_the_20262027_RPM_Base_Residual_Auction_Part_A_20251001.pdf`],
  ['IMM_Analysis_of_the_20262027_RPM_Base_Residual_Auction_Part_B_20260303', `${IMM}/Reports/2026/IMM_Analysis_of_the_20262027_RPM_Base_Residual_Auction_Part_B_20260303.pdf`],
  ['IMM_Analysis_of_the_20252026_RPM_Base_Residual_Auction_Part_G_20250603_Revised', `${IMM}/Reports/2025/IMM_Analysis_of_the_20252026_RPM_Base_Residual_Auction_Part_G_20250603_Revised.pdf`],
  ['IMM_Analysis_of_the_20252026_RPM_Base_Residual_Auction_Part_H_20250731', `${IMM}/Reports/2025/IMM_Analysis_of_the_20252026_RPM_Base_Residual_Auction_Part_H_20250731.pdf`],
  ['isone_fca18_results_filing', 'https://www.iso-ne.com/static-assets/documents/100012/er24-1290-000.pdf'],
  ['ucs_connection_costs_brief', 'https://www.ucs.org/media/13772'],
  ['harvard_eli_extracting_profits', 'https://eelp.law.harvard.edu/wp-content/uploads/2025/03/Harvard-ELI-Extracting-Profits-from-the-Public.pdf'],
  ['lbnl_retail_price_drivers_legmt_jan2026', 'https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf'],
  ['e3_ratepayer_study_2025', 'https://www.ethree.com/wp-content/uploads/2025/12/RatepayerStudy.pdf'],
  ['e3_rate_drivers_dc_2026', 'https://www.ethree.com/wp-content/uploads/2026/05/Understanding-the-Drivers-of-Rising-Electricity-Rates-and-the-Role-of-Data-Centers_E3-2026.pdf'],
  ['e3_large_load_tariff_whitepaper_2026', 'https://www.ethree.com/wp-content/uploads/2026/05/E3_Large-Load-Tariff-Whitepaper-1.pdf'],
  ['warren_ai_dc_boom_cost_oct2026', 'https://www.warren.senate.gov/wp-content/uploads/2026/10/471703-ai-data-center-boom-cost-Digital-8.5x11.pdf'],
  ['md_opc_rtep_complaint_may2026', 'https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf'],
  ['md_opc_lapp_pjm_annual_2026', 'https://opc.maryland.gov/Portals/0/Files/Publications/Others/PJM%20Annual%20Meeting%20-%20David%20Lapp%20presentation%20(5.13.2026).pdf'],
  ['eei_cra_retail_rate_trends_2026', 'https://media.crai.com/wp-content/uploads/2026/02/11105740/Retail-rate-trends-in-the-US-EEI-CRA.pdf'],
  ['jlarc_dc_study_presentation_2024', 'https://jlarc.virginia.gov/pdfs/presentations/JLARC%20Virginia%20Data%20Center%20Study_FINAL_12-09-2024.pdf'],
  ['ercot_senate_jul2026_panel1', 'https://www.ercot.com/files/docs/2026/07/29/ERCOT-Senate-July-29-Panel-1-Assessing-The-Grid.pdf'],
  ['ercot_igau_sep2026', 'https://www.ercot.com/files/docs/2026/09/17/10-Interconnection-and-Grid-Analysis-Update-REVISED.pdf'],
  ['doe_lbnl_dc_2025_update', 'https://www.energy.gov/documents/united-states-data-center-energy-usage-report-2025-update'],
];
const HTML = [
  ['cmu_dc_bills', 'https://www.cmu.edu/work-that-matters/energy-innovation/data-center-growth-could-increase-electricity-bills'],
  ['ucs_pjm_connection_costs', 'https://www.ucs.org/about/news/billions-dollars-unreported-data-center-costs-pjm'],
  ['ucs_blog_receipts', 'https://blog.ucs.org/mike-jacobs/data-centers-are-already-increasing-your-energy-bills/'],
  ['nrdc_pjm_board_67m', 'https://www.nrdc.org/press-releases/pjm-board-decide-higher-bills-67-million-americans-due-data-centers'],
  ['columbia_cgep_load_growth_lit_review', 'https://www.energypolicy.columbia.edu/publications/the-effects-of-load-growth-on-electricity-prices-in-the-united-states-a-literature-review/'],
  ['eei_ratepayer_pledge_2026', 'https://www.eei.org/News/news/All/2026-white-house-ratepayer-protection-pledge'],
];

fs.mkdirSync(TXT, { recursive: true });
const run = (cmd, args) => execFileSync(cmd, args, { stdio: 'inherit' });
for (const [name, url] of PDF) {
  const dir = path.join(RAW, name);
  const file = path.join(dir, `${name}.pdf`);
  try {
    run('node', [path.join(ROOT, 'scripts/markets/fetch.mjs'), url, file]);
    run('osascript', ['-l', 'JavaScript', path.join(ROOT, 'scripts/markets/pdf2txt.js'), file, path.join(TXT, `${name}.txt`)]);
  } catch (e) {
    console.error('FAILED', name, e.message);
  }
}
for (const [name, url] of HTML) {
  const dir = path.join(RAW, name);
  const file = path.join(dir, 'page.html');
  try {
    run('node', [path.join(ROOT, 'scripts/markets/fetch.mjs'), url, file]);
    run('python3', ['-I', path.join(ROOT, 'scripts/markets/html2txt.py'), file, path.join(TXT, `${name}.txt`)]);
  } catch (e) {
    console.error('FAILED', name, e.message);
  }
}
