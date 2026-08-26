import React from 'react';
import { AlertNotification, TradePlan } from '../../services/types';
import { Bell, X, Send, TrendingUp, TrendingDown, ChevronRight } from 'lucide-react';

interface AlertDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: AlertNotification[];
  activePlans?: TradePlan[];
  selectedSymbol?: string;
  onSelectPlan?: (plan: TradePlan) => void;
  onSelectStock?: (symbol: string) => void;
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
  onSelectStock,
  onTriggerTestAlert,
  isLoading,
  theme = 'dark',
}) => {
  if (!isOpen) return null;
  const isDark = theme === 'dark';

  const handleStockClick = (symbol: string) => {
    if (onSelectStock) {
      onSelectStock(symbol);
    } else if (onSelectPlan) {
      const planMatch = activePlans.find((p) => p.symbol === symbol);
      if (planMatch) {
        onSelectPlan(planMatch);
      }
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end">
      <div
        className={`w-full max-w-md border-l h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200 transition-colors ${
          isDark ? 'bg-[#0F172A] border-[#1E293B]' : 'bg-white border-slate-200'
        }`}
      >
        {/* Header */}
        <div
          className={`p-4 border-b flex items-center justify-between ${
            isDark ? 'bg-[#0B0F19] border-[#1E293B]' : 'bg-slate-50 border-slate-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <span className="text-amber-400 text-base">🔔</span>
            <h2 className={`font-bold text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Institutional Alert Center
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-950 text-cyan-300 border border-cyan-800/40 font-bold">
              {alerts.length || activePlans.length} Active
            </span>
          </div>
          <button
            onClick={onClose}
            className={`p-1 rounded transition-colors ${
              isDark ? 'hover:bg-[#1E293B] text-slate-400 hover:text-white' : 'hover:bg-slate-200 text-slate-400 hover:text-slate-700'
            }`}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Action Bar */}
        <div
          className={`px-4 py-2.5 border-b flex items-center justify-between text-xs ${
            isDark ? 'bg-[#0E1526] border-[#1E293B]' : 'bg-slate-50 border-slate-200'
          }`}
        >
          <span className={isDark ? 'text-slate-400' : 'text-slate-500'}>Test Dispatch:</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onTriggerTestAlert('TELEGRAM')}
              disabled={isLoading}
              className="px-2.5 py-1 bg-[#2962ff] hover:bg-[#2962ff]/80 text-white rounded text-[11px] font-medium flex items-center gap-1 transition-colors"
            >
              <Send className="w-3 h-3" />
              Telegram
            </button>
            <button
              onClick={() => onTriggerTestAlert('WEBHOOK')}
              disabled={isLoading}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                isDark
                  ? 'bg-[#1E293B] hover:bg-[#2A374A] text-[#d1d4dc]'
                  : 'bg-white hover:bg-slate-200 text-slate-700 border border-slate-300'
              }`}
            >
              Webhook
            </button>
          </div>
        </div>

        {/* Alerts List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {alerts.length > 0 ? (
            alerts.map((alert, idx) => {
              const planMatch = activePlans.find((p) => p.symbol === alert.symbol);
              const isDemand = (alert.payload as any)?.direction === 'DEMAND' || planMatch?.direction === 'DEMAND';
              const cleanMessage = typeof alert.rendered_message === 'string'
                ? alert.rendered_message.replace(/[{}"*]/g, '')
                : typeof alert.payload?.message === 'string'
                ? alert.payload.message.replace(/[{}"*]/g, '')
                : 'Price entering high-conviction institutional HTF zone';

              const entryPrice = planMatch?.entry_price || (alert.payload as any)?.entry_price || '---';

              return (
                <div
                  key={alert.id || idx}
                  onClick={() => handleStockClick(alert.symbol)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition-all hover:scale-[1.01] ${
                    isDark
                      ? 'bg-[#131B2E] border-slate-800 hover:border-cyan-500/60 shadow-lg'
                      : 'bg-white border-slate-200 hover:border-cyan-500 shadow-sm'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className={`font-bold font-mono text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {alert.symbol}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase flex items-center gap-1 ${
                          isDemand
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40'
                            : 'bg-rose-950 text-rose-400 border border-rose-800/40'
                        }`}
                      >
                        {isDemand ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                        {isDemand ? 'DEMAND' : 'SUPPLY'}
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : 'Live'}
                    </span>
                  </div>

                  <p className={`text-xs leading-relaxed mb-2.5 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                    {cleanMessage}
                  </p>

                  <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-slate-800/60">
                    <span className="text-cyan-400 font-bold">
                      Entry: ₹{typeof entryPrice === 'number' ? entryPrice.toFixed(2) : entryPrice}
                    </span>
                    <span className="text-slate-400 hover:text-cyan-300 flex items-center gap-0.5 font-sans font-semibold text-[10px]">
                      View Chart <ChevronRight className="w-3 h-3 text-cyan-400" />
                    </span>
                  </div>
                </div>
              );
            })
          ) : activePlans.length > 0 ? (
            activePlans.slice(0, 15).map((plan) => {
              const isDemand = plan.direction === 'DEMAND';
              return (
                <div
                  key={`fallback-plan-${plan.symbol}`}
                  onClick={() => handleStockClick(plan.symbol)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition-all hover:scale-[1.01] ${
                    isDark
                      ? 'bg-[#131B2E] border-slate-800 hover:border-cyan-500/60 shadow-lg'
                      : 'bg-white border-slate-200 hover:border-cyan-500 shadow-sm'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className={`font-bold font-mono text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {plan.symbol}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase flex items-center gap-1 ${
                          isDemand
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40'
                            : 'bg-rose-950 text-rose-400 border border-rose-800/40'
                        }`}
                      >
                        {isDemand ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                        {plan.direction}
                      </span>
                    </div>
                    <span className="text-[10px] text-cyan-400 font-mono font-bold">
                      {plan.distance_pct.toFixed(2)}% Away
                    </span>
                  </div>

                  <p className={`text-xs leading-relaxed mb-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                    Fresh {plan.direction} zone ({plan.achievements}-ACH) approaching institutional trigger level.
                  </p>

                  <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-slate-800/60">
                    <span className="text-cyan-400 font-bold">Entry: ₹{plan.entry_price.toFixed(2)}</span>
                    <span className="text-slate-400 flex items-center gap-0.5 font-sans font-semibold text-[10px]">
                      View Chart <ChevronRight className="w-3 h-3 text-cyan-400" />
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="flex flex-col items-center justify-center h-48 text-slate-500 text-xs">
              <span className="text-2xl mb-1">🔔</span>
              <span>No active alerts recorded</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
