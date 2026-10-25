import React, { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  FileSpreadsheet,
  Upload,
  Download,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  Loader2,
  Copy,
  Info,
} from 'lucide-react';
import { importsApi, transactionsApi } from '../api/endpoints';

export const ImportExportPage: React.FC = () => {
  const { onRefresh } = useOutletContext<{ onRefresh?: () => void }>() || {};
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [importResult, setImportResult] = useState<{
    total_rows_processed: number;
    imported_count: number;
    duplicate_count: number;
    failed_count: number;
    status: string;
  } | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Export filters
  const [exportStart, setExportStart] = useState('');
  const [exportEnd, setExportEnd] = useState('');
  const [exportType, setExportType] = useState('');
  const [isExporting, setIsExporting] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setImportResult(null);
      setUploadError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      setIsUploading(true);
      setUploadError(null);
      const res = await importsApi.uploadCsv(file);
      setImportResult(res.data);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Failed to process CSV file.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadSample = () => {
    const sampleCsv = `Date,Title,Amount,Type,Category,Payment Method,UPI Reference,Description
2026-10-01,Swiggy Order - Dinner Biryani,380.00,expense,Food and groceries,UPI,423456789012,Dinner with friends
2026-10-02,Uber Auto - Office Commute,140.00,expense,Transportation,UPI,423456789013,Morning cab
2026-10-03,Monthly Salary Credit,65000.00,income,Salary and income,Net Banking,NEFT-SAL-1029384,Direct deposit
2026-10-04,Airtel 5G Prepaid Recharge,719.00,expense,Bills and utilities,UPI,423456789014,84 days plan
2026-10-05,Amazon.in - Book & Wireless Earbuds,1850.00,expense,Shopping,UPI,423456789015,Noise earbuds
`;
    const blob = new Blob([sampleCsv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'sample_expense_transactions.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const handleExportFiltered = async () => {
    try {
      setIsExporting(true);
      const res = await transactionsApi.exportCsv({
        start_date: exportStart || '',
        end_date: exportEnd || '',
        type: exportType || '',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `transactions_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export failed', err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
          CSV Statement Import & Export
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
          Upload bank or UPI statements with duplicate hash detection and export financial records
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Col: Import CSV */}
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400">
                <Upload className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                  Import Bank / UPI Statement
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  CSV format with auto-column detection
                </p>
              </div>
            </div>

            <button
              onClick={handleDownloadSample}
              className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center space-x-1"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Sample CSV</span>
            </button>
          </div>

          {uploadError && (
            <div className="p-3 text-xs text-rose-700 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300 rounded-xl border border-rose-200">
              {uploadError}
            </div>
          )}

          <form onSubmit={handleUpload} className="space-y-4">
            {/* Dropzone container */}
            <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl hover:border-emerald-500 transition-colors cursor-pointer bg-slate-50/50 dark:bg-slate-800/30">
              <FileSpreadsheet className="w-8 h-8 text-slate-400 mb-2" />
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                {file ? file.name : 'Click to select or drop CSV statement'}
              </span>
              <span className="text-[11px] text-slate-400 mt-1">
                Supports Indian UPI exports, standard bank statements (max 5MB)
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            <button
              type="submit"
              disabled={!file || isUploading}
              className="w-full py-2.5 px-4 font-semibold text-xs text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 rounded-xl shadow-md transition-all cursor-pointer flex items-center justify-center space-x-2"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing & Deduplicating...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Import & Auto-Categorize Statement</span>
                </>
              )}
            </button>
          </form>

          {/* Import Result Report */}
          {importResult && (
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 space-y-2">
              <div className="flex items-center space-x-2 font-bold text-xs text-slate-900 dark:text-white">
                <FileCheck className="w-4 h-4 text-emerald-500" />
                <span>Import Analysis Report</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                <div className="p-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800">
                  <span className="text-slate-500 text-[11px] block">Imported Cleanly</span>
                  <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                    {importResult.imported_count}
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800">
                  <span className="text-slate-500 text-[11px] block">Duplicates Prevented</span>
                  <span className="text-sm font-bold text-amber-600 dark:text-amber-400">
                    {importResult.duplicate_count}
                  </span>
                </div>
              </div>
              {importResult.duplicate_count > 0 && (
                <p className="text-[11px] text-slate-500 italic">
                  * Duplicate transactions were detected via cryptographic hash matching and automatically skipped.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Right Col: Export CSV */}
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl shadow-xs space-y-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400">
              <Download className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Export Filtered History
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Download transactions as spreadsheet CSV
              </p>
            </div>
          </div>

          <div className="space-y-3 pt-2 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Transaction Type
              </label>
              <select
                value={exportType}
                onChange={(e) => setExportType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl dark:text-white outline-none"
              >
                <option value="">All Transactions (Income & Expenses)</option>
                <option value="expense">Expenses Only</option>
                <option value="income">Income Only</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  From Date (Optional)
                </label>
                <input
                  type="date"
                  value={exportStart}
                  onChange={(e) => setExportStart(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl dark:text-white outline-none"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  To Date (Optional)
                </label>
                <input
                  type="date"
                  value={exportEnd}
                  onChange={(e) => setExportEnd(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl dark:text-white outline-none"
                />
              </div>
            </div>

            <button
              onClick={handleExportFiltered}
              disabled={isExporting}
              className="w-full mt-4 py-2.5 px-4 font-semibold text-xs text-white bg-purple-600 hover:bg-purple-500 rounded-xl shadow-md transition-all cursor-pointer flex items-center justify-center space-x-2"
            >
              {isExporting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download Filtered CSV</span>
                </>
              )}
            </button>
          </div>

          <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-[11px] text-slate-500 space-y-1">
            <div className="flex items-center space-x-1 font-semibold text-slate-700 dark:text-slate-300">
              <Info className="w-3.5 h-3.5" />
              <span>Standard Indian Format</span>
            </div>
            <p>
              Exports include Date, Title, Amount in INR (₹), Type, Category, Payment Channel, and UPI Reference (UTR) for complete audit trail.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
