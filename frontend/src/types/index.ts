export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  occupation?: string;
  monthly_income: number;
  preferences: {
    dark_mode?: boolean;
    currency?: string;
    currency_symbol?: string;
    budget_alerts_enabled?: boolean;
    alert_thresholds?: number[];
  };
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Transaction {
  id: string;
  user_id: string;
  title: string;
  amount: number;
  type: 'expense' | 'income';
  date: string;
  category: string;
  payment_method: string;
  upi_reference?: string;
  description?: string;
  is_recurring: boolean;
  recurring_frequency?: string;
  ai_suggested_category?: string;
  ai_confidence?: number;
  is_user_confirmed: boolean;
  import_hash?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PaginatedTransactions {
  items: Transaction[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface CategorySpending {
  category: string;
  amount: number;
  percentage: number;
  count: number;
  color?: string;
}

export interface TrendPoint {
  date: string;
  income: number;
  expense: number;
  net: number;
}

export interface PaymentMethodSpending {
  method: string;
  amount: number;
  percentage: number;
  count: number;
}

export interface MonthlySpendPoint {
  month: string;
  income: number;
  expense: number;
  savings: number;
}

export interface BudgetVsActualPoint {
  category: string;
  budgeted: number;
  actual: number;
  remaining: number;
}

export interface DashboardSummary {
  period: string;
  start_date: string;
  end_date: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  mom_expense_change_percent?: number | null;
  highest_expense_category?: string | null;
  highest_category_amount?: number | null;
  active_budget?: number | null;
  budget_spent?: number | null;
  budget_utilization_percent?: number | null;
  transaction_count: number;
  recent_transactions: Transaction[];
  category_breakdown: CategorySpending[];
  daily_trends: TrendPoint[];
  payment_method_breakdown: PaymentMethodSpending[];
  monthly_history?: MonthlySpendPoint[];
  budget_vs_actual?: BudgetVsActualPoint[];
}

export interface CategoryBudgetStatus {
  category: string;
  budgeted: number;
  spent: number;
  remaining: number;
  percentage_used: number;
  status: 'ok' | 'warning' | 'exceeded';
}

export interface BudgetAlert {
  id: string;
  type: string;
  category?: string;
  threshold: number;
  message: string;
  current_percentage: number;
  spent: number;
  budget: number;
}

export interface Budget {
  id: string;
  user_id: string;
  month: string;
  overall_budget: number;
  category_budgets: Record<string, number>;
  alert_thresholds: number[];
  total_spent: number;
  overall_remaining: number;
  overall_percentage: number;
  category_statuses: CategoryBudgetStatus[];
  alerts: BudgetAlert[];
}

export interface ForecastPoint {
  date: string;
  predicted_expense: number;
  lower_bound: number;
  upper_bound: number;
  is_historical: boolean;
  actual_expense?: number | null;
}

export interface ForecastResponse {
  status: 'success' | 'insufficient_data';
  has_sufficient_data?: boolean;
  forecast_days: number;
  historical_days_used: number;
  predicted_total: number;
  predicted_daily_average: number;
  points: ForecastPoint[];
  influencing_factors: string[];
  overspending_risk_level: 'Low' | 'Medium' | 'High';
  message?: string;
}

export interface CategorizeResponse {
  predicted_category: string;
  confidence: number;
  model_type: string;
  explanation?: string;
  explanation_factors?: string[];
  alternative_suggestions?: { category: string; confidence: number }[];
}

export interface GroundedInsight {
  id: string;
  category_type: string;
  title: string;
  observation: string;
  actionable_recommendation: string;
  impact_amount?: number;
  severity: 'info' | 'warning' | 'critical' | 'positive';
}

export interface AIInsightsResponse {
  period: string;
  generated_at: string;
  insights: GroundedInsight[];
  monthly_summary: {
    total_spent: number;
    total_income: number;
    net_savings: number;
    savings_rate_percent: number;
    expense_count: number;
  };
  savings_potential_monthly: number;
  savings_potential_annual: number;
  ai_coach_summary?: string;
  ai_disclaimer: string;
}

export interface CategoryItem {
  id: string;
  name: string;
  type: string;
  color: string;
  icon: string;
  is_system: boolean;
}
