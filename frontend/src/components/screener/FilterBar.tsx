import React, { useState, useEffect, useRef } from 'react';
import { ZoneDirection } from '../../services/types';
import { api } from '../../services/api';
import { Search, Compass, X } from 'lucide-react';

import { NIFTY_500_UNIVERSE, StockUniverseItem } from '../../services/nifty500_universe';
import { TradePlan } from '../../services/types';
import { evaluateZoneMatch, evaluateATZMatch } from '../../utils/zoneEvaluator';

interface FilterBarProps {
  searchQuery: string;
  setSearchQuery: (v: string) => void;
  onSelectStockSymbol: (symbol: string) => void;
  tierFilter: 'ALL' | '3_ACH' | '2_ACH';
  setTierFilter: (v: 'ALL' | '3_ACH' | '2_ACH') => void;
  directionFilter: 'ALL' | ZoneDirection;
  setDirectionFilter: (v: 'ALL' | ZoneDirection) => void;
  approachingOnly: boolean;
  setApproachingOnly: (v: boolean) => void;
  maConfluenceOnly: boolean;
  setMaConfluenceOnly: (v: boolean) => void;
  topPicksFilter: 'ALL' | 'ATZ' | 'APP_WDZ' | 'APP_MDZ' | 'APP_QDZ' | 'APP_DDZ' | 'TOP_3' | 'TOP_5' | 'TOP_10' | 'SCORE_85' | 'GTF_11_5';
  setTopPicksFilter: (v: 'ALL' | 'ATZ' | 'APP_WDZ' | 'APP_MDZ' | 'APP_QDZ' | 'APP_DDZ' | 'TOP_3' | 'TOP_5' | 'TOP_10' | 'SCORE_85' | 'GTF_11_5') => void;
  masterPlans?: TradePlan[];
  totalPlansCount?: number;
  filteredPlansCount?: number;
  theme?: 'dark' | 'light';
}

