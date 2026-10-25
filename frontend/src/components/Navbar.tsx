import React, { useState } from 'react';
import { Menu, Sun, Moon, Plus, Sparkles, CheckCircle2 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { aiApi } from '../api/endpoints';

interface NavbarProps {
  onOpenSidebar: () => void;
  onOpenNewTransaction: () => void;
  onRefreshData?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenSidebar,
  onOpenNewTransaction,
  onRefreshData,
}) => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedSuccess, setSeedSuccess] = useState(false);

  const handleSeedDemoData = async () => {
    try {
      setIsSeeding(true);
      await aiApi.seedSamples(45);
      setSeedSuccess(true);
      if (onRefreshData) onRefreshData();
      setTimeout(() => setSeedSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to seed demo data', err);
    } finally {
      setIsSeeding(false);
    }
  };

  const getInitials = (name?: string) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 sm:px-6 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      {/* Left: Mobile hamburger */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenSidebar}
          className="p-2 -ml-2 text-slate-600 rounded-lg hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 md:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-base font-semibold text-slate-800 dark:text-slate-100 hidden sm:block">
            Smart Expense Dashboard
          </h1>
        </div>
      </div>

      {/* Right actions */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Seed Demo Data Button */}
        <button
          onClick={handleSeedDemoData}
          disabled={isSeeding}
          className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
            seedSuccess
              ? 'bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
              : 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800 dark:hover:bg-purple-900/50'
          }`}
          title="Seed 45 days of realistic Indian expense and salary data"
        >
          {seedSuccess ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Data Seeded!</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
              <span>{isSeeding ? 'Seeding...' : 'Seed Demo Data'}</span>
            </>
          )}
        </button>

        {/* New Transaction Button */}
        <button
          onClick={onOpenNewTransaction}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 text-xs sm:text-sm font-semibold rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 shadow-sm shadow-emerald-600/30 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>New Transaction</span>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 text-slate-500 rounded-lg hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors"
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5 text-amber-400" />}
        </button>

        {/* User Avatar */}
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold">
          {getInitials(user?.full_name)}
        </div>
      </div>
    </header>
  );
};
