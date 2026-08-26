import React from 'react';
import { AlertNotification, TradePlan } from '../../services/types';
import { Bell, X, Send, CheckCircle, AlertTriangle, XCircle, Info, Flame, Target, ShieldAlert } from 'lucide-react';

interface AlertDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: AlertNotification[];
  activePlans?: TradePlan[];
  selectedSymbol?: string;
  onSelectPlan?: (plan: TradePlan) => void;
  onTriggerTestAlert: (channel: string) => void;
  isLoading: boolean;
  theme?: 'dark' | 'light';
}

export const AlertDrawer: React.FC<AlertDrawerProps> = ({
  isOpen,
  onClose,
  alerts,
  activePlans = [],
  selectedSymbol,
  onSelectPlan,
  onTriggerTestAlert,
  isLoading,
  theme = 'dark',
}) => {
  if (!isOpen) return null;
  const isDark = theme === 'dark';
  const [filterMode, setFilterMode] = React.useState<'ALL' | 'HITTING_ZONE' | 'SELECTED'>('HITTING_ZONE');

  // Live stocks currently hitting or approaching demand/supply zones from left panel shortlist
  const liveHittingPlans = activePlans.filter(
    (p) => (p.distance_pct <= 2.5 || p.is_approaching) && p.direction === 'DEMAND'
  );

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'APPROACHING':
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case 'ZONE_HIT':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'TARGET_1_HIT':
      case 'TARGET_2_HIT':
      case 'TARGET_3_HIT':
        return <CheckCircle className="w-4 h-4 text-sky-500" />;
      case 'INVALIDATED':
        return <XCircle className="w-4 h-4 text-rose-500" />;
      default:
        return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end">
      <div
        className={`w-full max-w-md border-l h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200 transition-colors ${
          isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200'
        }`}
      >
        {/* Header */}
        <div
          className={`p-4 border-b flex items-center justify-between ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-[#2962ff]" />
            <h2 className={`font-bold text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Institutional Alert Center
            </h2>
          </div>
          <button
            onClick={onClose}
            className={`p-1 rounded transition-colors ${
              isDark ? 'hover:bg-[#2a2e39] text-[#787b86] hover:text-white' : 'hover:bg-slate-200 text-slate-400 hover:text-slate-700'
            }`}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Filters */}
        <div
          className={`px-3 py-2 border-b flex items-center gap-1.5 text-xs ${
            isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-slate-100 border-slate-200'
          }`}
        >
          <button
            onClick={() => setFilterMode('HITTING_ZONE')}
            className={`px-2.5 py-1 rounded font-semibold text-[11px] transition-colors ${
              filterMode === 'HITTING_ZONE'
                ? 'bg-emerald-500 text-white shadow-sm'
                : isDark
                ? 'bg-[#1e222d] text-[#787b86] hover:text-white'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-300'
            }`}
          >
            🔥 Hitting Demand Zone ({liveHittingPlans.length})
          </button>
          <button
            onClick={() => setFilterMode('SELECTED')}
            className={`px-2.5 py-1 rounded font-semibold text-[11px] transition-colors ${
              filterMode === 'SELECTED'
                ? 'bg-[#2962ff] text-white shadow-sm'
                : isDark
                ? 'bg-[#1e222d] text-[#787b86] hover:text-white'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-300'
            }`}
          >
            🎯 {selectedSymbol || 'Selected'}
          </button>
          <button
            onClick={() => setFilterMode('ALL')}
            className={`px-2.5 py-1 rounded font-semibold text-[11px] transition-colors ${
              filterMode === 'ALL'
                ? 'bg-slate-700 text-white'
                : isDark
                ? 'bg-[#1e222d] text-[#787b86] hover:text-white'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-300'
            }`}
          >
            📋 Logs ({alerts.length})
          </button>
        </div>

        {/* Action Bar */}
        <div
          className={`p-2.5 border-b flex items-center justify-between text-xs ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
          }`}
        >
          <span className={isDark ? 'text-[#787b86]' : 'text-slate-500'}>Test Connectivity:</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onTriggerTestAlert('TELEGRAM')}
              disabled={isLoading}
              className="px-2 py-0.5 bg-[#2962ff] hover:bg-[#2962ff]/80 text-white rounded text-[11px] font-medium flex items-center gap-1 transition-colors"
            >
              <Send className="w-3 h-3" />
              Telegram Ping
            </button>
            <button
              onClick={() => onTriggerTestAlert('WEBHOOK')}
              disabled={isLoading}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                isDark
                  ? 'bg-[#2a2e39] hover:bg-[#363a45] text-[#d1d4dc]'
                  : 'bg-white hover:bg-slate-200 text-slate-700 border border-slate-300'
              }`}
            >
              Webhook Ping
            </button>
          </div>
        </div>

        {/* Alerts & Live Demand Hit Setups List */}
        <div
          className={`flex-1 overflow-y-auto p-3 space-y-2.5 divide-y ${
            isDark ? 'divide-[#2a2e39]/40' : 'divide-slate-200'
          }`}
        >
          {filterMode === 'HITTING_ZONE' ? (
            liveHittingPlans.length === 0 ? (
              <div className={`text-center py-12 text-xs ${isDark ? 'text-[#787b86]' : 'text-slate-400'}`}>
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-40 text-emerald-500" />
                No stocks currently touching demand zone boundaries within 2.5%.
              </div>
            ) : (
              liveHittingPlans.map((plan) => (
                <div
                  key={`live-alert-${plan.symbol}`}
                  onClick={() => onSelectPlan && onSelectPlan(plan)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all hover:scale-[1.01] ${
                    isDark
                      ? 'bg-[#131722] border-emerald-500/40 hover:border-emerald-500'
                      : 'bg-emerald-50/50 border-emerald-300 hover:border-emerald-500'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <span className="animate-ping inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-75" />
                      <span className={`font-bold font-mono text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {plan.symbol}
                      </span>
                      <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
                        HITTING DEMAND
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-400 font-bold">
                      {plan.distance_pct.toFixed(2)}% Away
                    </span>
                  </div>

                  <div
                    className={`p-2 rounded font-mono text-[11px] leading-relaxed ${
                      isDark ? 'bg-[#181b24] text-emerald-300' : 'bg-white text-emerald-900 border border-emerald-200'
                    }`}
                  >
                    <div>• Setup: <b>FRESH DEMAND ({plan.achievements}-ACH)</b></div>
                    <div>• CMP: <b>₹{plan.current_price.toFixed(2)}</b></div>
                    <div>• Proximal Entry: <b>₹{plan.entry_price.toFixed(2)}</b></div>
                    <div>• Stop Loss: <b>₹{plan.stop_loss.toFixed(2)}</b> (Risk: ₹{plan.risk_per_share.toFixed(2)})</div>
                    <div>• T1: <b>₹{plan.target_1.toFixed(2)}</b> | T2: <b>₹{plan.target_2.toFixed(2)}</b> | T3: <b>₹{plan.target_3.toFixed(2)}</b></div>
                    <div>• Timeframes: #{plan.participating_timeframes.join(' #')}</div>
                  </div>
                </div>
              ))
            )
          ) : filterMode === 'SELECTED' && selectedSymbol ? (
            (() => {
              const selectedPlan = activePlans.find((p) => p.symbol === selectedSymbol);
              if (!selectedPlan) {
                return (
                  <div className={`text-center py-12 text-xs ${isDark ? 'text-[#787b86]' : 'text-slate-400'}`}>
                    No active trade plan found for {selectedSymbol}.
                  </div>
                );
              }
              const isDemand = selectedPlan.direction === 'DEMAND';
              return (
                <div
                  className={`p-3 rounded-lg border ${
                    isDark
                      ? isDemand
                        ? 'bg-[#131722] border-emerald-500/40'
                        : 'bg-[#131722] border-rose-500/40'
                      : isDemand
                      ? 'bg-emerald-50/50 border-emerald-300'
                      : 'bg-rose-50/50 border-rose-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <span className={`font-bold font-mono text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {selectedPlan.symbol}
                      </span>
                      <span
                        className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                          isDemand ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                        }`}
                      >
                        {selectedPlan.direction} SETUP
                      </span>
                    </div>
                    <span className="text-[10px] font-mono font-bold opacity-80">
                      {selectedPlan.distance_pct.toFixed(2)}% Distance
                    </span>
                  </div>

                  <div
                    className={`p-2.5 rounded font-mono text-[11px] leading-relaxed ${
                      isDark ? 'bg-[#181b24] text-[#d1d4dc]' : 'bg-white text-slate-800 border border-slate-200'
                    }`}
                  >
                    <div>• Confluence: <b>{selectedPlan.achievements}-Achievement</b></div>
                    <div>• Live CMP: <b>₹{selectedPlan.current_price.toFixed(2)}</b></div>
                    <div>• Proximal Entry: <b>₹{selectedPlan.entry_price.toFixed(2)}</b></div>
                    <div>• Stop Loss: <b>₹{selectedPlan.stop_loss.toFixed(2)}</b></div>
                    <div>• Target 1: <b>₹{selectedPlan.target_1.toFixed(2)}</b></div>
                    <div>• Target 2: <b>₹{selectedPlan.target_2.toFixed(2)}</b></div>
                    <div>• Target 3: <b>₹{selectedPlan.target_3.toFixed(2)}</b></div>
                    {selectedPlan.has_ma_confluence && (
                      <div className="text-purple-400">✓ 50 EMA / 200 SMA Inside Zone</div>
                    )}
                  </div>
                </div>
              );
            })()
          ) : (
            alerts.length === 0 ? (
              <div className={`text-center py-12 text-xs ${isDark ? 'text-[#787b86]' : 'text-slate-400'}`}>
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-40" />
                No notification events logged yet.
              </div>
            ) : (
              alerts.map((alert) => (
                <div key={alert.id || alert.created_at} className="pt-2.5 first:pt-0 space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      {getAlertIcon(alert.alert_type)}
                      <span className={`font-bold font-mono ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {alert.symbol}
                      </span>
                      <span
                        className={`px-1.5 py-0.2 rounded border text-[10px] font-semibold ${
                          isDark
                            ? 'bg-[#131722] border-[#2a2e39] text-[#d1d4dc]'
                            : 'bg-slate-100 border-slate-200 text-slate-700'
                        }`}
                      >
                        {alert.alert_type}
                      </span>
                    </div>
                    <span className={`text-[10px] ${isDark ? 'text-[#787b86]' : 'text-slate-400'}`}>
                      {alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : 'Just now'}
                    </span>
                  </div>

                  <div
                    className={`p-2 rounded border text-[10px] font-mono whitespace-pre-line leading-relaxed ${
                      isDark
                        ? 'bg-[#131722] border-[#2a2e39] text-[#d1d4dc]'
                        : 'bg-slate-50 border-slate-200 text-slate-800'
                    }`}
                  >
                    {alert.rendered_message || JSON.stringify(alert.payload, null, 2)}
                  </div>
                </div>
              ))
            )
          )}
        </div>
      </div>
    </div>
  );
};
