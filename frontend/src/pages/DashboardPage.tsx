import React, { useState, useEffect } from 'react';
import { useOutletContext, Link } from 'react-router-dom';
import {
  Wallet,
  TrendingDown,
  TrendingUp,
  PiggyBank,
  AlertTriangle,
  ArrowRight,
  CreditCard,
  Sparkles,
  Calendar,
  Receipt,
  PieChart as PieChartIcon,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts';
import { dashboardApi, aiApi } from '../api/endpoints';
import { DashboardSummary } from '../types';
import { StatCard } from '../components/StatCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';
import { formatRupee, formatDate, getCategoryColor } from '../utils/formatters';

const CHART_COLORS = [
  '#f97316', '#3b82f6', '#ec4899', '#8b5cf6',
  '#10b981', '#eab308', '#ef4444', '#06b6d4',
  '#14b8a6', '#22c55e', '#6366f1', '#64748b'
];

export const DashboardPage: React.FC = () => {
  const { refreshTrigger, onRefresh } = useOutletContext<{ refreshTrigger: number; onRefresh: () => void }>() || {};
  const [period, setPeriod] = useState<string>('this_month');
  const [customStart, setCustomStart] = useState<string>('');
  const [customEnd, setCustomEnd] = useState<string>('');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSeeding, setIsSeeding] = useState<boolean>(false);

  useEffect(() => {
    loadDashboard();
  }, [period, customStart, customEnd, refreshTrigger]);

  const loadDashboard = async () => {
    try {
      setIsLoading(true);
      const res = await dashboardApi.getSummary(
        period,
        period === 'custom' ? customStart : undefined,
        period === 'custom' ? customEnd : undefined
      );
      setSummary(res.data);
    } catch (err) {
      console.error('Failed to load dashboard', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSeedData = async () => {
    try {
      setIsSeeding(true);
      await aiApi.seedSamples(45);
      if (onRefresh) onRefresh();
      loadDashboard();
    } catch (err) {
      console.error('Failed to seed sample data', err);
    } finally {
      setIsSeeding(false);
    }
  };

  if (isLoading && !summary) {
    return <LoadingSpinner message="Calculating your financial insights..." />;
  }

  const hasTransactions = (summary?.transaction_count || 0) > 0;

  return (
    <div className="space-y-6">
      {/* Top Header & Period Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
            Financial Overview
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            {summary ? `${formatDate(summary.start_date)} — ${formatDate(summary.end_date)}` : 'Current financial period'}
          </p>
        </div>

        {/* Period Selector Tabs */}
        <div className="flex items-center p-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xs">
          {[
            { id: 'this_month', label: 'This Month' },
            { id: 'last_month', label: 'Last Month' },
            { id: 'last_30_days', label: 'Last 30 Days' },
            { id: 'custom', label: 'Custom' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setPeriod(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                period === tab.id
                  ? 'bg-emerald-500 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Date Pickers */}
      {period === 'custom' && (
        <div className="flex flex-wrap items-center gap-3 p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-slate-500">From:</span>
            <input
              type="date"
              value={customStart}
              onChange={(e) => setCustomStart(e.target.value)}
              className="px-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg dark:text-white outline-none"
            />
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-slate-500">To:</span>
            <input
              type="date"
              value={customEnd}
              onChange={(e) => setCustomEnd(e.target.value)}
              className="px-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg dark:text-white outline-none"
            />
          </div>
        </div>
      )}

      {/* Budget Overspending Alert Banner */}
      {summary?.budget_utilization_percent && summary.budget_utilization_percent >= 80 && (
        <div
          className={`flex items-start sm:items-center justify-between p-4 rounded-2xl border ${
            summary.budget_utilization_percent >= 100
              ? 'bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300'
              : 'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-300'
          }`}
        >
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <div>
              <p className="text-xs sm:text-sm font-semibold">
                {summary.budget_utilization_percent >= 100
                  ? `Overspending Alert: You have exceeded 100% of your monthly budget (${summary.budget_utilization_percent}% spent).`
                  : `Caution: You have utilized ${summary.budget_utilization_percent}% of your monthly budget limit.`}
              </p>
              <p className="text-xs opacity-85 mt-0.5">
                Total spent: {formatRupee(summary.total_expenses)} out of {formatRupee(summary.active_budget || 0)} allocated.
              </p>
            </div>
          </div>
          <Link
            to="/budgets"
            className="px-3 py-1 text-xs font-bold rounded-lg bg-white/80 dark:bg-black/30 hover:bg-white dark:hover:bg-black/50 transition-colors shrink-0 ml-3"
          >
            Manage Limits
          </Link>
        </div>
      )}

      {/* Empty State Banner if no transactions */}
      {!hasTransactions && (
        <div className="p-6 bg-gradient-to-r from-purple-500/10 via-emerald-500/10 to-teal-500/10 border border-purple-200 dark:border-purple-900/50 rounded-3xl text-center sm:text-left sm:flex sm:items-center sm:justify-between">
          <div className="space-y-1">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center justify-center sm:justify-start space-x-2">
              <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <span>Welcome to RupeeWise AI Expense Tracker!</span>
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 max-w-xl">
              No transactions found for this period. You can add your first expense or seed 45 days of realistic Indian student/professional data to immediately test charts, ML categorizer, and spending forecasts.
            </p>
          </div>
          <button
            onClick={handleSeedData}
            disabled={isSeeding}
            className="mt-4 sm:mt-0 px-4 py-2 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-500 rounded-xl shadow-md transition-all cursor-pointer whitespace-nowrap"
          >
            {isSeeding ? 'Generating Data...' : '⚡ Seed Realistic Demo Data'}
          </button>
        </div>
      )}

      {/* 4 Primary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Income"
          amount={formatRupee(summary?.total_income || 0)}
          subtitle={summary?.total_income ? 'Earned / credited this period' : 'Set salary in profile'}
          icon={Wallet}
          iconColor="text-emerald-600 dark:text-emerald-400"
          iconBg="bg-emerald-50 dark:bg-emerald-950/40"
        />

        <StatCard
          title="Total Expenses"
          amount={formatRupee(summary?.total_expenses || 0)}
          change={summary?.mom_expense_change_percent}
          changeLabel="vs prev period"
          icon={TrendingDown}
          iconColor="text-rose-600 dark:text-rose-400"
          iconBg="bg-rose-50 dark:bg-rose-950/40"
        />

        <StatCard
          title="Net Savings"
          amount={formatRupee(summary?.net_savings || 0)}
          subtitle={`Savings Rate: ${summary?.savings_rate || 0}%`}
          icon={PiggyBank}
          iconColor="text-blue-600 dark:text-blue-400"
          iconBg="bg-blue-50 dark:bg-blue-950/40"
        />

        <StatCard
          title="Highest Category"
          amount={summary?.highest_expense_category || 'None'}
          subtitle={summary?.highest_category_amount ? `${formatRupee(summary.highest_category_amount)} spent` : 'No expenses logged'}
          icon={PieChartIcon}
          iconColor="text-purple-600 dark:text-purple-400"
          iconBg="bg-purple-50 dark:bg-purple-950/40"
        />
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Daily Trends Area / Line Chart */}
        <div className="lg:col-span-2 p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Daily Spending & Income Trends
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Tracking daily cash inflows and outflows
              </p>
            </div>
          </div>

          <div className="h-64 sm:h-72 w-full">
            {summary && summary.daily_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={summary.daily_trends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(v) => v.slice(8)}
                    tick={{ fontSize: 11 }}
                    stroke="#94a3b8"
                  />
                  <YAxis
                    tickFormatter={(v) => `₹${v}`}
                    tick={{ fontSize: 11 }}
                    stroke="#94a3b8"
                  />
                  <Tooltip
                    formatter={(val: any) => [formatRupee(Number(val)), '']}
                    labelFormatter={(label) => formatDate(String(label))}
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Line type="monotone" dataKey="expense" name="Expense" stroke="#f43f5e" strokeWidth={2.5} dot={{ r: 2 }} />
                  <Line type="monotone" dataKey="income" name="Income" stroke="#10b981" strokeWidth={2} dot={{ r: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState
                icon={TrendingUp}
                title="No daily trends recorded"
                description="Add expenses or seed sample data to visualize daily financial momentum."
              />
            )}
          </div>
        </div>

        {/* Right 1 Col: Category Donut Chart */}
        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Category Breakdown
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Share of total spending
              </p>
            </div>
            <Link to="/categories" className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
              View All
            </Link>
          </div>

          <div className="h-64 sm:h-72 w-full flex flex-col justify-center items-center">
            {summary && summary.category_breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={summary.category_breakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="amount"
                    nameKey="category"
                  >
                    {summary.category_breakdown.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={getCategoryColor(entry.category) || CHART_COLORS[index % CHART_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any) => [formatRupee(Number(val)), 'Amount']}
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState
                icon={PieChartIcon}
                title="No categories"
                description="Expenses will be automatically grouped into categories here."
              />
            )}
          </div>
        </div>
      </div>

      {/* Monthly Spending History & Budget vs Actual Charts */}
      {summary && ((summary.monthly_history && summary.monthly_history.length > 0) || (summary.budget_vs_actual && summary.budget_vs_actual.length > 0)) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Monthly Comparison Bar Chart */}
          {summary.monthly_history && summary.monthly_history.length > 0 && (
            <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                    Monthly Spending & Income Bar Chart
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Month-over-month cash flow comparison
                  </p>
                </div>
              </div>

              <div className="h-64 sm:h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={summary.monthly_history} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                    <YAxis tickFormatter={(v) => `₹${v}`} tick={{ fontSize: 11 }} stroke="#94a3b8" />
                    <Tooltip
                      formatter={(val: any) => [formatRupee(Number(val)), '']}
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Bar dataKey="income" name="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="expense" name="Expense" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Budget vs Actual Spending Chart */}
          {summary.budget_vs_actual && summary.budget_vs_actual.length > 0 && (
            <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                    Budget vs Actual Spending Chart
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Allocated limit vs current spend by category
                  </p>
                </div>
                <Link to="/budgets" className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
                  Adjust Limits
                </Link>
              </div>

              <div className="h-64 sm:h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={summary.budget_vs_actual} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis dataKey="category" tickFormatter={(v) => v.length > 8 ? v.slice(0, 8) + '…' : v} tick={{ fontSize: 10 }} stroke="#94a3b8" />
                    <YAxis tickFormatter={(v) => `₹${v}`} tick={{ fontSize: 11 }} stroke="#94a3b8" />
                    <Tooltip
                      formatter={(val: any, name: any) => [formatRupee(Number(val)), name]}
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Bar dataKey="budgeted" name="Budget Limit" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="actual" name="Actual Spent" fill="#f97316" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Bottom Section: Payment Methods & Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Payment Methods Distribution */}
        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Payment Channel Analytics
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                UPI vs Cards vs Net Banking
              </p>
            </div>
            <CreditCard className="w-4 h-4 text-slate-400" />
          </div>

          <div className="space-y-3 mt-4">
            {summary && summary.payment_method_breakdown.length > 0 ? (
              summary.payment_method_breakdown.map((pm) => (
                <div key={pm.method} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-700 dark:text-slate-300">
                      {pm.method} ({pm.count} txns)
                    </span>
                    <span className="font-bold text-slate-900 dark:text-white">
                      {formatRupee(pm.amount)} ({pm.percentage}%)
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full"
                      style={{ width: `${Math.min(100, pm.percentage)}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-8 text-center">No payment channel data yet.</p>
            )}
          </div>
        </div>

        {/* Recent Transactions List (2 Cols) */}
        <div className="lg:col-span-2 p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Recent Transactions
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Latest payment activities
              </p>
            </div>
            <Link
              to="/transactions"
              className="flex items-center space-x-1 text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline"
            >
              <span>View All History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            {summary && summary.recent_transactions.length > 0 ? (
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2">Title</th>
                    <th className="pb-2">Category</th>
                    <th className="pb-2">Payment</th>
                    <th className="pb-2">Date</th>
                    <th className="pb-2 text-right">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                  {summary.recent_transactions.map((txn) => (
                    <tr key={txn.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                      <td className="py-2.5 font-semibold text-slate-900 dark:text-white truncate max-w-[160px]">
                        {txn.title}
                      </td>
                      <td className="py-2.5">
                        <span
                          className="px-2 py-0.5 rounded-full text-[10px] font-semibold text-white"
                          style={{ backgroundColor: getCategoryColor(txn.category) }}
                        >
                          {txn.category}
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-500 dark:text-slate-400">
                        {txn.payment_method}
                      </td>
                      <td className="py-2.5 text-slate-500 dark:text-slate-400 whitespace-nowrap">
                        {formatDate(txn.date)}
                      </td>
                      <td
                        className={`py-2.5 text-right font-bold whitespace-nowrap ${
                          txn.type === 'income'
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : 'text-rose-600 dark:text-rose-400'
                        }`}
                      >
                        {txn.type === 'income' ? '+' : '-'} {formatRupee(txn.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                icon={Receipt}
                title="No recent transactions"
                description="Your recent payments, food orders, and salary deposits will show up here."
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
