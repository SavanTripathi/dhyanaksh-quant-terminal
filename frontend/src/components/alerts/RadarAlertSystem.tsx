import React, { useEffect, useState, useRef } from 'react';
import { TradePlan } from '../../services/types';
import { Volume2, VolumeX, Radar, ArrowRight, ShieldAlert, Sparkles } from 'lucide-react';

interface RadarAlertSystemProps {
  plans: TradePlan[];
  selectedSymbol?: string;
  onSelectPlan: (plan: TradePlan) => void;
  theme?: 'dark' | 'light';
}

export const RadarAlertSystem: React.FC<RadarAlertSystemProps> = ({
  plans,
  selectedSymbol,
  onSelectPlan,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [activeRadarPlans, setActiveRadarPlans] = useState<TradePlan[]>([]);
  const lastSoundPlayedRef = useRef<number>(0);
  const audioCtxRef = useRef<AudioContext | null>(null);

  // Play synthesized radar chime ping using Web Audio API
  const playRadarChime = () => {
    if (isMuted) return;
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gainNode = ctx.createGain();

      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(880, ctx.currentTime); // A5
      osc1.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.15); // A6

      osc2.type = 'triangle';
      osc2.frequency.setValueAtTime(440, ctx.currentTime);
      osc2.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15);

      gainNode.gain.setValueAtTime(0.15, ctx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

      osc1.connect(gainNode);
      osc2.connect(gainNode);
      gainNode.connect(ctx.destination);

      osc1.start();
      osc2.start();
      osc1.stop(ctx.currentTime + 0.35);
      osc2.stop(ctx.currentTime + 0.35);
    } catch (e) {
      // audio context blocked until user gesture
    }
  };

  // Monitor high proximity or inside-zone setups (Distance <= 2.0%), prioritizing selected stock
  useEffect(() => {
    let radarHot = plans.filter((p) => (p.distance_pct || 10.0) <= 2.5 || p.is_approaching);

    // If user has selected a stock and it's approaching, prioritize it at the front
    if (selectedSymbol) {
      const selectedPlan = plans.find((p) => p.symbol === selectedSymbol);
      if (selectedPlan && (selectedPlan.distance_pct <= 3.0 || selectedPlan.is_approaching)) {
        radarHot = [selectedPlan, ...radarHot.filter((p) => p.symbol !== selectedSymbol)];
      } else if (selectedPlan) {
        // Show selected stock alert banner
        radarHot = [selectedPlan, ...radarHot.filter((p) => p.symbol !== selectedSymbol)];
      }
    }

    setActiveRadarPlans(radarHot);

    if (radarHot.length > 0) {
      const topPlan = radarHot[0];
      const now = Date.now();
      // Throttle audio ping to at most once every 15 seconds if touching zone
      if (topPlan.distance_pct <= 1.0 && now - lastSoundPlayedRef.current > 15000) {
        playRadarChime();
        lastSoundPlayedRef.current = now;

        // Trigger native notification if permission granted
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification(`⚡ Zone Alert: ${topPlan.symbol}`, {
            body: `${topPlan.direction} Zone touched / within ${topPlan.distance_pct.toFixed(2)}%! Entry: ₹${topPlan.entry_price.toFixed(2)}`,
            icon: '/pwa-192x192.svg',
          });
        }
      }
    }
  }, [plans, selectedSymbol, isMuted]);

  // Request browser notification permission once on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  if (activeRadarPlans.length === 0) return null;

  const highlightedPlan = activeRadarPlans[0];
  const isDemand = highlightedPlan.direction === 'DEMAND';

  return (
    <div
      className={`w-full px-3 py-1.5 border-b flex items-center justify-between transition-all duration-300 z-30 ${
        isDemand
          ? isDark
            ? 'bg-emerald-950/80 border-emerald-800/60 text-emerald-200'
            : 'bg-emerald-50 border-emerald-200 text-emerald-900'
          : isDark
          ? 'bg-rose-950/80 border-rose-800/60 text-rose-200'
          : 'bg-rose-50 border-rose-200 text-rose-900'
      }`}
    >
      <div className="flex items-center gap-2 overflow-hidden">
        <div className="relative flex items-center justify-center">
          <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-emerald-400 opacity-75"></span>
          <Radar className="w-4 h-4 text-emerald-400 relative" />
        </div>

        <div className="flex items-center gap-1.5 text-xs font-semibold truncate">
          <span className="uppercase tracking-wider font-mono px-1.5 py-0.2 rounded bg-black/20 text-[10px] font-bold">
            PROXIMITY RADAR
          </span>
          <span className="font-bold font-mono">{highlightedPlan.symbol}</span>
          <span className="opacity-80 text-[11px]">
            entering {highlightedPlan.direction} Zone (₹{highlightedPlan.entry_price.toFixed(2)}) • {highlightedPlan.distance_pct.toFixed(2)}% Away
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={() => onSelectPlan(highlightedPlan)}
          className="text-xs px-2 py-0.5 rounded bg-emerald-500 hover:bg-emerald-600 text-white font-bold flex items-center gap-1 transition-colors shadow-sm"
        >
          <span>View Plan</span>
          <ArrowRight className="w-3 h-3" />
        </button>

        <button
          onClick={() => setIsMuted(!isMuted)}
          className={`p-1 rounded transition-colors ${
            isDark ? 'hover:bg-white/10 text-[#787b86] hover:text-white' : 'hover:bg-slate-200 text-slate-600'
          }`}
          title={isMuted ? 'Unmute Radar Alert' : 'Mute Radar Alert'}
        >
          {isMuted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4 text-emerald-400" />}
        </button>
      </div>
    </div>
  );
};
