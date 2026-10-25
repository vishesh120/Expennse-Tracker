import api from './client';
import {
  AuthResponse,
  User,
  Transaction,
  PaginatedTransactions,
  DashboardSummary,
  Budget,
  ForecastResponse,
  AIInsightsResponse,
  CategoryItem,
  CategorizeResponse,
} from '../types';

export const authApi = {
  register: (data: { email: string; password: string; full_name: string; monthly_income?: number; occupation?: string }) =>
    api.post<AuthResponse>('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post<AuthResponse>('/auth/login', data),
  getProfile: () =>
    api.get<User>('/auth/me'),
  updateProfile: (data: Partial<User>) =>
    api.patch<User>('/auth/me', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
  logout: () =>
    api.post('/auth/logout'),
};

export const transactionsApi = {
  list: (params: {
    page?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
    category?: string;
    type?: string;
    payment_method?: string;
    search?: string;
    sort_by?: string;
    sort_order?: string;
  }) => api.get<PaginatedTransactions>('/transactions', { params }),

  get: (id: string) =>
    api.get<Transaction>(`/transactions/${id}`),

  create: (data: Omit<Transaction, 'id' | 'user_id' | 'created_at' | 'updated_at'>) =>
    api.post<Transaction>('/transactions', data),

  update: (id: string, data: Partial<Transaction>) =>
    api.patch<Transaction>(`/transactions/${id}`, data),

  delete: (id: string) =>
    api.delete(`/transactions/${id}`),

  exportCsv: (params?: Record<string, string>) =>
    api.get('/transactions/export/csv', { params, responseType: 'blob' }),
};

export const dashboardApi = {
  getSummary: (period = 'this_month', startDate?: string, endDate?: string) =>
    api.get<DashboardSummary>('/dashboard/summary', {
      params: { period, start_date: startDate, end_date: endDate },
    }),
};

export const budgetsApi = {
  list: () =>
    api.get<Budget[]>('/budgets'),
  getByMonth: (month: string) =>
    api.get<Budget>(`/budgets/${month}`),
  upsert: (data: {
    month: string;
    overall_budget: number;
    category_budgets: Record<string, number>;
    alert_thresholds?: number[];
  }) => api.post<Budget>('/budgets', data),
  delete: (id: string) =>
    api.delete(`/budgets/${id}`),
};

export const aiApi = {
  categorize: (data: { title: string; description?: string; merchant?: string; amount?: number }) =>
    api.post<CategorizeResponse>('/ai/categorize', data),

  submitFeedback: (data: {
    title: string;
    predicted_category: string;
    confirmed_category: string;
    confidence?: number;
  }) => api.post('/ai/feedback', data),

  getForecast: (days = 30) =>
    api.get<ForecastResponse>('/ai/forecast', { params: { days } }),

  getInsights: () =>
    api.get<AIInsightsResponse>('/ai/insights'),

  seedSamples: (days = 45) =>
    api.post<{ message: string; count: number }>('/ai/seed-samples', null, { params: { days } }),
};

export const categoriesApi = {
  list: () =>
    api.get<CategoryItem[]>('/categories'),
  create: (data: { name: string; type?: string; color?: string; icon?: string }) =>
    api.post<CategoryItem>('/categories', data),
  delete: (id: string) =>
    api.delete(`/categories/${id}`),
};

export const importsApi = {
  uploadCsv: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<{
      total_rows_processed: number;
      imported_count: number;
      duplicate_count: number;
      failed_count: number;
      status: string;
    }>('/imports/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
