/**
 * API Service - Handles all backend communication
 * Configured to work with Python FastAPI backend
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Types for API responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface Transaction {
  id: string;
  merchant: string;
  amount: number;
  category: string;
  description?: string;
  date: string;
  created_at?: string;
}

export interface UserProfile {
  id?: string;
  email: string;
  name: string;
  monthly_income: number;
  fixed_bills: number;
  savings_goal: number;
  telegram_connected?: boolean;
  telegram_username?: string;
  telegram_user_id?: string;
}

export interface ReceiptAnalysis {
  merchant: string;
  amount: number;
  currency?: string;
  date?: string;
  description?: string;
  items?: string[];
  category: string;
}

export interface BudgetAlert {
  alert_level: string;
  alert_message: string;
  metrics: {
    monthly_income: number;
    fixed_bills: number;
    available_budget: number;
    spent_this_month: number;
    remaining_budget: number;
    budget_used_percentage: number;
    savings_goal: number;
  };
  category_alerts: Record<string, any>;
  transactions_count: number;
}

export interface SpendingAdvice {
  success: boolean;
  advice: string;
  context?: any;
}

// Helper function to make API calls
async function apiCall<T>(
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any,
  userId?: string
): Promise<T> {
  const url = `${BACKEND_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add user ID if provided
  if (userId) {
    headers['user-id'] = userId;
  }

  const options: RequestInit = {
    method,
    headers,
  };

  if (data && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || errorData.detail || `API Error: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error(`API Error [${method} ${endpoint}]:`, error);
    throw error;
  }
}

// ==================== AUTHENTICATION ====================

export const authService = {
  signup: (email: string, password: string, name: string) =>
    apiCall<any>('/api/auth/signup', 'POST', { email, password, name }),

  login: (email: string, password: string) =>
    apiCall<any>('/api/auth/login', 'POST', { email, password }),

  logout: () =>
    apiCall<any>('/api/auth/logout', 'POST'),

  getProfile: (userId: string) =>
    apiCall<UserProfile>('/api/auth/profile', 'GET', undefined, userId),

  updateProfile: (userId: string, profile: Partial<UserProfile>) =>
    apiCall<UserProfile>('/api/auth/profile', 'PUT', profile, userId),
};

// ==================== TRANSACTIONS ====================

export const transactionService = {
  getTransactions: (userId: string, limit: number = 100, offset: number = 0) =>
    apiCall<Transaction[]>(
      `/api/transactions?limit=${limit}&offset=${offset}`,
      'GET',
      undefined,
      userId
    ),

  getTransaction: (userId: string, id: string) =>
    apiCall<Transaction>(`/api/transactions/${id}`, 'GET', undefined, userId),

  createTransaction: (userId: string, transaction: Partial<Transaction>) =>
    apiCall<{ success: boolean; transaction: Transaction }>(
      '/api/transactions',
      'POST',
      transaction,
      userId
    ),

  updateTransaction: (userId: string, id: string, transaction: Partial<Transaction>) =>
    apiCall<{ success: boolean; transaction: Transaction }>(
      `/api/transactions/${id}`,
      'PUT',
      transaction,
      userId
    ),

  deleteTransaction: (userId: string, id: string) =>
    apiCall<{ success: boolean; message: string }>(
      `/api/transactions/${id}`,
      'DELETE',
      undefined,
      userId
    ),

  getStats: (userId: string) =>
    apiCall<any>('/api/transactions/stats/summary', 'GET', undefined, userId),
};

// ==================== AI ANALYSIS ====================

export const aiService = {
  analyzeReceipt: (userId: string, imageUrl?: string, imageBase64?: string) =>
    apiCall<ReceiptAnalysis>(
      '/api/ai/analyze-receipt',
      'POST',
      { image_url: imageUrl, image_base64: imageBase64 },
      userId
    ),

  analyzeReceiptUpload: async (userId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${BACKEND_URL}/api/ai/analyze-receipt-upload`;
    const headers: HeadersInit = {
      'user-id': userId,
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Upload failed: ${response.status}`);
    }

    return response.json() as Promise<ReceiptAnalysis>;
  },

  categorizeTransaction: (userId: string, merchant: string, amount: number, description?: string) =>
    apiCall<{ success: boolean; category: string }>(
      '/api/ai/categorize',
      'POST',
      { merchant, amount, description },
      userId
    ),

  analyzeSpending: (
    userId: string,
    monthlyIncome: number,
    fixedBills: number,
    savingsGoal: number
  ) =>
    apiCall<any>(
      '/api/ai/analyze-spending',
      'POST',
      { monthly_income: monthlyIncome, fixed_bills: fixedBills, savings_goal: savingsGoal },
      userId
    ),

  getAdvice: (userId: string) =>
    apiCall<SpendingAdvice>('/api/ai/get-advice', 'POST', undefined, userId),

  checkBudgetAlert: (userId: string) =>
    apiCall<BudgetAlert>('/api/ai/budget-alert', 'POST', undefined, userId),
};

// ==================== TELEGRAM ====================

export const telegramService = {
  verifyConnection: (userId: string) =>
    apiCall<{ verified: boolean; username?: string; user_id?: string; message: string }>(
      '/api/telegram/verify',
      'GET',
      undefined,
      userId
    ),

  connectAccount: (userId: string, username: string, telegramUserId?: string) =>
    apiCall<{ success: boolean; message: string; username: string }>(
      '/api/telegram/connect',
      'POST',
      { telegram_username: username, telegram_user_id: telegramUserId },
      userId
    ),

  disconnectAccount: (userId: string) =>
    apiCall<{ success: boolean; message: string }>(
      '/api/telegram/disconnect',
      'POST',
      undefined,
      userId
    ),

  sendAlert: (userId: string) =>
    apiCall<{ success: boolean; message: string }>(
      '/api/telegram/send-alert',
      'POST',
      undefined,
      userId
    ),

  sendAdvice: (userId: string) =>
    apiCall<{ success: boolean; message: string }>(
      '/api/telegram/send-advice',
      'POST',
      undefined,
      userId
    ),
};

// ==================== HEALTH CHECK ====================

export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
};

export default {
  authService,
  transactionService,
  aiService,
  telegramService,
  healthCheck,
  apiCall,
};
