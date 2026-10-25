import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Target,
  AlertTriangle,
  CheckCircle2,
  Save,
  Plus,
  Trash2,
  Calendar,
  ShieldCheck,
  TrendingUp,
  Loader2,
} from 'lucide-react';
import { budgetsApi, categoriesApi } from '../api/endpoints';
import { Budget, CategoryItem, CategoryBudgetStatus } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { formatRupee, getCategoryColor } from '../utils/formatters';

export const BudgetsPage: React.FC = () => {
  const { refreshTrigger } = useOutletContext<{ refreshTrigger: number }>() || {};
  const currentMonth = new Date().toISOString().slice(0, 7); // e.g. "2026-10"
  const [selectedMonth, setSelectedMonth] = useState<string>(currentMonth);
  const [budget, setBudget] = useState<Budget | null>(null);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [history, setHistory] = useState<Budget[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Form State
  const [overallLimit, setOverallLimit] = useState<string>('');
  const [catLimits, setCatLimits] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  useEffect(() => {
    categoriesApi.list().then((res) => setCategories(res.data)).catch(() => {});
    loadBudgetHistory();
  }, []);

  useEffect(() => {
    loadBudgetForMonth(selectedMonth);
  }, [selectedMonth, refreshTrigger]);

  const loadBudgetForMonth = async (m: string) => {
    try {
      setIsLoading(true);
      const res = await budgetsApi.getByMonth(m);
      setBudget(res.data);
      setOverallLimit(res.data.overall_budget > 0 ? res.data.overall_budget.toString() : '');
      const limitsMap: Record<string, string> = {};
      Object.entries(res.data.category_budgets || {}).forEach(([cat, val]) => {
        limitsMap[cat] = val.toString();
      });
      setCatLimits(limitsMap);
    } catch (err) {
      console.error('Failed to load budget for month', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadBudgetHistory = async () => {
    try {
      const res = await budgetsApi.list();
      setHistory(res.data);
    } catch (err) {
      console.error('Failed to load budget history', err);
    }
  };

  const handleSaveBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      const numOverall = parseFloat(overallLimit) || 0;
      const numCatLimits: Record<string, number> = {};
      Object.entries(catLimits).forEach(([cat, val]) => {
        const parsed = parseFloat(val);
        if (!isNaN(parsed) && parsed > 0) {
          numCatLimits[cat] = parsed;
        }
      });

      const res = await budgetsApi.upsert({
        month: selectedMonth,
        overall_budget: numOverall,
        category_budgets: numCatLimits,
        alert_thresholds: [50, 80, 100],
      });

      setBudget(res.data);
      setSaveSuccess(true);
      loadBudgetHistory();
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save budget', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCatLimitChange = (cat: string, val: string) => {
    setCatLimits((prev) => ({ ...prev, [cat]: val }));
  };

  if (isLoading && !budget) {
    return <LoadingSpinner message="Loading monthly budget status..." />;
  }

  const overallSpent = budget?.total_spent || 0;
  const overallCap = budget?.overall_budget || 0;
  const overallRemaining = budget?.overall_remaining || 0;
  const overallPct = budget?.overall_percentage || 0;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
            Budget Management & Threshold Alerts
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            Set overall and category spending limits with 50%, 80%, and 100% alerts
          </p>
        </div>

        {/* Month Selector */}
        <div className="flex items-center space-x-2 bg-white dark:bg-slate-900 p-1.5 rounded-xl border border-slate-200 dark:border-slate-800">
          <Calendar className="w-4 h-4 text-slate-400 ml-1" />
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="text-xs font-semibold bg-transparent dark:text-white outline-none cursor-pointer"
          />
        </div>
      </div>

      {/* Active Threshold Alerts Log */}
      {budget?.alerts && budget.alerts.length > 0 && (
        <div className="space-y-2">
          {budget.alerts.map((al) => (
            <div
              key={al.id}
              className={`flex items-center justify-between p-3.5 rounded-2xl border text-xs font-medium ${
                al.threshold >= 100
                  ? 'bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300'
                  : 'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-300'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{al.message}</span>
              </div>
              <span className="font-bold shrink-0 ml-2">
                {al.current_percentage}% used
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Main Budget Progress Card */}
      <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-100 dark:border-slate-800">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Overall Monthly Budget ({selectedMonth})
            </span>
            <div className="flex items-baseline space-x-3 mt-1">
              <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white">
                {formatRupee(overallSpent)}
              </h2>
              <span className="text-sm font-semibold text-slate-400">
                / {overallCap > 0 ? formatRupee(overallCap) : 'No limit set'}
              </span>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-500 block">Remaining Buffer</span>
            <span
              className={`text-xl font-bold ${
                overallRemaining > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'
              }`}
            >
              {formatRupee(overallRemaining)}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-5 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="text-slate-600 dark:text-slate-400">Utilization</span>
            <span
              className={
                overallPct >= 100
                  ? 'text-rose-600 font-bold'
                  : overallPct >= 80
                  ? 'text-amber-600 font-bold'
                  : 'text-emerald-600 font-bold'
              }
            >
              {overallPct}%
            </span>
          </div>
          <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                overallPct >= 100
                  ? 'bg-rose-500'
                  : overallPct >= 80
                  ? 'bg-amber-500'
                  : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, overallPct)}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
            <span>0%</span>
            <span>Alert at 50%</span>
            <span>Warning at 80%</span>
            <span>Exceeded at 100%</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Category Budgets Status Table */}
        <div className="lg:col-span-2 p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-1">
            Category Budget Utilization ({selectedMonth})
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
            Actual expenses vs configured limits
          </p>

          <div className="space-y-4">
            {budget?.category_statuses && budget.category_statuses.length > 0 ? (
              budget.category_statuses.map((cat: CategoryBudgetStatus) => (
                <div key={cat.category} className="space-y-1.5 p-3 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: getCategoryColor(cat.category) }}
                      />
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {cat.category}
                      </span>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className="font-bold text-slate-900 dark:text-white">
                        {formatRupee(cat.spent)}
                      </span>
                      <span className="text-slate-400 text-[11px]">
                        / {cat.budgeted > 0 ? formatRupee(cat.budgeted) : 'No cap'}
                      </span>
                      {cat.budgeted > 0 && (
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                            cat.status === 'exceeded'
                              ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300'
                              : cat.status === 'warning'
                              ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                              : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                          }`}
                        >
                          {cat.percentage_used}%
                        </span>
                      )}
                    </div>
                  </div>

                  {cat.budgeted > 0 && (
                    <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${
                          cat.percentage_used >= 100
                            ? 'bg-rose-500'
                            : cat.percentage_used >= 80
                            ? 'bg-amber-500'
                            : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.min(100, cat.percentage_used)}%` }}
                      />
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">
                No category limits defined yet. Use the editor on the right.
              </p>
            )}
          </div>
        </div>

        {/* Right 1 Col: Budget Limit Settings Form */}
        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs h-fit">
          <div className="flex items-center space-x-2 mb-4">
            <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Set Spending Caps
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                For {selectedMonth}
              </p>
            </div>
          </div>

          <form onSubmit={handleSaveBudget} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Overall Monthly Limit (₹) *
              </label>
              <input
                type="number"
                placeholder="e.g. 35000"
                value={overallLimit}
                onChange={(e) => setOverallLimit(e.target.value)}
                required
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none font-medium"
              />
            </div>

            <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
              <span className="font-semibold text-slate-700 dark:text-slate-300 block mb-2">
                Category Limits (Optional)
              </span>

              <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                {categories
                  .filter((c) => c.type !== 'income')
                  .map((c) => (
                    <div key={c.id} className="flex items-center justify-between space-x-2">
                      <span className="text-[11px] font-medium text-slate-600 dark:text-slate-400 truncate max-w-[130px]">
                        {c.name}
                      </span>
                      <input
                        type="number"
                        placeholder="Limit ₹"
                        value={catLimits[c.name] || ''}
                        onChange={(e) => handleCatLimitChange(c.name, e.target.value)}
                        className="w-28 px-2.5 py-1 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg dark:text-white outline-none"
                      />
                    </div>
                  ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={isSaving}
              className="w-full py-2.5 px-4 font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl shadow-md transition-all cursor-pointer flex items-center justify-center space-x-1.5"
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : saveSuccess ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Limits Saved!</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Budget Limits</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Historical Budgets & MoM Comparison Section */}
      <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-emerald-500" />
              <span>Historical Budgets & Cross-Month Review</span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Compare limits and actual expenditures across past cycles
            </p>
          </div>
        </div>

        {history.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
            {history.map((h) => {
              const pct = h.overall_percentage || (h.overall_budget > 0 ? Math.round((h.total_spent / h.overall_budget) * 100) : 0);
              const isSelected = h.month === selectedMonth;
              return (
                <div
                  key={h.id || h.month}
                  onClick={() => setSelectedMonth(h.month)}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'border-emerald-500 bg-emerald-50/30 dark:bg-emerald-950/20 shadow-xs ring-1 ring-emerald-500'
                      : 'border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 hover:border-slate-300 dark:hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm text-slate-900 dark:text-white">
                      {h.month}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        pct >= 100
                          ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300'
                          : pct >= 80
                          ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                          : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                      }`}
                    >
                      {pct}% used
                    </span>
                  </div>

                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between text-slate-500">
                      <span>Spent:</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {formatRupee(h.total_spent)}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-500">
                      <span>Allocated:</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {formatRupee(h.overall_budget)}
                      </span>
                    </div>
                  </div>

                  {/* Micro Progress Bar */}
                  <div className="mt-3 w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        pct >= 100 ? 'bg-rose-500' : pct >= 80 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(100, pct)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-xs text-slate-500 italic py-2">
            No past budgets recorded yet. Budgets you save will be archived here for multi-month review.
          </p>
        )}
      </div>
    </div>
  );
};
