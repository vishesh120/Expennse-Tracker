export const formatRupee = (amount: number, showDecimals = true): string => {
  if (isNaN(amount) || amount === null || amount === undefined) return '₹0';
  
  // Format in Indian currency numbering system (e.g. 1,00,000)
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: showDecimals ? 2 : 0,
    maximumFractionDigits: showDecimals ? 2 : 0,
  }).format(amount);
};

export const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  try {
    const parts = dateString.split('-');
    if (parts.length === 3) {
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1;
      const day = parseInt(parts[2], 10);
      const date = new Date(year, month, day);
      return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });
    }
    const d = new Date(dateString);
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateString;
  }
};

export const getCategoryColor = (category: string): string => {
  const map: Record<string, string> = {
    'Food and groceries': '#f97316',
    'Transportation': '#3b82f6',
    'Shopping': '#ec4899',
    'Education': '#8b5cf6',
    'Rent and housing': '#10b981',
    'Bills and utilities': '#eab308',
    'Healthcare': '#ef4444',
    'Entertainment': '#06b6d4',
    'Travel': '#14b8a6',
    'Salary and income': '#22c55e',
    'Investments and savings': '#6366f1',
    'Other': '#64748b',
  };
  return map[category] || '#6366f1';
};
