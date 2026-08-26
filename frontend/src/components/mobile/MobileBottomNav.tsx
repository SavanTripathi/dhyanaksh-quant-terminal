import React from 'react';
import { BarChart3, ListFilter, Zap, Bell } from 'lucide-react';

export type MobileTab = 'CHARTS' | 'SCREENER' | 'TOP_ALPHA' | 'ALERTS';

interface MobileBottomNavProps {
  activeTab: MobileTab;
  onTabChange: (tab: MobileTab) => void;
  shortlistCount: number;
  alertCount: number;
  theme?: 'dark' | 'light';
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  activeTab,
  onTabChange,
  shortlistCount,
  alertCount,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  const tabs: { id: MobileTab; label: string; icon: React.ReactNode; badge?: number }[] = [
    {
      id: 'CHARTS',
      label: 'Charts',
      icon: <BarChart3 className="w-5 h-5" />,
    },
    {
      id: 'SCREENER',
      label: 'Screener',
      icon: <ListFilter className="w-5 h-5" />,
      badge: shortlistCount,
    },
    {
      id: 'TOP_ALPHA',
      label: 'Top Alpha',
      icon: <Zap className="w-5 h-5" />,
    },
    {
      id: 'ALERTS',
      label: 'Alerts',
      icon: <Bell className="w-5 h-5" />,
      badge: alertCount,
    },
  ];

  return (
    <div
      className={`md:hidden fixed bottom-0 left-0 right-0 z-40 border-t flex items-center justify-around px-2 py-1.5 safe-area-pb transition-colors ${
        isDark ? 'bg-[#181b24]/95 backdrop-blur border-[#2a2e39]' : 'bg-white/95 backdrop-blur border-slate-200 shadow-lg'
      }`}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex-1 flex flex-col items-center justify-center py-1 relative rounded-lg transition-colors ${
              isActive
                ? isDark
                  ? 'text-[#2962ff] font-bold'
                  : 'text-blue-600 font-bold'
                : isDark
                ? 'text-[#787b86] hover:text-white'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <div className="relative">
              {tab.icon}
              {tab.badge !== undefined && tab.badge > 0 && (
                <span className="absolute -top-1 -right-2 px-1 py-0.2 bg-[#2962ff] text-white text-[9px] font-bold rounded-full min-w-[14px] text-center leading-tight">
                  {tab.badge > 99 ? '99+' : tab.badge}
                </span>
              )}
            </div>
            <span className="text-[10px] mt-0.5 tracking-tight">{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
};
