import React, { useEffect, useState } from 'react';
import { Download, X, Smartphone } from 'lucide-react';

interface PWAInstallPromptProps {
  theme?: 'dark' | 'light';
}

export const PWAInstallPrompt: React.FC<PWAInstallPromptProps> = ({ theme = 'dark' }) => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showPrompt, setShowPrompt] = useState<boolean>(false);
  const isDark = theme === 'dark';

  useEffect(() => {
    // Listen for the beforeinstallprompt event on mobile browsers
    const handleBeforeInstallPrompt = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
      // Only show if user hasn't dismissed it in this session
      const dismissed = sessionStorage.getItem('pwa_prompt_dismissed');
      if (!dismissed) {
        setShowPrompt(true);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Check if already in standalone mode
    if (window.matchMedia('(display-mode: standalone)').matches || (window.navigator as any).standalone) {
      setShowPrompt(false);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      // Guide iOS users if standard prompt is unavailable
      alert('To install on iPhone/iPad: Tap the Share button at the bottom of Safari, then tap "Add to Home Screen" 📲');
      return;
    }
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setShowPrompt(false);
    }
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    sessionStorage.setItem('pwa_prompt_dismissed', 'true');
  };

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-16 left-3 right-3 sm:left-auto sm:right-4 sm:w-96 z-50 animate-bounce-subtle">
      <div
        className={`p-3.5 rounded-xl border shadow-2xl flex items-center justify-between gap-3 ${
          isDark
            ? 'bg-[#181b24]/95 border-cyan-500/40 text-white backdrop-blur-md'
            : 'bg-white/95 border-blue-500/40 text-slate-900 backdrop-blur-md'
        }`}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-md shrink-0">
            <Smartphone className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-xs tracking-wide">
              Install Dhyanaksh App
            </span>
            <span className="text-[10px] text-slate-400">
              Fast, full-screen HTF charts on your phone
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={handleInstallClick}
            className="px-3 py-1.5 bg-gradient-to-r from-[#2962ff] to-cyan-500 text-white text-xs font-bold rounded-lg flex items-center gap-1 shadow-md active:scale-95 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Install</span>
          </button>
          <button
            onClick={handleDismiss}
            className="p-1.5 text-slate-400 hover:text-white rounded-md transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
