import React, { useState, useEffect } from 'react';
import { X, Sparkles, Loader2 } from 'lucide-react';
import { Transaction, CategoryItem } from '../types';
import { transactionsApi, categoriesApi, aiApi } from '../api/endpoints';

interface TransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  transactionToEdit?: Transaction | null;
}

export const TransactionModal: React.FC<TransactionModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  transactionToEdit,
}) => {
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [type, setType] = useState<'expense' | 'income'>('expense');
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [category, setCategory] = useState('Food and groceries');
  const [paymentMethod, setPaymentMethod] = useState('UPI');
  const [upiReference, setUpiReference] = useState('');
  const [description, setDescription] = useState('');
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringFrequency, setRecurringFrequency] = useState('monthly');

  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // AI categorization state
  const [aiPrediction, setAiPrediction] = useState<{
    category: string;
    confidence: number;
    modelType: string;
    explanation?: string;
    explanationFactors?: string[];
  } | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);

  useEffect(() => {
    // Load categories
    categoriesApi
      .list()
      .then((res) => setCategories(res.data))
      .catch((err) => console.error('Failed to load categories', err));
  }, []);

  useEffect(() => {
    if (transactionToEdit) {
      setTitle(transactionToEdit.title);
      setAmount(transactionToEdit.amount.toString());
      setType(transactionToEdit.type);
      setDate(transactionToEdit.date);
      setCategory(transactionToEdit.category);
      setPaymentMethod(transactionToEdit.payment_method);
      setUpiReference(transactionToEdit.upi_reference || '');
      setDescription(transactionToEdit.description || '');
      setIsRecurring(transactionToEdit.is_recurring);
      setRecurringFrequency(transactionToEdit.recurring_frequency || 'monthly');
      setAiPrediction(null);
    } else {
      setTitle('');
      setAmount('');
      setType('expense');
      setDate(new Date().toISOString().split('T')[0]);
      setCategory('Food and groceries');
      setPaymentMethod('UPI');
      setUpiReference('');
      setDescription('');
      setIsRecurring(false);
      setRecurringFrequency('monthly');
      setAiPrediction(null);
    }
    setError(null);
  }, [transactionToEdit, isOpen]);

  // Debounced AI categorization on title change
  useEffect(() => {
    if (transactionToEdit || !title.trim() || title.length < 3) {
      setAiPrediction(null);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setIsPredicting(true);
        const res = await aiApi.categorize({ title });
        if (res.data && res.data.predicted_category) {
          setAiPrediction({
            category: res.data.predicted_category,
            confidence: res.data.confidence,
            modelType: res.data.model_type,
            explanation: res.data.explanation,
            explanationFactors: res.data.explanation_factors,
          });
          // Auto-select category if confidence is high
          if (res.data.confidence >= 0.8) {
            setCategory(res.data.predicted_category);
          }
        }
      } catch (err) {
        console.error('AI categorization error', err);
      } finally {
        setIsPredicting(false);
      }
    }, 450);

    return () => clearTimeout(timer);
  }, [title, transactionToEdit]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setError('Please enter a valid positive amount');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      const payload = {
        title: title.trim(),
        amount: parsedAmount,
        type,
        date,
        category,
        payment_method: paymentMethod,
        upi_reference: upiReference.trim() || undefined,
        description: description.trim() || undefined,
        is_recurring: isRecurring,
        recurring_frequency: isRecurring ? recurringFrequency : undefined,
        ai_suggested_category: aiPrediction?.category,
        ai_confidence: aiPrediction?.confidence,
        is_user_confirmed: true,
      };

      if (transactionToEdit) {
        await transactionsApi.update(transactionToEdit.id, payload);
      } else {
        await transactionsApi.create(payload as any);
      }

      // If user accepted or modified AI prediction, submit feedback asynchronously
      if (aiPrediction) {
        aiApi.submitFeedback({
          title: title.trim(),
          predicted_category: aiPrediction.category,
          confirmed_category: category,
          confidence: aiPrediction.confidence,
        }).catch(() => {});
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save transaction');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs overflow-y-auto">
      <div className="relative w-full max-w-lg p-6 bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">
            {transactionToEdit ? 'Edit Transaction' : 'Add New Transaction'}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="p-3 my-3 text-xs font-medium text-rose-700 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300 rounded-xl border border-rose-200 dark:border-rose-900">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Transaction Type Tabs */}
          <div className="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
            <button
              type="button"
              onClick={() => setType('expense')}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                type === 'expense'
                  ? 'bg-white dark:bg-slate-700 text-rose-600 dark:text-rose-400 shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Expense (-)
            </button>
            <button
              type="button"
              onClick={() => setType('income')}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                type === 'income'
                  ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Income (+)
            </button>
          </div>

          {/* Title with AI Categorization preview */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Title / Merchant Name *
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="e.g. Swiggy order, Uber commute, Electricity bill"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              />
              {isPredicting && (
                <div className="absolute right-3 top-2.5 text-purple-500 animate-spin">
                  <Loader2 className="w-4 h-4" />
                </div>
              )}
            </div>

            {/* AI Suggestion Banner with Explainability */}
            {aiPrediction && !transactionToEdit && (
              <div className="mt-2 p-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800/60 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-purple-700 dark:text-purple-300">
                    <Sparkles className="w-4 h-4 text-purple-500 shrink-0" />
                    <span>
                      Suggested: <strong className="font-semibold">{aiPrediction.category}</strong>{' '}
                      ({Math.round(aiPrediction.confidence * 100)}% match)
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setCategory(aiPrediction.category)}
                    className="px-2 py-0.5 font-medium text-purple-700 bg-purple-200/70 hover:bg-purple-200 dark:bg-purple-800/50 dark:text-purple-200 rounded-md cursor-pointer"
                  >
                    Apply
                  </button>
                </div>
                {aiPrediction.explanation && (
                  <p className="mt-1 text-[11px] text-purple-600/90 dark:text-purple-300/80 leading-normal pl-6">
                    💡 {aiPrediction.explanation}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Amount & Date */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Amount (₹) *
              </label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                placeholder="0.00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Date *
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              />
            </div>
          </div>

          {/* Category & Payment Method */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Category *
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              >
                {categories.length > 0 ? (
                  categories.map((c) => (
                    <option key={c.id} value={c.name}>
                      {c.name}
                    </option>
                  ))
                ) : (
                  <>
                    <option value="Food and groceries">Food and groceries</option>
                    <option value="Transportation">Transportation</option>
                    <option value="Shopping">Shopping</option>
                    <option value="Education">Education</option>
                    <option value="Rent and housing">Rent and housing</option>
                    <option value="Bills and utilities">Bills and utilities</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Entertainment">Entertainment</option>
                    <option value="Travel">Travel</option>
                    <option value="Salary and income">Salary and income</option>
                    <option value="Investments and savings">Investments and savings</option>
                    <option value="Other">Other</option>
                  </>
                )}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Payment Method
              </label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              >
                <option value="UPI">UPI</option>
                <option value="Debit Card">Debit Card</option>
                <option value="Credit Card">Credit Card</option>
                <option value="Net Banking">Net Banking</option>
                <option value="Cash">Cash</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          {/* UPI Reference (if UPI) */}
          {paymentMethod === 'UPI' && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                UPI Reference / UTR (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. 423456789012"
                value={upiReference}
                onChange={(e) => setUpiReference(e.target.value)}
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none"
              />
            </div>
          )}

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Description / Notes (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="Additional notes..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 dark:text-white outline-none resize-none"
            />
          </div>

          {/* Recurring commitment toggle */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60">
            <div>
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block">
                Recurring Transaction
              </span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">
                Factor into spending forecasts and monthly budgeting
              </span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={isRecurring}
                onChange={(e) => setIsRecurring(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-emerald-600"></div>
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-200 dark:border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center space-x-1 px-5 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl shadow-md shadow-emerald-600/30 transition-all cursor-pointer"
            >
              {isSubmitting && <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" />}
              <span>{transactionToEdit ? 'Save Changes' : 'Add Transaction'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
