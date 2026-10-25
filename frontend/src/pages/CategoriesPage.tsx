import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  PieChart,
  Plus,
  Trash2,
  Tag,
  Loader2,
  TrendingUp,
  FolderPlus,
  CreditCard,
  QrCode,
} from 'lucide-react';
import { categoriesApi, dashboardApi } from '../api/endpoints';
import { CategoryItem, CategorySpending, PaymentMethodSpending } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';
import { formatRupee, getCategoryColor } from '../utils/formatters';

const PRESET_COLORS = [
  '#f97316', '#3b82f6', '#ec4899', '#8b5cf6',
  '#10b981', '#eab308', '#ef4444', '#06b6d4',
  '#14b8a6', '#6366f1', '#84cc16', '#64748b'
];

export const CategoriesPage: React.FC = () => {
  const { refreshTrigger } = useOutletContext<{ refreshTrigger: number }>() || {};
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [spendingBreakdown, setSpendingBreakdown] = useState<CategorySpending[]>([]);
  const [paymentBreakdown, setPaymentBreakdown] = useState<PaymentMethodSpending[]>([]);
  const [period, setPeriod] = useState<string>('this_month');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // New Category Form
  const [name, setName] = useState('');
  const [type, setType] = useState('expense');
  const [color, setColor] = useState('#6366f1');
  const [isCreating, setIsCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [period, refreshTrigger]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [catsRes, summaryRes] = await Promise.all([
        categoriesApi.list(),
        dashboardApi.getSummary(period),
      ]);
      setCategories(catsRes.data);
      setSpendingBreakdown(summaryRes.data.category_breakdown);
      setPaymentBreakdown(summaryRes.data.payment_method_breakdown || []);
    } catch (err) {
      console.error('Failed to load categories', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      setIsCreating(true);
      setFormError(null);
      await categoriesApi.create({
        name: name.trim(),
        type,
        color,
        icon: 'Tag',
      });
      setName('');
      loadData();
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to create category');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteCategory = async (id: string) => {
    try {
      await categoriesApi.delete(id);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Cannot delete category');
    }
  };

  if (isLoading && categories.length === 0) {
    return <LoadingSpinner message="Loading category metrics..." />;
  }

  const customCategories = categories.filter((c) => !c.is_system);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
            Categories & Spending Distribution
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            Analyze expenses by segment and create custom financial buckets
          </p>
        </div>

        {/* Period Selector */}
        <div className="flex items-center p-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl">
          {[
            { id: 'this_month', label: 'This Month' },
            { id: 'last_month', label: 'Last Month' },
            { id: 'last_30_days', label: 'Last 30 Days' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setPeriod(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                period === tab.id
                  ? 'bg-emerald-500 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Category Spending Analytics */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-1">
              Active Category Expenditure
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-5">
              Ranked by total spending for the selected period
            </p>

            {spendingBreakdown.length > 0 ? (
              <div className="space-y-4">
                {spendingBreakdown.map((item) => (
                  <div key={item.category} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2">
                        <span
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ backgroundColor: getCategoryColor(item.category) }}
                        />
                        <span className="font-semibold text-slate-800 dark:text-slate-200">
                          {item.category}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          ({item.count} {item.count === 1 ? 'txn' : 'txns'})
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 font-bold">
                        <span className="text-slate-900 dark:text-white">
                          {formatRupee(item.amount)}
                        </span>
                        <span className="text-slate-400 text-[11px]">
                          ({item.percentage}%)
                        </span>
                      </div>
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${Math.min(100, item.percentage)}%`,
                          backgroundColor: getCategoryColor(item.category),
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={PieChart}
                title="No category spending recorded"
                description="Expenditure breakdown will appear here once transactions are recorded."
              />
            )}
          </div>

          {/* Custom Categories List Card */}
          <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-1">
              Your Custom Categories ({customCategories.length})
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Personal categories added beyond system presets
            </p>

            {customCategories.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {customCategories.map((c) => (
                  <div
                    key={c.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60"
                  >
                    <div className="flex items-center space-x-2.5">
                      <span
                        className="w-3.5 h-3.5 rounded-full"
                        style={{ backgroundColor: c.color }}
                      />
                      <div>
                        <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block">
                          {c.name}
                        </span>
                        <span className="text-[10px] text-slate-400 capitalize">
                          {c.type}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteCategory(c.id)}
                      className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                      title="Delete category"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic py-2">
                No custom categories yet. Use the creator on the right to add your own.
              </p>
            )}
          </div>

          {/* Payment Method Distribution Analytics */}
          <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2">
                  <CreditCard className="w-4 h-4 text-emerald-500" />
                  <span>Payment Channels & UPI Analytics</span>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Transaction volume and value share by payment mode
                </p>
              </div>
            </div>

            {paymentBreakdown.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {paymentBreakdown.map((pm) => (
                  <div
                    key={pm.method}
                    className="p-3.5 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                        {pm.method === 'UPI' && <QrCode className="w-3.5 h-3.5 text-purple-500" />}
                        <span>{pm.method}</span>
                      </span>
                      <span className="font-bold text-slate-900 dark:text-white">
                        {formatRupee(pm.amount)}
                      </span>
                    </div>

                    <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${Math.min(100, pm.percentage)}%` }}
                      />
                    </div>

                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>{pm.count} {pm.count === 1 ? 'transaction' : 'transactions'}</span>
                      <span className="font-medium text-slate-600 dark:text-slate-300">{pm.percentage}% of total</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic py-2">
                No payment channel records found for this period.
              </p>
            )}
          </div>
        </div>

        {/* Right 1 Col: Create Custom Category Form */}
        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs h-fit">
          <div className="flex items-center space-x-2 mb-4">
            <div className="p-2 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400">
              <FolderPlus className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                New Custom Category
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Create a tailored budget bucket
              </p>
            </div>
          </div>

          {formError && (
            <div className="p-2.5 mb-3 text-xs text-rose-700 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300 rounded-xl border border-rose-200">
              {formError}
            </div>
          )}

          <form onSubmit={handleCreateCategory} className="space-y-3.5 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Category Name *
              </label>
              <input
                type="text"
                placeholder="e.g. Pet Care, Gadgets, Gym"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Classification Type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
                <option value="both">Both</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Color Badge
              </label>
              <div className="flex flex-wrap gap-2">
                {PRESET_COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setColor(c)}
                    className={`w-6 h-6 rounded-full transition-transform ${
                      color === c ? 'scale-125 ring-2 ring-offset-2 ring-emerald-500' : 'hover:scale-110'
                    }`}
                    style={{ backgroundColor: c }}
                  />
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={isCreating}
              className="w-full py-2.5 px-4 font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl shadow-md transition-all cursor-pointer flex items-center justify-center space-x-1.5"
            >
              {isCreating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Create Category</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
