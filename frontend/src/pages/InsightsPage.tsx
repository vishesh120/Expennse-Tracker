import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Sparkles,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  CheckCircle,
  PiggyBank,
  Info,
  ArrowUpRight,
  ShieldAlert,
} from 'lucide-react';
import { aiApi } from '../api/endpoints';
import { AIInsightsResponse, GroundedInsight } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';
import { formatRupee } from '../utils/formatters';

export const InsightsPage: React.FC = () => {
  const { refreshTrigger, onRefresh } = useOutletContext<{ refreshTrigger: number; onRefresh: () => void }>() || {};
  const [data, setData] = useState<AIInsightsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSeeding, setIsSeeding] = useState<boolean>(false);

  useEffect(() => {
    loadInsights();
  }, [refreshTrigger]);

  const loadInsights = async () => {
    try {
      setIsLoading(true);
      const res = await aiApi.getInsights();
      setData(res.data);
    } catch (err) {
      console.error('Failed to load insights', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSeed = async () => {
    try {
      setIsSeeding(true);
      await aiApi.seedSamples(45);
      if (onRefresh) onRefresh();
      loadInsights();
    } catch (err) {
      console.error('Seed error', err);
    } finally {
      setIsSeeding(false);
    }
  };

  if (isLoading && !data) {
    return <LoadingSpinner message="Generating AI financial intelligence..." />;
  }

  const getSeverityIcon = (sev: string) => {
    switch (sev) {
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-rose-500" />;
      case 'warning':
        return <ShieldAlert className="w-5 h-5 text-amber-500" />;
      case 'positive':
        return <CheckCircle className="w-5 h-5 text-emerald-500" />;
      default:
        return <Lightbulb className="w-5 h-5 text-purple-500" />;
    }
  };

  const getSeverityBadgeClass = (sev: string) => {
    switch (sev) {
      case 'critical':
        return 'bg-rose-50 border-rose-200 text-rose-700 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300';
      case 'warning':
        return 'bg-amber-50 border-amber-200 text-amber-700 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-300';
      case 'positive':
        return 'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-950/40 dark:border-emerald-900 dark:text-emerald-300';
      default:
        return 'bg-purple-50 border-purple-200 text-purple-700 dark:bg-purple-950/40 dark:border-purple-900 dark:text-purple-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
              AI Financial Intelligence & Recommendations
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300">
              Grounded AI
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            Personalized, data-backed observations computed from your actual transactions
          </p>
        </div>

        <button
          onClick={loadInsights}
          className="px-3.5 py-1.5 text-xs font-semibold rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shrink-0"
        >
          Re-Analyze
        </button>
      </div>

      {/* AI Financial Coach Briefing Banner */}
      {data?.ai_coach_summary && (
        <div className="p-5 bg-gradient-to-r from-purple-500/10 via-indigo-500/10 to-emerald-500/10 border border-purple-200/80 dark:border-purple-800/60 rounded-3xl shadow-xs">
          <div className="flex items-start space-x-3.5">
            <div className="p-2.5 rounded-2xl bg-purple-600 text-white shadow-md shadow-purple-600/20 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold uppercase tracking-wider text-purple-700 dark:text-purple-300">
                  AI Financial Coach Briefing
                </span>
                <span className="text-[10px] px-1.5 py-0.2 rounded-md bg-purple-100 text-purple-800 dark:bg-purple-900/60 dark:text-purple-200 font-semibold">
                  Personalized
                </span>
              </div>
              <p className="text-xs sm:text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                {data.ai_coach_summary}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Metric Cards Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-200 dark:border-emerald-900/60 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between text-emerald-600 dark:text-emerald-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Annual Savings Potential</span>
            <PiggyBank className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            {formatRupee(data?.savings_potential_annual || 0, false)}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Achievable with micro-spending adjustments
          </p>
        </div>

        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between text-purple-600 dark:text-purple-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Monthly Buffer Potential</span>
            <Sparkles className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            {formatRupee(data?.savings_potential_monthly || 0, false)} / mo
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Recommended monthly discretionary savings
          </p>
        </div>

        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between text-blue-600 dark:text-blue-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Current Savings Rate</span>
            <TrendingUp className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            {data?.monthly_summary.savings_rate_percent || 0}%
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Net savings: {formatRupee(data?.monthly_summary.net_savings || 0)}
          </p>
        </div>

        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between text-rose-600 dark:text-rose-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Total Analyzed Expenses</span>
            <TrendingDown className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            {formatRupee(data?.monthly_summary.total_spent || 0)}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Across {data?.monthly_summary.expense_count || 0} recorded transactions
          </p>
        </div>
      </div>

      {/* Insights Cards Grid */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
          <Lightbulb className="w-5 h-5 text-amber-500" />
          <span>Actionable Observations & Insights</span>
        </h2>

        {data && data.insights.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.insights.map((insight: GroundedInsight) => (
              <div
                key={insight.id}
                className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800">
                        {getSeverityIcon(insight.severity)}
                      </div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                        {insight.title}
                      </h3>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${getSeverityBadgeClass(
                        insight.severity
                      )}`}
                    >
                      {insight.severity}
                    </span>
                  </div>

                  <p className="mt-3 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                    {insight.observation}
                  </p>
                </div>

                {/* Recommendation Box */}
                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-700/60">
                  <div className="flex items-center space-x-1.5 text-xs font-semibold text-emerald-700 dark:text-emerald-300 mb-1">
                    <ArrowUpRight className="w-3.5 h-3.5" />
                    <span>Actionable Recommendation:</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300">
                    {insight.actionable_recommendation}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Sparkles}
            title="Insufficient data for deep insights"
            description="Add a few more transactions or seed realistic sample data to generate automated observations."
            actionText="⚡ Seed Demo Data"
            onAction={handleSeed}
          />
        )}
      </div>

      {/* Financial Wellness Disclaimer */}
      <div className="flex items-center space-x-3 p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
        <Info className="w-4 h-4 shrink-0 text-slate-400" />
        <p>
          <strong>Disclaimer:</strong> {data?.ai_disclaimer || 'Insights and forecasts are algorithmically computed for personal budgeting and financial wellness. They do not constitute certified investment or tax advice.'}
        </p>
      </div>
    </div>
  );
};