export const FilterBar: React.FC<FilterBarProps> = ({
  searchQuery,
  setSearchQuery,
  onSelectStockSymbol,
  tierFilter,
  setTierFilter,
  directionFilter,
  setDirectionFilter,
  approachingOnly,
  setApproachingOnly,
  maConfluenceOnly,
  setMaConfluenceOnly,
  topPicksFilter,
  setTopPicksFilter,
  masterPlans = [],
  totalPlansCount,
  filteredPlansCount,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';
  const [searchResults, setSearchResults] = useState<StockUniverseItem[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  // Instant In-Memory Dynamic Search across all 500 NIFTY Stocks
  useEffect(() => {
    const q = searchQuery.trim().toUpperCase();
    if (!q) {
      setSearchResults([]);
      setIsDropdownOpen(false);
      return;
    }

    // 1. Instant local filter across all 500 symbols and names
    const directMatches = NIFTY_500_UNIVERSE.filter(
      (s) => s.symbol.toUpperCase().includes(q) || s.name.toUpperCase().includes(q) || s.sector.toUpperCase().includes(q)
    );

    setSearchResults(directMatches.slice(0, 30));
    setIsDropdownOpen(directMatches.length > 0);

    // 2. Background API verification if local search returns few items
    if (directMatches.length === 0) {
      const timer = setTimeout(async () => {
        try {
          const res = await api.searchUniverse(q);
          if (Array.isArray(res) && res.length > 0) {
            setSearchResults(res.slice(0, 30));
            setIsDropdownOpen(true);
          }
        } catch (e) {
          // ignore
        }
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [searchQuery]);

  // Click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleStockClick = (symbol: string) => {
    onSelectStockSymbol(symbol);
    setSearchQuery('');
    setIsDropdownOpen(false);
  };

  return (
    <div
      className={`p-3 border-b space-y-2.5 transition-colors ${
        isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
      }`}
    >
      {/* Top Header: Title & Dynamic Setups Count Badge */}
      <div className="flex items-center justify-between mb-1">
        <span className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-white' : 'text-slate-900'}`}>
          Institutional Setups
        </span>
        <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-blue-950/80 text-cyan-400 border border-cyan-800/40 shadow-sm">
          {filteredPlansCount ?? totalPlansCount ?? 0} Setups
        </span>
      </div>

      {/* Search Input with Auto-complete for NIFTY 500 */}
      <div ref={searchContainerRef} className="relative">
        <Search
          className={`absolute left-2.5 top-2.5 w-3.5 h-3.5 ${
            isDark ? 'text-[#787b86]' : 'text-slate-400'
          }`}
        />
        <input
          type="text"
          placeholder="Search NIFTY 500 Stocks (e.g. RELIANCE, TCS, INFY)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => {
            if (searchResults.length > 0) setIsDropdownOpen(true);
          }}
          className={`w-full pl-8 pr-7 py-1.5 border rounded text-xs focus:outline-none transition-colors ${
            isDark
              ? 'bg-[#131722] border-[#2a2e39] text-[#d1d4dc] placeholder-[#787b86] focus:border-[#2962ff]'
              : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:border-blue-500'
          }`}
        />
        {searchQuery && (
          <button
            onClick={() => {
              setSearchQuery('');
              setIsDropdownOpen(false);
            }}
            className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-200"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}

        {/* NIFTY 500 Dropdown */}
        {isDropdownOpen && searchResults.length > 0 && (
          <div
            className={`absolute top-full left-0 right-0 mt-1 max-h-56 overflow-y-auto rounded shadow-xl border z-50 divide-y ${
              isDark
                ? 'bg-[#1e222d] border-[#2a2e39] divide-[#2a2e39] text-[#d1d4dc]'
                : 'bg-white border-slate-200 divide-slate-100 text-slate-800'
            }`}
          >
            {searchResults.map((stock) => (
              <div
                key={stock.symbol}
                onClick={() => handleStockClick(stock.symbol)}
                className={`p-2 px-3 text-xs cursor-pointer flex items-center justify-between transition-colors ${
                  isDark ? 'hover:bg-[#2a2e39]' : 'hover:bg-blue-50'
                }`}
              >
                <div>
                  <span className="font-bold font-mono text-blue-500 mr-2">{stock.symbol}</span>
                  <span className="text-[11px] opacity-80">{stock.name}</span>
                </div>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded ${
                    isDark ? 'bg-[#131722] text-[#787b86]' : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  {stock.sector}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Step 9 & MTF Pro Retracement Quick-Filters */}
      <div className="flex flex-wrap items-center gap-1 text-[10px]">
        {(() => {
          const countATZ = masterPlans.length > 0 ? masterPlans.filter((p) => evaluateATZMatch(p, directionFilter)).length : 0;
          const countWDZ = masterPlans.length > 0 ? masterPlans.filter((p) => evaluateZoneMatch(p, '1W', directionFilter).isMatch).length : 0;
          const countMDZ = masterPlans.length > 0 ? masterPlans.filter((p) => evaluateZoneMatch(p, '1M', directionFilter).isMatch).length : 0;
          const countQDZ = masterPlans.length > 0 ? masterPlans.filter((p) => evaluateZoneMatch(p, '3M', directionFilter).isMatch).length : 0;
          const countDDZ = masterPlans.length > 0 ? masterPlans.filter((p) => evaluateZoneMatch(p, '1D', directionFilter).isMatch).length : 0;

          return (
            <>
              <button
                onClick={() => setTopPicksFilter('ALL')}
                className={`px-2 py-0.5 rounded font-bold transition-all ${
                  topPicksFilter === 'ALL'
                    ? 'bg-[#2962ff] text-white shadow-sm'
                    : isDark
                    ? 'bg-[#131722] text-[#787b86] hover:text-white border border-[#2a2e39]'
                    : 'bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200'
                }`}
              >
                All 500 {totalPlansCount ? `(${totalPlansCount})` : ''}
              </button>

              {/* 👑 ATZ Multi-Timeframe Confluence Filter */}
              <button
                onClick={() => setTopPicksFilter(topPicksFilter === 'ATZ' ? 'ALL' : 'ATZ')}
                className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
                  topPicksFilter === 'ATZ'
                    ? 'bg-gradient-to-r from-amber-400 via-yellow-400 to-amber-500 text-black shadow-lg shadow-amber-500/20 font-extrabold border border-amber-300'
                    : isDark
                    ? 'bg-[#131722] text-amber-300 hover:bg-amber-500/10 border border-amber-500/40'
                    : 'bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-300'
                }`}
              >
                👑 ATZ {countATZ > 0 ? `(${countATZ})` : ''}
              </button>

              {/* MTF Retracement Quick-Filters */}
              <button
                onClick={() => setTopPicksFilter(topPicksFilter === ('APP_WDZ' as any) ? 'ALL' : ('APP_WDZ' as any))}
                className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
                  topPicksFilter === ('APP_WDZ' as any)
                    ? 'bg-gradient-to-r from-cyan-400 to-blue-500 text-black shadow-md font-extrabold'
                    : isDark
                    ? 'bg-[#131722] text-cyan-300 hover:bg-cyan-500/10 border border-cyan-500/30'
                    : 'bg-cyan-50 text-cyan-700 hover:bg-cyan-100 border border-cyan-300'
                }`}
              >
                🎯 Near WDZ {countWDZ > 0 ? `(${countWDZ})` : ''}
              </button>

              <button
                onClick={() => setTopPicksFilter(topPicksFilter === ('APP_MDZ' as any) ? 'ALL' : ('APP_MDZ' as any))}
                className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
                  topPicksFilter === ('APP_MDZ' as any)
                    ? 'bg-gradient-to-r from-amber-400 to-orange-500 text-black shadow-md font-extrabold'
                    : isDark
                    ? 'bg-[#131722] text-amber-300 hover:bg-amber-500/10 border border-amber-500/30'
                    : 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-300'
                }`}
              >
                🔥 Near MDZ {countMDZ > 0 ? `(${countMDZ})` : ''}
              </button>

              <button
                onClick={() => setTopPicksFilter(topPicksFilter === ('APP_QDZ' as any) ? 'ALL' : ('APP_QDZ' as any))}
                className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
                  topPicksFilter === ('APP_QDZ' as any)
                    ? 'bg-gradient-to-r from-rose-400 to-pink-500 text-white shadow-md font-extrabold'
                    : isDark
                    ? 'bg-[#131722] text-rose-300 hover:bg-rose-500/10 border border-rose-500/30'
                    : 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-300'
                }`}
              >
                💎 Near QDZ {countQDZ > 0 ? `(${countQDZ})` : ''}
              </button>

              <button
                onClick={() => setTopPicksFilter(topPicksFilter === ('APP_DDZ' as any) ? 'ALL' : ('APP_DDZ' as any))}
                className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
                  topPicksFilter === ('APP_DDZ' as any)
                    ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-black shadow-md font-extrabold'
                    : isDark
                    ? 'bg-[#131722] text-green-300 hover:bg-green-500/10 border border-green-500/30'
                    : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-300'
                }`}
              >
                🔰 Near DDZ {countDDZ > 0 ? `(${countDDZ})` : ''}
              </button>
            </>
          );
        })()}

        <button
          onClick={() => setTopPicksFilter('TOP_3')}
          className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
            topPicksFilter === 'TOP_3'
              ? 'bg-gradient-to-r from-amber-400 to-yellow-500 text-black shadow-md font-extrabold'
              : isDark
              ? 'bg-[#131722] text-amber-400 hover:bg-amber-500/10 border border-amber-500/30'
              : 'bg-amber-50 text-amber-600 hover:bg-amber-100 border border-amber-300'
          }`}
        >
          👑 Top 3 Best
        </button>
        <button
          onClick={() => setTopPicksFilter('TOP_5')}
          className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
            topPicksFilter === 'TOP_5'
              ? 'bg-gradient-to-r from-sky-400 to-blue-500 text-white shadow-md font-extrabold'
              : isDark
              ? 'bg-[#131722] text-sky-400 hover:bg-sky-500/10 border border-sky-500/30'
              : 'bg-sky-50 text-sky-600 hover:bg-sky-100 border border-sky-300'
          }`}
        >
          🚀 Top 5
        </button>
        <button
          onClick={() => setTopPicksFilter('SCORE_85')}
          className={`px-2 py-0.5 rounded font-bold transition-all flex items-center gap-1 ${
            topPicksFilter === 'SCORE_85'
              ? 'bg-gradient-to-r from-emerald-400 to-teal-500 text-black shadow-md font-extrabold'
              : isDark
              ? 'bg-[#131722] text-emerald-400 hover:bg-emerald-500/10 border border-emerald-500/30'
              : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-300'
          }`}
        >
          ⚡ Score ≥85
        </button>
      </div>

      {/* Filter Pills */}
      <div className="flex flex-wrap items-center gap-1.5 text-xs">
        {/* Tier Pills */}
        <div
          className={`flex items-center p-0.5 rounded border ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-white border-slate-300'
          }`}
        >
          <button
            onClick={() => setTierFilter('ALL')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              tierFilter === 'ALL'
                ? 'bg-[#2962ff] text-white'
                : isDark
                ? 'text-[#787b86] hover:text-[#d1d4dc]'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            All (≥2)
          </button>
          <button
            onClick={() => setTierFilter('3_ACH')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              tierFilter === '3_ACH'
                ? 'bg-amber-500 text-black font-bold'
                : isDark
                ? 'text-[#787b86] hover:text-[#d1d4dc]'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            🥇 3-Ach
          </button>
          <button
            onClick={() => setTierFilter('2_ACH')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              tierFilter === '2_ACH'
                ? 'bg-blue-500 text-white font-bold'
                : isDark
                ? 'text-[#787b86] hover:text-[#d1d4dc]'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            🥈 2-Ach
          </button>
        </div>

        {/* Direction Pills */}
        <div
          className={`flex items-center p-0.5 rounded border ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-white border-slate-300'
          }`}
        >
          <button
            onClick={() => setDirectionFilter('ALL')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              directionFilter === 'ALL'
                ? isDark
                  ? 'bg-[#2a2e39] text-white'
                  : 'bg-slate-200 text-slate-800'
                : isDark
                ? 'text-[#787b86] hover:text-[#d1d4dc]'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setDirectionFilter('DEMAND')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              directionFilter === 'DEMAND'
                ? 'bg-emerald-500 text-black font-bold'
                : isDark
                ? 'text-[#787b86] hover:text-[#d1d4dc]'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Demand
          </button>
          <button
            onClick={() => setDirectionFilter('SUPPLY')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              directionFilter === 'SUPPLY'
                ? 'bg-rose-500 text-white font-bold'
                : isDark
                ? 'text-[#787b86] hover:text-[#d1d4dc]'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Supply
          </button>
        </div>

        {/* Proximity Toggle */}
        <button
          onClick={() => setApproachingOnly(!approachingOnly)}
          className={`px-2.5 py-1 rounded border text-[11px] font-semibold transition-colors flex items-center gap-1 ${
            approachingOnly
              ? 'bg-amber-500/20 border-amber-500 text-amber-500 font-bold'
              : isDark
              ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
              : 'border-slate-300 text-slate-500 hover:text-slate-800'
          }`}
        >
          <Compass className="w-3 h-3" />
          Approaching (≤2.5%)
        </button>

        {/* MA Confluence Toggle */}
        <button
          onClick={() => setMaConfluenceOnly(!maConfluenceOnly)}
          className={`px-2.5 py-1 rounded border text-[11px] font-semibold transition-colors ${
            maConfluenceOnly
              ? 'bg-purple-500/20 border-purple-500 text-purple-600 dark:text-purple-300 font-bold'
              : isDark
              ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
              : 'border-slate-300 text-slate-500 hover:text-slate-800'
          }`}
        >
          MA Nested
        </button>
      </div>
    </div>
  );
};
