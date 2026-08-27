import axios from 'axios';
import {
  Timeframe,
  ZoneDirection,
  ScreenerShortlistResponse,
  ChartCandlesResponse,
  ChartZonesResponse,
  AlertHistoryResponse,
  TradePlan
} from './types';

const API_BASE_URL = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Search NIFTY 500 universe
  async searchUniverse(query: string, limit: number = 25): Promise<any[]> {
    const res = await apiClient.get<any[]>('/universe/search', {
      params: { query, limit },
    });
    return res.data;
  },

  // Chart Candles Data
  async fetchCandles(symbol: string, timeframe: Timeframe = '1D', days: number = 180): Promise<ChartCandlesResponse> {
    const res = await apiClient.get<ChartCandlesResponse>(`/charts/${symbol}/candles`, {
      params: { timeframe, days },
    });
    return res.data;
  },

  // Real-time LTP Quote
  async fetchQuote(symbol: string): Promise<{
    symbol: string;
    ltp: number;
    previous_close: number;
    change: number;
    change_pct: number;
    open: number;
    high: number;
    low: number;
    volume: number;
    timestamp: string;
  }> {
    const res = await apiClient.get<any>(`/charts/${symbol}/quote`);
    return res.data;
  },

  // Chart Zones & Overlaps
  async fetchZones(symbol: string, days: number = 180, minAchievements: number = 2): Promise<ChartZonesResponse> {
    const res = await apiClient.get<ChartZonesResponse>(`/charts/${symbol}/zones`, {
      params: { days, min_achievements: minAchievements },
    });
    return res.data;
  },

  // Screener Shortlist (Strict GTF: Fresh, Opposing Violation, Deduplicated by default)
  async fetchScreenerShortlist(params?: {
    min_achievements?: number;
    direction?: ZoneDirection;
    approaching_only?: boolean;
    has_ma_confluence?: boolean;
    opposing_violation_only?: boolean;
    deduplicate?: boolean;
    limit?: number;
  }): Promise<ScreenerShortlistResponse> {
    const res = await apiClient.get<ScreenerShortlistResponse>('/screener/shortlist', {
      params: { min_achievements: 2, opposing_violation_only: true, deduplicate: true, limit: 1000, ...params },
    });
    return res.data;
  },

  // Step 9: Top Picks (Top 3, 5, 10)
  async fetchTopPicks(limit: number = 5, minScore: number = 70): Promise<ScreenerShortlistResponse> {
    const res = await apiClient.get<ScreenerShortlistResponse>('/screener/top-picks', {
      params: { limit, min_score: minScore },
    });
    return res.data;
  },

  // Step 9: Symbol Conviction Analysis
  async fetchSymbolAnalysis(symbol: string): Promise<any> {
    const res = await apiClient.get(`/screener/analysis/${symbol}`);
    return res.data;
  },

  // Trigger EOD Batch Scan
  async triggerBatchScan(lookbackDays: number = 180, minAchievements: number = 2): Promise<any> {
    const res = await apiClient.post('/batch/run', null, {
      params: { lookback_days: lookbackDays, min_achievements: minAchievements },
    });
    return res.data;
  },

  // Fetch Batch Scan Progress
  async fetchBatchProgress(): Promise<any> {
    const res = await apiClient.get('/batch/progress');
    return res.data;
  },

  // Alert History
  async fetchAlertsHistory(limit: number = 30): Promise<AlertHistoryResponse> {
    const res = await apiClient.get<AlertHistoryResponse>('/alerts/history', {
      params: { limit },
    });
    return res.data;
  },

  // Trigger Test Alert
  async triggerTestAlert(channel: string = 'TELEGRAM', symbol: string = 'RELIANCE'): Promise<any> {
    const res = await apiClient.post('/alerts/test', {
      channel,
      symbol,
      alert_type: 'SYSTEM_TEST',
    });
    return res.data;
  },

  // Dispatch Batch Alerts
  async dispatchBatchAlerts(): Promise<any> {
    const res = await apiClient.post('/alerts/dispatch-batch');
    return res.data;
  },

  // Backtest Run
  async runBacktest(payload: {
    symbol: string;
    lookback_days: number;
    min_achievements: number;
    account_size: number;
    risk_per_trade_pct: number;
  }): Promise<any> {
    const res = await apiClient.post('/backtest/run', payload);
    return res.data;
  },

  // Backtest Results
  async fetchBacktestResults(runId: number): Promise<any> {
    const res = await apiClient.get(`/backtest/results/${runId}`);
    return res.data;
  },

  // Step 7: Market Regime
  async fetchMarketRegime(): Promise<any> {
    const res = await apiClient.get('/context/market-regime');
    return res.data;
  },

  // Step 7: Sector Rotation
  async fetchSectorRotation(): Promise<any> {
    const res = await apiClient.get('/context/sectors');
    return res.data;
  },

  // Step 7: F&O Intelligence
  async fetchFOIntelligence(symbol: string): Promise<any> {
    const res = await apiClient.get(`/context/fo/${symbol}`);
    return res.data;
  },

  // Health check
  async healthCheck(): Promise<any> {
    const res = await apiClient.get('/health');
    return res.data;
  },
};


