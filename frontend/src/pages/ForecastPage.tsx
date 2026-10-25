import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  TrendingUp,
  AlertTriangle,
  Sparkles,
  Calendar,
  CheckCircle2,
  Info,
  Clock,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { aiApi } from '../api/endpoints';
import { ForecastResponse } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';
import { formatRupee, formatDate } from '../utils/formatters';

export const ForecastPage: React.FC = () => {
  const { refreshTrigger, onRefresh } = useOutletContext<{ refreshTrigger: number; onRefresh: () => void }>() || {};
  const [days, setDays] = useState<number>(30);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSeeding, setIsSeeding] = useState<boolean>(false);

  useEffect(() => {
    loadForecast();
  }, [days, refreshTrigger]);

  const loadForecast = async () => {
    try {
      setIsLoading(true);
      const res = await aiApi.getForecast(days);
      setForecast(res.data);
    } catch (err) {
      console.error('Failed to load forecast', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSeed = async () => {
    try {
      setIsSeeding(true);
      await aiApi.seedSamples(45);
      if (onRefresh) onRefresh();
      loadForecast();
    } catch (err) {
      console.error('Failed to seed sample data', err);
    } finally {
      setIsSeeding(false);
    }
  };

  if (isLoading && !forecast) {
    return <LoadingSpinner message="Calculating predictive spending curves..." />;
  }

  const isInsufficient = forecast?.status === 'insufficient_data' || forecast?.has_sufficient_data === false;

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'High':
        return 'bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800';
      case 'Medium':
        return 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800';
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
              AI Spending Prediction & Forecasting
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300">
              ML Time-Series
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            Projected expense trajectories with confidence intervals and overspending detection
          </p>
        </div>

        {/* Horizon Tabs */}
        <div className="flex items-center p-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl">
          <button
            onClick={() => setDays(7)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              days === 7
                ? 'bg-purple-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Next 7 Days
          </button>
          <button
            onClick={() => setDays(30)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              days === 30
                ? 'bg-purple-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Next 30 Days
          </button>
          <button
            onClick={() => setDays(90)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              days === 90
                ? 'bg-purple-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Next 90 Days
          </button>
        </div>
      </div>

      {/* Insufficient Data Guard */}
      {isInsufficient ? (
        <div className="p-8 bg-white dark:bg-slate-900 border border-dashed border-slate-200 dark:border-slate-800 rounded-3xl text-center max-w-xl mx-auto space-y-4">
          <div className="p-4 mx-auto w-fit rounded-2xl bg-amber-50 dark:bg-amber-950/40 text-amber-600">
            <Clock className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            More Transaction History Needed
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            {forecast?.message ||
              'A minimum of 5 to 7 days of historical expenses are required to build a reliable predictive trend line and uncertainty bounds.'}
          </p>
          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="px-5 py-2.5 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-500 rounded-xl shadow-md transition-all cursor-pointer"
          >
            {isSeeding ? 'Populating Data...' : '⚡ Seed 45 Days of Realistic Demo Data'}
          </button>
        </div>
      ) : (
        <>
          {/* Metrics summary cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Projected Total ({days} Days)
              </span>
              <h2 className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                {formatRupee(forecast?.predicted_total || 0)}
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Based on {forecast?.historical_days_used || 0} days of spending history
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Projected Daily Average
              </span>
              <h2 className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                {formatRupee(forecast?.predicted_daily_average || 0)} / day
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Incorporates weekend surge & recurring bills
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Overspending Risk Level
              </span>
              <div className="mt-2 flex items-center space-x-2">
                <span
                  className={`px-3 py-1 text-xs font-bold rounded-lg border ${getRiskBadge(
                    forecast?.overspending_risk_level || 'Low'
                  )}`}
                >
                  {forecast?.overspending_risk_level || 'Low'} Risk
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Relative to monthly budget limit
              </p>
            </div>
          </div>

          {/* Forecasting Curve Chart */}
          <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-2">
              <div>
                <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                  Historical Spending vs {days}-Day Prediction Curve
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Solid line denotes actuals & forecasted values; shaded band shows uncertainty range
                </p>
              </div>
            </div>

            <div className="h-72 sm:h-80 w-full">
              {forecast && forecast.points.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart
                    data={forecast.points}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(v) => v.slice(5)}
                      tick={{ fontSize: 11 }}
                      stroke="#94a3b8"
                    />
                    <YAxis
                      tickFormatter={(v) => `₹${v}`}
                      tick={{ fontSize: 11 }}
                      stroke="#94a3b8"
                    />
                    <Tooltip
                      formatter={(val: any, name: any) => [formatRupee(Number(val)), name]}
                      labelFormatter={(label) => formatDate(String(label))}
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderRadius: '12px',
                        color: '#fff',
                        fontSize: '12px',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    {/* Uncertainty Bounds */}
                    <Area
                      type="monotone"
                      dataKey="upper_bound"
                      stroke="none"
                      fill="#c084fc"
                      fillOpacity={0.15}
                      name="Uncertainty Range"
                    />
                    {/* Historical Actuals */}
                    <Line
                      type="monotone"
                      dataKey="actual_expense"
                      name="Historical Actual Spend"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ r: 2.5 }}
                      connectNulls={false}
                    />
                    {/* Forecasted Line */}
                    <Line
                      type="monotone"
                      dataKey="predicted_expense"
                      name="Projected Forecast"
                      stroke="#a855f7"
                      strokeWidth={2.5}
                      strokeDasharray="4 4"
                      dot={{ r: 2 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </div>

          {/* Influencing Factors Explainability Panel */}
          <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-2 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-purple-500" />
              <span>Forecast Explainability & Influencing Factors</span>
            </h2>
            <div className="space-y-2 mt-3">
              {forecast?.influencing_factors.map((factor, idx) => (
                <div
                  key={idx}
                  className="flex items-start space-x-2 text-xs text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700/60"
                >
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  <span>{factor}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Forecast Disclaimer */}
      <div className="flex items-center space-x-3 p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
        <Info className="w-4 h-4 shrink-0 text-slate-400" />
        <p>
          <strong>Estimate Notice:</strong> Forecasts are probabilistic statistical estimates based on your past spending cadence and day-of-week seasonality. Actual future expenses may vary depending on unexpected emergency payments or discretionary choices.
        </p>
      </div>
    </div>
  );
};
