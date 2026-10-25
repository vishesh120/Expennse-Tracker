import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  amount: string;
  subtitle?: string;
  change?: number | null;
  changeLabel?: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  amount,
  subtitle,
  change,
  changeLabel = 'vs last month',
  icon: Icon,
  iconColor = 'text-emerald-600 dark:text-emerald-400',
  iconBg = 'bg-emerald-50 dark:bg-emerald-950/40',
}) => {
  return (
    <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs transition-all hover:shadow-md">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl ${iconBg} ${iconColor}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3">
        <h3 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          {amount}
        </h3>
        {subtitle && (
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            {subtitle}
          </p>
        )}
      </div>

      {change !== undefined && change !== null && (
        <div className="flex items-center mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/80 text-xs">
          {change > 0 ? (
            <span className="flex items-center font-semibold text-rose-600 dark:text-rose-400 mr-1.5">
              <TrendingUp className="w-3.5 h-3.5 mr-0.5" />
              +{change}%
            </span>
          ) : change < 0 ? (
            <span className="flex items-center font-semibold text-emerald-600 dark:text-emerald-400 mr-1.5">
              <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
              {change}%
            </span>
          ) : (
            <span className="flex items-center font-semibold text-slate-500 mr-1.5">
              <Minus className="w-3.5 h-3.5 mr-0.5" />
              0%
            </span>
          )}
          <span className="text-slate-500 dark:text-slate-400">{changeLabel}</span>
        </div>
      )}
    </div>
  );
};
