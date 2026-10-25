import React from 'react';
import { Link } from 'react-router-dom';
import {
  IndianRupee,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  Zap,
  ArrowRight,
  PieChart,
  Target,
  FileSpreadsheet,
  CheckCircle,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl w-full mx-auto border-b border-slate-100 dark:border-slate-800/80">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white shadow-md shadow-emerald-500/20">
            <IndianRupee className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-slate-900 dark:text-white text-lg tracking-tight block">
              RupeeWise AI
            </span>
            <span className="text-[10px] uppercase font-semibold text-emerald-600 dark:text-emerald-400 tracking-wider">
              Smart Expense Tracker
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/login"
            className="px-4 py-2 text-xs sm:text-sm font-semibold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="px-4 py-2 text-xs sm:text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl shadow-md shadow-emerald-600/30 transition-all"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-6 py-20 lg:py-28 max-w-5xl mx-auto text-center flex-1 flex flex-col justify-center">
        {/* Badge */}
        <div className="inline-flex items-center self-center px-3 py-1 mb-6 rounded-full bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-xs font-semibold text-emerald-700 dark:text-emerald-300 space-x-1.5">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          <span>Tailored for Indian Students, Freshers & Working Professionals</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
          Master Your Expenses with{' '}
          <span className="bg-gradient-to-r from-emerald-500 to-teal-400 bg-clip-text text-transparent">
            Intelligent AI Insights
          </span>
        </h1>

        <p className="mt-6 text-base sm:text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Effortlessly track daily income and expenses in Indian Rupees (₹), auto-categorize UPI transactions, forecast 7-day and 30-day spending, and unlock data-grounded saving recommendations.
        </p>

        {/* CTA Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/register"
            className="flex items-center justify-center space-x-2 w-full sm:w-auto px-7 py-3.5 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl shadow-lg shadow-emerald-600/30 transition-all"
          >
            <span>Start Free Today</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/login"
            className="flex items-center justify-center space-x-2 w-full sm:w-auto px-7 py-3.5 text-sm font-semibold text-slate-800 dark:text-slate-200 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 rounded-xl transition-all"
          >
            <span>Live Demo Sign In</span>
          </Link>
        </div>

        {/* Key USPs Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-20 text-left">
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
            <div className="p-2.5 w-fit rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 mb-3">
              <Zap className="w-5 h-5" />
            </div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">
              UPI Ready & Auto-Categorization
            </h2>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Instant classification for Swiggy, Uber, Zomato, Rent, and UPI transactions using NLP heuristics and ML.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
            <div className="p-2.5 w-fit rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 mb-3">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">
              30-Day Expense Forecast
            </h2>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Statistical time-series forecasting with uncertainty bounds and overspending risk detection.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
            <div className="p-2.5 w-fit rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 mb-3">
              <Target className="w-5 h-5" />
            </div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">
              50% / 80% / 100% Budget Alerts
            </h2>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Set overall and category-specific spending caps and prevent budget overruns before they happen.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
            <div className="p-2.5 w-fit rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 mb-3">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">
              Privacy First & Safe Imports
            </h2>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              CSV bank statement import with duplicate hashing. Your financial data is securely isolated.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 border-t border-slate-100 dark:border-slate-800 text-center text-xs text-slate-500">
        <p>© 2026 RupeeWise AI - Smart Expense Tracker. Built for personal financial wellness in India.</p>
      </footer>
    </div>
  );
};
