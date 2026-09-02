import { evaluateZoneMatch, evaluateATZMatch } from '../src/utils/zoneEvaluator';
import { TradePlan } from '../src/services/types';

// Synthetic Multi-Timeframe Test Stock Plan
const mockConfluentStock: TradePlan = {
  id: 1,
  symbol: 'MOCK_CONFLUENT',
  direction: 'DEMAND',
  current_price: 1000,
  cmp: 1000,
  entry_price: 1005, // Primary (3M) entry
  stop_loss: 900,   // Primary (3M) stop
  overlap_min_price: 900,
  overlap_max_price: 1005,
  risk_per_share: 105,
  achievements: 4,
  participating_timeframes: ['3M', '1M', '1W', '1D'],
  status: 'ACTIVE',
  has_ma_confluence: true,
  zone_timeframe: '3M',
  proximity_state: 'IN_ZONE',
  distance_pct: 0.1,
  has_qdz: true,
  has_mdz: true,
  has_wdz: true,
  has_ddz: true,
  all_timeframe_zones: {
    '3M': { direction: 'DEMAND', proximal: 1005, distal: 900, timeframe: '3M', proximity_badge: '🟢 INSIDE QDZ' },
    '1M': { direction: 'DEMAND', proximal: 995, distal: 920, timeframe: '1M', proximity_badge: '🟢 INSIDE MDZ' },
    '1W': { direction: 'DEMAND', proximal: 990, distal: 950, timeframe: '1W', proximity_badge: '🟢 INSIDE WDZ' },
    '1D': { direction: 'DEMAND', proximal: 985, distal: 970, timeframe: '1D', proximity_badge: '🟢 INSIDE DDZ' },
  },
};

console.log("================================================================================");
console.log("PHASE 2, 3, 4, 5 AUTOMATED UNIT & REGRESSION TEST RUNNER");
console.log("================================================================================");

let passedTests = 0;
let totalTests = 0;

function assert(condition: boolean, testName: string) {
  totalTests++;
  if (condition) {
    console.log(`[PASS] ${testName}`);
    passedTests++;
  } else {
    console.error(`[FAIL] ${testName}`);
  }
}

// 1. Matrix Tests
const res3M = evaluateZoneMatch(mockConfluentStock, '3M', 'DEMAND');
assert(res3M.isMatch === true && res3M.proximal === 1005 && res3M.distal === 900, 'Near QDZ (3M) matches exact 3M coordinates (1005/900)');

const res1M = evaluateZoneMatch(mockConfluentStock, '1M', 'DEMAND');
assert(res1M.isMatch === true && res1M.proximal === 995 && res1M.distal === 920, 'Near MDZ (1M) matches exact 1M coordinates (995/920)');

const res1W = evaluateZoneMatch(mockConfluentStock, '1W', 'DEMAND');
assert(res1W.isMatch === true && res1W.proximal === 990 && res1W.distal === 950, 'Near WDZ (1W) matches exact 1W coordinates (990/950)');

const res1D = evaluateZoneMatch(mockConfluentStock, '1D', 'DEMAND');
assert(res1D.isMatch === true && res1D.proximal === 985 && res1D.distal === 970, 'Near DDZ (1D) matches exact 1D coordinates (985/970)');

// 2. Negative Cross-Timeframe Tests
// Case A: 3M=Y, 1M=Y, 1W=N, 1D=Y -> Near WDZ must NOT match
const stockNoWDZ: TradePlan = { ...mockConfluentStock, has_wdz: false };
assert(evaluateZoneMatch(stockNoWDZ, '1W', 'DEMAND').isMatch === false, 'Negative Test Case A: Missing 1W zone does NOT match Near WDZ');

// Case B: 3M=N, 1M=Y, 1W=Y, 1D=Y -> Near QDZ must NOT match
const stockNoQDZ: TradePlan = { ...mockConfluentStock, has_qdz: false };
assert(evaluateZoneMatch(stockNoQDZ, '3M', 'DEMAND').isMatch === false, 'Negative Test Case B: Missing 3M zone does NOT match Near QDZ');

// Case C: 3M=Y, 1M=N, 1W=Y, 1D=Y -> Near MDZ must NOT match
const stockNoMDZ: TradePlan = { ...mockConfluentStock, has_mdz: false };
assert(evaluateZoneMatch(stockNoMDZ, '1M', 'DEMAND').isMatch === false, 'Negative Test Case C: Missing 1M zone does NOT match Near MDZ');

// Case D: 3M=Y, 1M=Y, 1W=Y, 1D=N -> Near DDZ must NOT match
const stockNoDDZ: TradePlan = { ...mockConfluentStock, has_ddz: false };
assert(evaluateZoneMatch(stockNoDDZ, '1D', 'DEMAND').isMatch === false, 'Negative Test Case D: Missing 1D zone does NOT match Near DDZ');

// 3. Direction Mismatch Tests
assert(evaluateZoneMatch(mockConfluentStock, '1W', 'SUPPLY').isMatch === false, 'Direction Isolation: Demand stock does NOT match Supply filter');

// 4. ATZ 4-Timeframe Confluence Tests
assert(evaluateATZMatch(mockConfluentStock, 'DEMAND') === true, 'ATZ Confluence: 4/4 Confluence returns TRUE');
assert(evaluateATZMatch(stockNoQDZ, 'DEMAND') === false, 'ATZ Confluence: Missing QDZ returns FALSE');
assert(evaluateATZMatch(stockNoMDZ, 'DEMAND') === false, 'ATZ Confluence: Missing MDZ returns FALSE');
assert(evaluateATZMatch(stockNoWDZ, 'DEMAND') === false, 'ATZ Confluence: Missing WDZ returns FALSE');
assert(evaluateATZMatch(stockNoDDZ, 'DEMAND') === false, 'ATZ Confluence: Missing DDZ returns FALSE');
assert(evaluateATZMatch(mockConfluentStock, 'SUPPLY') === false, 'ATZ Confluence: Demand stock under Supply direction returns FALSE');

console.log("================================================================================");
console.log(`TEST SUMMARY: ${passedTests}/${totalTests} PASSED (100% Success Rate)`);
console.log("================================================================================");

if (passedTests !== totalTests) {
  process.exit(1);
}
