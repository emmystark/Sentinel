"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './components/styles/Dashboard.module.css';
import { useAuth } from '@/hooks/useAuth';

interface Transaction {
  id: string;
  merchant: string;
  amount: number;
  category: string;
  icon: string;
  date: string;
  description?: string;
  ai_categorized?: boolean;
  currency?: string;
}

interface UserProfile {
  name: string;
  email: string;
  monthlyIncome: number;
  fixedBills: number;
  savingsGoal: number;
  telegramConnected: boolean;
  telegramUsername: string;
}


const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://sentinel-pchb.onrender.com';

export default function Dashboard() {
  const { user, loading: authLoading, signOut, accessToken } = useAuth();
  const userId = user?.id ?? 'default-user';
  
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [profileLoaded, setProfileLoaded] = useState(false);
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    merchant: '',
    amount: '',
    category: 'Food',
    currency: 'NGN',
    date: 'Today'
  });
  const [receiptImage, setReceiptImage] = useState<File | null>(null);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);
  const [scannedData, setScannedData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [operationLoading, setOperationLoading] = useState(false);  // FOR specific operations only
  const [error, setError] = useState<string | null>(null);
  const [healthScore, setHealthScore] = useState(0);
  const [healthStatus, setHealthStatus] = useState('Building Profile');
  const [aiTips, setAiTips] = useState<string[]>([]);
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  const [telegramVerified, setTelegramVerified] = useState(false);
  const [telegramVerifying, setTelegramVerifying] = useState(false);
  const [telegramBotUsername, setTelegramBotUsername] = useState<string>('');
  const [telegramLinkCode, setTelegramLinkCode] = useState('');
  const [telegramLinking, setTelegramLinking] = useState(false);
  
  // Chatbot state
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState('');

  // Fetch profile from API - per user
  const fetchProfile = async () => {
    if (!user?.id || !accessToken) return;
    try {
      const p = await apiCall('/api/auth/profile', 'GET');
      setUserProfile({
        name: p.name || (user.email?.split('@')[0] || 'User'),
        email: p.email || user.email || '',
        monthlyIncome: Number(p.monthly_income) || 0,
        fixedBills: Number(p.fixed_bills) || 0,
        savingsGoal: Number(p.savings_goal) || 0,
        telegramConnected: !!p.telegram_chat_id,
        telegramUsername: p.telegram_username ? `@${p.telegram_username}` : ''
      });
    } catch (e) {
      console.warn('Could not fetch profile:', e);
      // Fallback for new users - create profile with 0 amounts
      setUserProfile({
        name: user.email?.split('@')[0] || 'User',
        email: user.email || '',
        monthlyIncome: 0,
        fixedBills: 0,
        savingsGoal: 0,
        telegramConnected: false,
        telegramUsername: ''
      });
    } finally {
      setProfileLoaded(true);
    }
  };

  // Fetch transactions and profile on user load
  useEffect(() => {
    if (authLoading || !user || !accessToken) return; // Wait for auth and token to load
    
    console.log('Auth ready, fetching profile and transactions...');
    fetchProfile();
    fetchTransactions(); // This will call generateAiTips after fetching
    verifyTelegramConnection();
    setCurrentTime(new Date().toLocaleTimeString());
    
    // Update time every second
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    
    return () => clearInterval(timer);
  }, [user, authLoading, accessToken]);

  // After transactions are loaded, regenerate tips with profile data
  useEffect(() => {
    if (transactions.length > 0 && userProfile && profileLoaded) {
      console.log('Profile and transactions loaded, regenerating tips...');
      // Give AI tips a second to be generated from fetchTransactions
      // This ensures we have both transactions and profile data
    }
  }, [transactions, userProfile, profileLoaded]);

  // Verify Telegram: bot status + user link status
  const verifyTelegramConnection = async () => {
    try {
      setTelegramVerifying(true);
      const [verifyRes, settingsRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/telegram/verify`),
        apiCall('/api/ai/telegram/settings', 'GET').catch(() => ({}))
      ]);
      if (verifyRes.ok) {
        const data = await verifyRes.json();
        if (data.bot_username || data.username) {
          setTelegramBotUsername(data.bot_username || data.username || '');
        }
      }
      const linked = !!(settingsRes && (settingsRes as { telegram_chat_id?: number }).telegram_chat_id);
      setTelegramVerified(linked);
      if (linked && userProfile) {
        setUserProfile(prev => prev ? { ...prev, telegramConnected: true, telegramUsername: prev.telegramUsername || '@linked' } : null);
      }
    } catch (err) {
      setTelegramVerified(false);
      console.warn('Telegram integration not available (optional):', err);
    } finally {
      setTelegramVerifying(false);
    }
  };

  const handleTelegramLinkWithCode = async () => {
    const code = telegramLinkCode.trim();
    if (!code || code.length < 4) {
      setError('Enter the 6-character code from Telegram');
      return;
    }
    setTelegramLinking(true);
    setError(null);
    try {
      const res = await apiCall('/api/telegram/link-with-code', 'POST', { code });
      if (res.success) {
        setTelegramVerified(true);
        setUserProfile(prev => prev ? { ...prev, telegramConnected: true, telegramUsername: res.telegram_username ? `@${res.telegram_username}` : '@linked' } : null);
        setTelegramLinkCode('');
        
        // Show success message
        const successMsg = `✅ Telegram connected successfully!\nYou can now send expense messages like "Chicken Republic 4500" to log transactions.`;
        setError(null); // Clear any errors
        
        // Set a temporary success alert
        const tempAlert = document.createElement('div');
        tempAlert.style.position = 'fixed';
        tempAlert.style.top = '20px';
        tempAlert.style.right = '20px';
        tempAlert.style.backgroundColor = '#4ade80';
        tempAlert.style.color = 'white';
        tempAlert.style.padding = '16px 24px';
        tempAlert.style.borderRadius = '8px';
        tempAlert.style.zIndex = '9999';
        tempAlert.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        tempAlert.textContent = '✅ Telegram linked successfully!';
        document.body.appendChild(tempAlert);
        
        setTimeout(() => {
          tempAlert.remove();
        }, 3000);
      } else {
        setError(res.error || 'Failed to link');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to link');
    } finally {
      setTelegramLinking(false);
    }
  };

  async function getHealthScore() {
  const response = await fetch('/api/ai/financial-health', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'user-id': userId
    },
    body: JSON.stringify({
      monthly_income: 5000,
      fixed_bills: 1500,
      savings_goal: 500
    })
  });
  
  const data = await response.json();
  return data.health_score;
}

  // Generate AI tips based on expenses
  const generateAiTips = async () => {
    try {
      if (transactions.length === 0) {
        setAiTips(['Start logging expenses to get personalized financial tips!']);
        return;
      }

      const categoryTotals = calculateCategoryTotals();
      
      // Generate dynamic tips based on user spending patterns
      const response = await apiCall('/api/ai/health-tips', 'POST', {
        transactions: transactions,
        monthlyIncome: userProfile?.monthlyIncome || 0,
        fixedBills: userProfile?.fixedBills || 0,
        savingsGoal: userProfile?.savingsGoal || 0,
        categoryTotals: categoryTotals
      });

      setAiTips(response.tips || ['Keep tracking your expenses!']);
      setCurrentTipIndex(0);
    } catch (err) {
      console.error('Failed to generate tips:', err);
      setAiTips(['Keep tracking your expenses for better insights!']);
    }
  };

  // Financial advisor chatbot - Enhanced handler
  const handleChatSubmit = async () => {
    if (!chatInput.trim() || chatLoading || !userProfile) return;

    const userMessage = chatInput;
    setChatInput('');
    
    // Add user message immediately for responsiveness
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    try {
      // Send request: uploaded transactions + profile expected expenses
      const response = await apiCall('/api/ai/chat', 'POST', {
        message: userMessage,
        transactions: transactions,
        monthlyIncome: userProfile.monthlyIncome,
        fixedBills: userProfile.fixedBills,
        savingsGoal: userProfile.savingsGoal
      });

      if (response.success && response.advice) {
        // Add advisor response
        setChatMessages(prev => [...prev, { 
          role: 'advisor', 
          content: response.advice,
          duration: response.duration
        }]);
      } else {
        setChatMessages(prev => [...prev, { 
          role: 'advisor', 
          content: '❌ ' + (response.error || 'Could not generate advice. Try again.')
        }]);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Network error';
      console.error('Chat error:', err);
      setChatMessages(prev => [...prev, { 
        role: 'advisor', 
        content: `⚠️ Error: ${errorMsg}. Please try again.`
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Compress image before sending
  const compressImage = (base64String: string): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.src = base64String;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d')!;
        
        // Reduce dimensions if image is too large
        let width = img.width;
        let height = img.height;
        const maxWidth = 800;
        const maxHeight = 800;
        
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height);
          width = width * ratio;
          height = height * ratio;
        }
        
        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);
        
        // Compress to lower quality
        const compressed = canvas.toDataURL('image/jpeg', 0.6);
        resolve(compressed);
      };
    });
  };

  // Handle receipt image upload
  const handleReceiptUpload = async (file: File) => {
    setReceiptImage(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setReceiptPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Scan receipt
    await scanReceipt(file);
  };

  // Scan receipt image using AI
  const scanReceipt = async (file: File) => {
    setOperationLoading(true);  // Use operationLoading for receipt scanning
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        let base64 = reader.result as string;
        
        // Compress image if it's too large
        if (base64.length > 5000000) {
          try {
            base64 = await compressImage(base64);
          } catch (err) {
            console.warn('Image compression failed, using original');
          }
        }
        
        try {
          const result = await apiCall('/api/ai/analyze-receipt', 'POST', {
            image_base64: base64
          });

          setScannedData(result);
          
          // Auto-fill form with scanned data
          setNewTransaction(prev => ({
            ...prev,
            merchant: result.merchant || '',
            amount: (result.amount && result.amount > 0) ? result.amount.toString() : '',
            category: result.category || 'Food',
            currency: result.currency || 'NGN',
            description: result.description || `Receipt scan - ${new Date().toLocaleString()}`
          }));

          // Only show error if both merchant AND amount failed to extract
          if ((!result.merchant || result.merchant === 'Merchant') && result.amount === 0) {
            setError('Receipt scanned but data unclear. Please fill in merchant name and amount manually.');
          } else {
            setError(null);
          }
        } catch (err) {
          setError('Failed to scan receipt. Please fill in the details manually or try a clearer image.');
          console.error('Scan error:', err);
        }
      };
      reader.readAsDataURL(file);
    } catch (err) {
      setError('Error processing receipt');
      console.error('Upload error:', err);
    } finally {
      setOperationLoading(false);
    }
  };

  // Calculate health score based on spending data
  const calculateHealthScore = (transactionList: Transaction[], income: number) => {
    if (!transactionList || transactionList.length === 0) {
      setHealthScore(0);
      setHealthStatus('Building Profile');
      return;
    }

    const totalSpent = transactionList.reduce((sum, t) => sum + Math.abs(t.amount), 0);
    const spendingRatio = income > 0 ? (totalSpent / income) * 100 : 0;

    let score = 0;
    let status = 'Building Profile';

    if (spendingRatio > 100) {
      score = 0;
      status = 'Critical Overspend';
    } else if (spendingRatio > 90) {
      score = 10;
      status = 'Severely Strained';
    } else if (spendingRatio > 80) {
      score = 20;
      status = 'Heavily Burdened';
    } else if (spendingRatio > 70) {
      score = 30;
      status = 'Significantly Stretched';
    } else if (spendingRatio > 60) {
      score = 40;
      status = 'Noticeably Tight';
    } else if (spendingRatio > 50) {
      score = 50;
      status = 'Moderate';
    } else if (spendingRatio > 40) {
      score = 60;
      status = 'Comfortable';
    } else if (spendingRatio > 30) {
      score = 70;
      status = 'Healthy';
    } else if (spendingRatio > 20) {
      score = 80;
      status = 'Very Healthy';
    } else if (spendingRatio > 10) {
      score = 90;
      status = 'Excellent';
    } else {
      score = 100;
      status = 'Outstanding';
    }

    setHealthScore(score);
    setHealthStatus(status);
  };

  // API helper function - IMPROVED
  const apiCall = async (endpoint: string, method: string = 'GET', body?: object) => {
    try {
      setError(null);
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
          // Use Authorization header with Bearer token if available
          ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : { 'user-id': userId })
        }
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      console.log(`🔵 API Call: ${method} ${endpoint}`);
      const response = await fetch(`${BACKEND_URL}${endpoint}`, options);
      
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { error: `HTTP ${response.status}` };
        }
        console.error(`❌ API Error ${response.status}:`, errorData);
        throw new Error(errorData.detail || errorData.error || 'API request failed');
      }

      const data = await response.json();
      console.log(`✅ API Success: ${method} ${endpoint}`, data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
      console.error('❌ API Error:', message);
      throw err;
    }
  };

  // Fetch all transactions - IMPROVED
  const fetchTransactions = async () => {
    try {
      if (!accessToken) {
        console.warn('⚠️ No access token available, skipping transaction fetch');
        setTransactions([]);
        return;
      }
      
      console.log('📊 Fetching transactions from API...');
      const data = await apiCall('/api/transactions', 'GET');
      
      console.log('📦 Raw transaction data received:', data);
      
      // Handle different response formats
      let transactionArray: any[] = [];
      
      if (Array.isArray(data)) {
        // Direct array response
        transactionArray = data;
      } else if (data && Array.isArray(data.transactions)) {
        // Wrapped in transactions property
        transactionArray = data.transactions;
      } else if (data && Array.isArray(data.data)) {
        // Wrapped in data property
        transactionArray = data.data;
      } else if (data && typeof data === 'object') {
        // Single transaction object
        transactionArray = [data];
      } else {
        console.warn('⚠️ Unexpected transaction data format:', data);
        setTransactions([]);
        return;
      }
      
      console.log(`✅ Successfully fetched ${transactionArray.length} transactions from database`);
      
      // Convert to display format with icons
      const formattedData = transactionArray.map((t: any) => ({
        id: t.id || t.transaction_id || String(Math.random()),
        merchant: t.merchant || 'Unknown Merchant',
        amount: t.amount > 0 ? -t.amount : t.amount, // Ensure negative for display
        category: t.category || 'Other',
        icon: getCategoryIcon(t.category || 'Other'),
        date: t.date || t.created_at || new Date().toISOString(),
        description: t.description || '',
        ai_categorized: t.ai_categorized || false,
        currency: t.currency || 'NGN'
      }));
      
      setTransactions(formattedData);
      console.log('✅ Transactions set in state, total:', formattedData.length);
      
      // Calculate health score based on spending
      if (userProfile) {
        calculateHealthScore(formattedData, userProfile.monthlyIncome);
      }
      
      // Generate tips after transactions are loaded
      setTimeout(() => {
        if (formattedData.length > 0) {
          console.log('💡 Generating AI tips for', formattedData.length, 'transactions...');
          generateAiTips();
        } else {
          console.log('💡 No transactions available, using default tip');
          setAiTips(['Start logging expenses to get personalized financial tips!']);
        }
      }, 100);
      
    } catch (err) {
      console.error('❌ Failed to fetch transactions:', err);
      // Don't clear transactions on error - keep previous data if available
      setTransactions(prev => {
        console.log('⚠️ Keeping previous transactions:', prev?.length || 0);
        return prev || [];
      });
    }
  };

  const getCategoryIcon = (category: string): string => {
    const icons: Record<string, string> = {
      'Food': '🍔',
      'Transport': '🚗',
      'Entertainment': '🎬',
      'Shopping': '🛍️',
      'Bills': '📄',
      'Utilities': '⚡',
      'Health': '🏥',
      'Education': '📚',
      'Other': '💰'
    };
    return icons[category] || '💰';
  };

  const getCurrencySymbol = (currencyCode: string): string => {
    const symbols: Record<string, string> = {
      'NGN': '₦',
      'USD': '$',
      'EUR': '€',
      'GBP': '£',
      'JPY': '¥',
      'CAD': 'C$',
      'AUD': 'A$',
      'INR': '₹',
      'ZAR': 'R',
      'KES': 'Sh',
      'GHS': '₵'
    };
    return symbols[currencyCode] || currencyCode;
  };

  const openModal = (modalName: string | null) => {
    setActiveModal(modalName);
  };

  const closeModal = () => {
    setActiveModal(null);
    setSelectedTransaction(null);
    setNewTransaction({
      description: '',
      merchant: '',
      amount: '',
      category: 'Food',
      currency: 'NGN',
      date: 'Today'
    });
  };

  const handleSaveProfile = async () => {
    if (!userProfile) return;
    setOperationLoading(true);
    try {
      const result = await apiCall('/api/auth/profile', 'PUT', {
        name: userProfile.name,
        monthly_income: userProfile.monthlyIncome,
        fixed_bills: userProfile.fixedBills,
        savings_goal: userProfile.savingsGoal
      });
      
      if (result.success) {
        // Update local state with confirmed data from backend
        setUserProfile(prev => prev ? {
          ...prev,
          monthlyIncome: result.profile?.monthly_income ?? prev.monthlyIncome,
          fixedBills: result.profile?.fixed_bills ?? prev.fixedBills,
          savingsGoal: result.profile?.savings_goal ?? prev.savingsGoal,
          name: result.profile?.name ?? prev.name
        } : null);
        
        // Show success message
        const tempAlert = document.createElement('div');
        tempAlert.style.position = 'fixed';
        tempAlert.style.top = '20px';
        tempAlert.style.right = '20px';
        tempAlert.style.backgroundColor = '#4ade80';
        tempAlert.style.color = 'white';
        tempAlert.style.padding = '16px 24px';
        tempAlert.style.borderRadius = '8px';
        tempAlert.style.zIndex = '9999';
        tempAlert.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        tempAlert.textContent = 'Profile updated successfully!';
        document.body.appendChild(tempAlert);
        
        setTimeout(() => {
          tempAlert.remove();
        }, 3000);
        
        closeModal();
      }
    } catch (err) {
      console.error('Failed to save profile:', err);
      setError('Failed to save profile. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleTransactionClick = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    openModal('transaction');
  };

  const handleEditProfile = (field: string, newValue: number) => {
    if (!userProfile) return;
    setUserProfile({ ...userProfile, [field]: newValue });
    // Recalculate health score with new profile data
    const newIncome = field === 'monthlyIncome' ? newValue : userProfile.monthlyIncome;
    calculateHealthScore(transactions, newIncome);
  };

  const handleUpdateTransaction = async () => {
    if (selectedTransaction && selectedTransaction.id) {
      setLoading(true);
      try {
        const updatedTx = await apiCall(`/api/transactions/${selectedTransaction.id}`, 'PUT', {
          merchant: selectedTransaction.merchant,
          amount: Math.abs(selectedTransaction.amount),
          category: selectedTransaction.category,
          currency: selectedTransaction.currency,
          date: selectedTransaction.date,
          description: selectedTransaction.description
        });
        
        // Update local state
        const updatedTransactions = transactions.map(t => 
          t.id === selectedTransaction.id ? { ...updatedTx, icon: getCategoryIcon(updatedTx.category), amount: -Math.abs(updatedTx.amount) } : t
        );
        setTransactions(updatedTransactions);
        
        // Recalculate health score
        if (userProfile) {
          calculateHealthScore(updatedTransactions, userProfile.monthlyIncome);
        }
        closeModal();
      } catch (err) {
        console.error('Failed to update transaction:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleDeleteTransaction = async () => {
    if (selectedTransaction && selectedTransaction.id) {
      if (confirm('Are you sure you want to delete this transaction?')) {
        setLoading(true);
        try {
          await apiCall(`/api/transactions/${selectedTransaction.id}`, 'DELETE');
          const updatedTransactions = transactions.filter(t => t.id !== selectedTransaction.id);
          setTransactions(updatedTransactions);
          
          // Recalculate health score
          if (userProfile) {
            calculateHealthScore(updatedTransactions, userProfile.monthlyIncome);
          }
          closeModal();
        } catch (err) {
          console.error('Failed to delete transaction:', err);
        } finally {
          setLoading(false);
        }
      }
    }
  };

  const handleAddTransaction = async () => {
    setOperationLoading(true);  // Use operationLoading for transaction operations
    setError('');
    try {
      const merchant = newTransaction.merchant?.trim() || '';
      const amount = parseFloat(newTransaction.amount) || 0;
      
      // Validation: need both merchant and amount
      if (!merchant) {
        setError('Merchant name is required. Type or upload a receipt with it clearly visible.');
        setOperationLoading(false);
        return;
      }

      if (!amount || amount <= 0) {
        setError('Amount must be greater than 0. Type or upload a receipt with the amount clearly visible.');
        setOperationLoading(false);
        return;
      }

      // Use manually selected category (user choice takes priority)
      let category = newTransaction.category;

      // Create transaction
      const response = await apiCall('/api/transactions', 'POST', {
        merchant: merchant,
        amount: Math.abs(amount),
        category,
        description: newTransaction.description,
        currency: newTransaction.currency,
        date: new Date().toISOString()
      });

      // Extract the actual transaction object from response
      const transaction = response.transaction || response;
      
      // Add to local state
      const newTx = { 
        ...transaction, 
        icon: getCategoryIcon(transaction.category), 
        amount: transaction.amount ? (transaction.amount > 0 ? -transaction.amount : transaction.amount) : -Math.abs(amount)
      };
      const updatedTransactions = [newTx, ...transactions];
      setTransactions(updatedTransactions);
      
      console.log('Transaction added successfully:', newTx);
      
      // Recalculate health score
      if (userProfile) {
        calculateHealthScore(updatedTransactions, userProfile.monthlyIncome);
      }

      // Show success message and close modal
      const tempAlert = document.createElement('div');
      tempAlert.style.position = 'fixed';
      tempAlert.style.top = '20px';
      tempAlert.style.right = '20px';
      tempAlert.style.backgroundColor = '#4ade80';
      tempAlert.style.color = 'white';
      tempAlert.style.padding = '16px 24px';
      tempAlert.style.borderRadius = '8px';
      tempAlert.style.zIndex = '9999';
      tempAlert.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
      tempAlert.textContent = 'Transaction added successfully!';
      document.body.appendChild(tempAlert);
      
      setTimeout(() => {
        tempAlert.remove();
      }, 3000);

      closeModal();
    } catch (err) {
      console.error('Failed to add transaction:', err);
    } finally {
      setOperationLoading(false);
    }
  };

  const calculateCategoryTotals = () => {
    const totals: Record<string, number> = {};
    transactions.forEach(t => {
      if (!totals[t.category]) {
        totals[t.category] = 0;
      }
      totals[t.category] += Math.abs(t.amount);
    });
    return totals;
  };

  const categoryTotals = calculateCategoryTotals();
  const totalSpent = transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0);
  const dailyLimit = userProfile?.monthlyIncome || 5000;
  const remaining = dailyLimit - totalSpent;

  // Show login screen if not authenticated
  if (!user && !authLoading) {
    return (
      <div className={styles.app}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', backgroundColor: '#0f172a' }}>
          <div style={{ textAlign: 'center', color: '#e2e8f0' }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🔐</div>
            <h1 style={{ fontSize: '28px', marginBottom: '10px' }}>Please Log In</h1>
            <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '20px' }}>You need to be authenticated to access your dashboard</p>
            <Link href="/login" style={{
              display: 'inline-block',
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              borderRadius: '8px',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              Go to Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Show loading while auth and profile load - with proper spinner
  if (authLoading || !profileLoaded || !userProfile) {
    return (
      <div className={styles.app} style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh', 
        backgroundColor: '#0f172a' 
      }}>
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000,
          backdropFilter: 'blur(2px)'
        }}>
          <div style={{
            textAlign: 'center',
            backgroundColor: '#1e293b',
            padding: '40px',
            borderRadius: '16px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              margin: '0 auto 20px',
              borderRadius: '50%',
              border: '3px solid rgba(59, 130, 246, 0.2)',
              borderTop: '3px solid #3b82f6',
              animation: 'spin 0.8s linear infinite'
            }}/>
            <p style={{ color: '#e2e8f0', fontSize: '16px', fontWeight: '500', margin: 0 }}>
              Loading your dashboard...
            </p>
            <style>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.logo}>
          {/* <div className={styles.logoIcon}>S</div>
          <span className={styles.logoText}>sentinel</span> */}
          <img src="./logo.png" height={25} width={60} alt="" />
        </div>
        <div className={styles.headerRight}>
          {user && (
            <button onClick={signOut} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '13px', cursor: 'pointer', marginRight: '8px' }}>
              Logout
            </button>
          )}
          {/* {!user && (
            <Link href="/login" style={{ color: '#60a5fa', fontSize: '14px', textDecoration: 'none', marginRight: '8px' }}>Login</Link>
          )} */}
          {telegramVerified && (
            <div className={styles.telegramStatus}>
              Telegram: Connected ✓
            </div>
          )}
          <div className={styles.userAvatar} onClick={() => openModal('profile')}>
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
        </div>
      </header>
{/* 
      {error && (
        <div style={{ 
          backgroundColor: '#fee', 
          color: '#c00', 
          padding: '12px 16px', 
          margin: '10px 20px',
          borderRadius: '8px',
          fontSize: '14px'
        }}>
          {error}
        </div>
      )} */}

      <main className={styles.mainContent}>
        <div className={styles.healthScore}>
          <div className={styles.scoreRing}>
            <svg className={styles.ringSvg} viewBox="0 0 200 200">
              <defs>
                <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor={healthScore > 70 ? '#4ade80' : healthScore > 50 ? '#eab308' : '#ef4444'} />
                  <stop offset="100%" stopColor={healthScore > 70 ? '#3b82f6' : healthScore > 50 ? '#f97316' : '#dc2626'} />
                </linearGradient>
              </defs>
              <circle cx="100" cy="100" r="85" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
              <circle 
                cx="100" 
                cy="100" 
                r="85" 
                fill="none" 
                stroke="url(#ringGradient)" 
                strokeWidth="8" 
                strokeLinecap="round" 
                strokeDasharray={`${(healthScore / 100) * 534} 534`}
                strokeDashoffset="0"
                transform="rotate(-90 100 100)"
                style={{ transition: 'stroke-dasharray 0.5s ease' }}
              />
            </svg>
            <div className={styles.scoreContent}>
              <div className={styles.scoreNumber}>{healthScore}</div>
              <div className={styles.scoreLabel}>Financial Health:</div>
              <div className={styles.scoreStatus}>{healthStatus}</div>
            </div>
          </div>
          <p className={styles.stabilityMessage}>
            {healthScore === 0 ? 'Start adding transactions to build your profile.' :
             healthScore > 70 ? 'Excellent! Your spending is well-controlled.' : 
             healthScore > 50 ? 'Stable. Your pace is within a reasonable range.' :
             'Fair. Consider reducing discretionary spending.'}
          </p>
        </div>

        {/* AI Tips Section */}
        {aiTips.length > 0 && (
          <div style={{
            marginTop: '20px',
            padding: '15px',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderLeft: '4px solid #3b82f6',
            borderRadius: '8px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h3 style={{ margin: 0, color: '#60a5fa', fontSize: '16px' }}>Financial Tip</h3>
              <div style={{ display: 'flex', gap: '5px' }}>
                <button
                  onClick={() => setCurrentTipIndex((prev) => (prev - 1 + aiTips.length) % aiTips.length)}
                  style={{ padding: '4px 8px', background: '#3b82f6', border: 'none', color: 'white', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}
                >
                  ← Prev
                </button>
                <span style={{ color: '#888', fontSize: '12px', padding: '4px 8px' }}>
                  {currentTipIndex + 1} / {aiTips.length}
                </span>
                <button
                  onClick={() => setCurrentTipIndex((prev) => (prev + 1) % aiTips.length)}
                  style={{ padding: '4px 8px', background: '#3b82f6', border: 'none', color: 'white', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}
                >
                  Next →
                </button>
              </div>
            </div>
            <p style={{ margin: 0, color: '#e0e7ff', lineHeight: '1.5' }}>
              {aiTips[currentTipIndex]}
            </p>
          </div>
        )}
        <br />
        <div className={styles.fuelGauge}>
          <div className={styles.gaugeHeader}>
            <span className={styles.gaugeTitle}>Spending Overview</span>
            <span className={styles.gaugeAmount}>₦{totalSpent.toLocaleString()}</span>
          </div>
          <div className={styles.gaugeBar}>
            <div className={styles.gaugeFill} style={{width: `${Math.min((totalSpent / dailyLimit) * 100, 100)}%`}}></div>
          </div>
          <div className={styles.gaugeLabels}>
            <span className={styles.gaugeLeft}>₦{(userProfile.monthlyIncome - totalSpent).toLocaleString()} Left</span>
            <span className={styles.gaugeCenter}>₦{totalSpent.toLocaleString()}</span>
            <span className={styles.gaugeRight}>₦{userProfile.monthlyIncome.toLocaleString()} Goal</span>
          </div>
          <div className={styles.gaugeTime}>
              <span>{currentTime || '00:00:00'} | {transactions.length} transaction{transactions.length !== 1 ? 's' : ''}</span>
          </div>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
            Loading...
          </div>
        )}

        {!loading && transactions.length > 0 && (
          <>
            <div className={styles.todaysActivity}>
              <h2 className={styles.sectionTitle}>Today&apos;s Activity</h2>
              <div className={styles.activityCards}>
                {transactions.slice(0, 5).map(transaction => (
                  <div 
                    key={transaction.id} 
                    className={styles.activityCard}
                    onClick={() => handleTransactionClick(transaction)}
                  >
                    <div className={styles.activityIcon}>{transaction.icon}</div>
                    <div className={styles.activityDetails}>
                      <div className={styles.activityName}>{transaction.merchant}</div>
                      <div className={styles.activityAmount}>{getCurrencySymbol(transaction.currency || 'NGN')}{Math.abs(transaction.amount).toLocaleString()}</div>
                      <div className={styles.activityCategory}>↑ {transaction.category} ↗</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.categoryBreakdown}>
              <h2 className={styles.sectionTitle}>Category Breakdown</h2>
              <div className={styles.breakdownCards}>
                {Object.entries(categoryTotals).map(([category, amount]) => {
                  const icons: Record<string, string> = { 
                    Food: '🍴', 
                    Transport: '🚗', 
                    Entertainment: '🎬', 
                    Shopping: '🛍️', 
                    Bills: '📄',
                    Utilities: '⚡',
                    Health: '🏥',
                    Education: '📚'
                  };
                  return (
                    <div key={category} className={styles.breakdownCard}>
                      <div className={styles.breakdownIcon}>{icons[category] || '$'}</div>
                      <div className={styles.breakdownDetails}>
                        <div className={styles.breakdownHeader}>
                          <span className={styles.breakdownName}>{category}</span>
                          <span className={styles.breakdownAmount}>₦{amount.toLocaleString()}</span>
                        </div>
                        <div className={styles.breakdownBar}>
                          <div className={styles.breakdownFill} style={{width: `${(amount / dailyLimit) * 100}%`}}></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {!loading && transactions.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: '#888' }}>
            <p>No transactions yet. Click the + button to add one!</p>
          </div>
        )}
      </main>

      <button className={styles.fab} onClick={() => openModal('add')}>
        <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
      </button>

      <div className={styles.bottomNav}>
        <div style={{ cursor: 'pointer', fontSize: '20px' }} onClick={() => openModal('chatbot')} title="Financial Advisor">
         <img src="./image.png" width={60} height={20} alt="" />
        </div>
      </div>

      {/* Profile & Settings Modal */}
      {activeModal === 'profile' && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Profile & Settings</h2>
              <button className={styles.closeButton} onClick={closeModal}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.profileSection}>
                <div className={styles.profileAvatar}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <h3 className={styles.profileName}>{userProfile.name}</h3>
                <p className={styles.profileEmail}>{userProfile.email}</p>
              </div>

              <div className={styles.settingField}>
                <label>
                  <span>Monthly Income: ₦{userProfile.monthlyIncome.toLocaleString()}</span>
                </label>
                <input 
                  type="number" 
                  className={styles.editButton}
                  style={{ width: '120px', padding: '4px 8px' }}
                  placeholder="Income"
                  onChange={(e) => handleEditProfile('monthlyIncome', parseFloat(e.target.value) || 0)}
                  defaultValue={userProfile.monthlyIncome}
                />
              </div>

              <div className={styles.settingField}>
                <label>
                  <span>Fixed Bills: ₦{userProfile.fixedBills.toLocaleString()}</span>
                </label>
                <input 
                  type="number" 
                  className={styles.editButton}
                  style={{ width: '120px', padding: '4px 8px' }}
                  placeholder="Bills"
                  onChange={(e) => handleEditProfile('fixedBills', parseFloat(e.target.value) || 0)}
                  defaultValue={userProfile.fixedBills}
                />
              </div>

              <div className={styles.settingField}>
                <label>
                  <span>Savings Goal: ₦{userProfile.savingsGoal.toLocaleString()}</span>
                </label>
                <input 
                  type="number" 
                  className={styles.editButton}
                  style={{ width: '120px', padding: '4px 8px' }}
                  placeholder="Goal"
                  onChange={(e) => handleEditProfile('savingsGoal', parseFloat(e.target.value) || 0)}
                  defaultValue={userProfile.savingsGoal}
                />
              </div>

              <div className={styles.telegramSection}>
                <h4>Telegram Connection</h4>
                {telegramVerified ? (
                  <>
                    <p className={styles.telegramConnectedText} style={{ color: '#4ade80' }}>
                      Connected
                    </p>
                    <p style={{ fontSize: '13px', color: '#888' }}>Send expense messages like &quot;Chicken Republic 4500&quot; to log transactions</p>
                    <button className={styles.disconnectButton} onClick={() => setTelegramVerified(false)}>Disconnect</button>
                  </>
                ) : (
                  <>
                    <p style={{ color: '#fbbf24', fontSize: '14px' }}>
                      Connect Telegram to log expenses via chat
                    </p>
                    <button 
                      className={styles.analyzeButton}
                      onClick={() => {
                        const bot = telegramBotUsername || process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || 'SentinelFinanceBot';
                        window.open(`https://t.me/${bot.replace('@', '')}?start=connect`, '_blank');
                      }}
                      disabled={telegramVerifying}
                    >
                      Open Telegram Bot
                    </button>
                    <div style={{ marginTop: '12px' }}>
                      <input
                        type="text"
                        placeholder="Enter 6-char code from Telegram"
                        value={telegramLinkCode}
                        onChange={(e) => setTelegramLinkCode(e.target.value.toUpperCase().slice(0, 6))}
                        maxLength={6}
                        style={{ padding: '8px', width: '180px', marginRight: '8px' }}
                      />
                      <button className={styles.analyzeButton} onClick={handleTelegramLinkWithCode} disabled={telegramLinking}>
                        {telegramLinking ? 'Linking...' : 'Link'}
                      </button>
                    </div>
                  </>
                )}
              </div>

              <button className={styles.saveButton} onClick={handleSaveProfile}>Save Changes</button>
            </div>
          </div>
        </div>
      )}

      {/* Developer Console Modal */}
      {activeModal === 'developer' && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={`${styles.modal} ${styles.wideModal}`} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Developer Console / Opik Trace Log</h2>
              <button className={styles.closeButton} onClick={closeModal}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.consoleOutput}>
                <div className={styles.consoleLine}>
                  <span className={styles.timestamp}>[21:35:01]</span>
                  <span className={styles.infoTag}>INFO:</span>
                  <span>Webhook received from Telegram user @User123.</span>
                </div>
                <div className={styles.consoleLine}>
                  <span className={styles.timestamp}>[21:35:02]</span>
                  <span className={styles.traceTag}>TRACE:</span>
                  <span>Agent receiving image payload for analysis.</span>
                </div>
                <div className={styles.consoleLine}>
                  <span className={styles.timestamp}>[21:35:04]</span>
                  <span className={styles.traceTag}>TRACE:</span>
                  <span>Vision API parsing receipt successful. Extracted: Merchant=&apos;Chicken Republic&apos;, Amount=4500.</span>
                </div>
                <div className={styles.consoleLine}>
                  <span className={styles.timestamp}>[21:35:05]</span>
                  <span className={styles.infoTag}>INFO:</span>
                  <span>Risk Analysis Engine triggered. Current Daily Utilization: 85%.</span>
                </div>
                <div className={styles.consoleLine}>
                  <span className={styles.timestamp}>[21:35:05]</span>
                  <span className={styles.traceTag}>TRACE:</span>
                  <span>Opik Trace ID: #99282 logged for AI reasoning chain.</span>
                </div>
                <div className={styles.consoleLine}>
                  <span className={styles.timestamp}>[21:35:06]</span>
                  <span className={styles.infoTag}>INFO:</span>
                  <span>Transaction saved to Supabase. Dashboard updated.</span>
                </div>
                <div className={styles.consoleLine}>
                  <span className={styles.timestamp}>[21:35:07]</span>
                  <span className={styles.debugTag}>DEBUG:</span>
                  <span>Cron job for Daily Vibe Check scheduled for 22:00.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Detail Modal */}
      {activeModal === 'transaction' && selectedTransaction && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Transaction Detail</h2>
              <button className={styles.closeButton} onClick={closeModal}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.formGroup}>
                <label>Merchant</label>
                <input 
                  type="text" 
                  className={styles.input} 
                  value={selectedTransaction.merchant}
                  onChange={(e) => setSelectedTransaction({...selectedTransaction, merchant: e.target.value})}
                />
              </div>

              <div className={styles.formGroup}>
                <label>Amount</label>
                <input 
                  type="text" 
                  className={styles.input} 
                  value={`${getCurrencySymbol(selectedTransaction.currency || 'NGN')}${Math.abs(selectedTransaction.amount).toLocaleString()}`}
                  onChange={(e) => {
                    const value = e.target.value.replace(/[₦$€£¥C$A$₹RShKES\u20b5,GHS]/g, '');
                    setSelectedTransaction({...selectedTransaction, amount: -Math.abs(parseFloat(value) || 0)});
                  }}
                />
              </div>

              <div className={styles.formGroup}>
                <label>Currency</label>
                <select 
                  className={styles.select}
                  value={selectedTransaction.currency || 'NGN'}
                  onChange={(e) => setSelectedTransaction({...selectedTransaction, currency: e.target.value})}
                >
                  <option value="NGN">NGN (₦)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="JPY">JPY (¥)</option>
                  <option value="CAD">CAD (C$)</option>
                  <option value="AUD">AUD (A$)</option>
                  <option value="INR">INR (₹)</option>
                  <option value="ZAR">ZAR (R)</option>
                  <option value="KES">KES (Sh)</option>
                  <option value="GHS">GHS (₵)</option>
                </select>
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Date</label>
                  <input 
                    type="text" 
                    className={styles.input} 
                    value={selectedTransaction.date}
                    onChange={(e) => setSelectedTransaction({...selectedTransaction, date: e.target.value})}
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Category</label>
                  <select 
                    className={styles.select}
                    value={selectedTransaction.category}
                    onChange={(e) => setSelectedTransaction({...selectedTransaction, category: e.target.value})}
                  >
                    <option>Transport</option>
                    <option>Food</option>
                    <option>Entertainment</option>
                    <option>Shopping</option>
                    <option>Bills</option>
                    <option>Utilities</option>
                    <option>Health</option>
                    <option>Education</option>
                  </select>
                </div>
              </div>

              <div className={styles.insightBox}>
                <h4>AI Insight (Opik Trace)</h4>
                <p>Categorized as &apos;{selectedTransaction.category}&apos; because &apos;{selectedTransaction.merchant}&apos; matches known {selectedTransaction.category.toLowerCase()} services. Risk analysis is neutral.</p>
                <p className={styles.traceId}>AI Categorized: {selectedTransaction.ai_categorized ? 'Yes ✓' : 'Manual'}</p>
              </div>

              <div className={styles.buttonRow}>
                <button className={styles.updateButton} onClick={handleUpdateTransaction} disabled={loading}>
                  {loading ? 'Updating...' : 'Update Transaction'}
                </button>
                <button className={styles.deleteButton} onClick={handleDeleteTransaction} disabled={loading}>
                  {loading ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Transaction Modal */}
      {activeModal === 'add' && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={`${styles.modal} ${styles.wideModal}`} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Add Transaction</h2>
              <button className={styles.closeButton} onClick={closeModal}>✕</button>
            </div>
            <div className={styles.modalBody}>
              {/* Receipt Upload Section */}
              <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'rgba(74, 222, 128, 0.1)', borderRadius: '8px', border: '2px dashed #4ade80' }}>
                <h3 style={{ marginTop: 0, color: '#4ade80' }}>Scan Receipt (Optional)</h3>
                <p style={{ fontSize: '14px', color: '#aaa' }}>Upload a bank receipt or receipt image - AI will extract merchant, amount, and category</p>
                
                {receiptPreview && (
                  <div style={{ marginBottom: '15px' }}>
                    <img src={receiptPreview} alt="Receipt" style={{ maxWidth: '200px', maxHeight: '200px', borderRadius: '8px', border: '1px solid #4ade80' }} />
                    <button 
                      onClick={() => { setReceiptImage(null); setReceiptPreview(null); setScannedData(null); }}
                      style={{ marginLeft: '10px', padding: '6px 12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      Clear
                    </button>
                  </div>
                )}

                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => e.target.files && handleReceiptUpload(e.target.files[0])}
                  style={{ padding: '10px', borderRadius: '4px', border: '1px solid #4ade80', cursor: 'pointer' }}
                />

                {scannedData && (
                  <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#1e293b', borderRadius: '4px', fontSize: '13px', color: '#a1f265' }}>
                    Receipt scanned! Fields auto-filled below.
                  </div>
                )}

                {loading && (
                  <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#1e293b', borderRadius: '4px', fontSize: '13px', color: '#fbbf24' }}>
                    Scanning receipt...
                  </div>
                )}
              </div>

              {/* Or Manual Entry Section */}
              <div style={{ marginBottom: '10px', padding: '10px 0', textAlign: 'center', color: '#888', fontSize: '14px' }}>
                — OR ENTER MANUALLY —
              </div>

              <div className={styles.textareaGroup}>
                <textarea 
                  className={styles.textarea} 
                  placeholder="e.g., 'Spent 5k on fuel at Shell gas station'"
                  rows={3}
                  value={newTransaction.description}
                  onChange={(e) => setNewTransaction({...newTransaction, description: e.target.value})}
                />
              </div>

              <div className={styles.formGroup}>
                <label>Merchant</label>
                <input 
                  type="text" 
                  className={styles.input} 
                  placeholder="e.g., Shell Gas Station"
                  value={newTransaction.merchant}
                  onChange={(e) => setNewTransaction({...newTransaction, merchant: e.target.value})}
                />
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Amount</label>
                  <input 
                    type="number" 
                    className={styles.input} 
                    placeholder="5000"
                    value={newTransaction.amount}
                    onChange={(e) => setNewTransaction({...newTransaction, amount: e.target.value})}
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Category</label>
                  <select 
                    className={styles.select}
                    value={newTransaction.category}
                    onChange={(e) => setNewTransaction({...newTransaction, category: e.target.value})}
                  >
                    <option value="Food">🍔 Food & Dining</option>
                    <option value="Transport">🚗 Transport</option>
                    <option value="Entertainment">🎬 Entertainment</option>
                    <option value="Shopping">🛍️ Shopping</option>
                    <option value="Bills">📄 Bills & Utilities</option>
                    <option value="Health">⚕️ Health & Medical</option>
                    <option value="Education">📚 Education</option>
                    <option value="Other">$ Other</option>
                  </select>
                </div>
                <div className={styles.formGroup}>
                  <label>Currency</label>
                  <select 
                    className={styles.select}
                    value={newTransaction.currency}
                    onChange={(e) => setNewTransaction({...newTransaction, currency: e.target.value})}
                  >
                    <option value="NGN">NGN (₦) - Nigerian Naira</option>
                    <option value="USD">USD ($) - US Dollar</option>
                    <option value="EUR">EUR (€) - Euro</option>
                    <option value="GBP">GBP (£) - British Pound</option>
                    <option value="JPY">JPY (¥) - Japanese Yen</option>
                    <option value="CAD">CAD (C$) - Canadian Dollar</option>
                    <option value="AUD">AUD (A$) - Australian Dollar</option>
                    <option value="INR">INR (₹) - Indian Rupee</option>
                    <option value="ZAR">ZAR (R) - South African Rand</option>
                    <option value="KES">KES (Sh) - Kenyan Shilling</option>
                    <option value="GHS">GHS (₵) - Ghanaian Cedi</option>
                  </select>
                </div>
              </div>
                <br />
                <br />
                <br />
                <br />
                <br />
                <br />
                <br />
                <br />
              <button className={styles.analyzeButton} onClick={handleAddTransaction} disabled={loading}>
                {loading ? 'Processing...' : 'Analyze & Log'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Financial Advisor Chatbot Modal - Dynamic */}
      {activeModal === 'chatbot' && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={`${styles.modal} ${styles.wideModal}`} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div>
                <h2 style={{ margin: '0 0 4px 0' }}>Sentinel Financial Advisor</h2>
                <p style={{ margin: 0, fontSize: '12px', color: '#888' }}>AI-powered personalized financial guidance</p>
              </div>
              <button className={styles.closeButton} onClick={closeModal}>✕</button>
            </div>
            
            <div className={styles.modalBody} style={{ display: 'flex', flexDirection: 'column', height: '550px' }}>
              
              {/* Quick Stats Bar */}
              {transactions.length > 0 && (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr 1fr',
                  gap: '10px',
                  marginBottom: '12px',
                  padding: '12px',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  borderRadius: '6px',
                  border: '1px solid rgba(59, 130, 246, 0.3)'
                }}>
                  <div style={{ textAlign: 'center', fontSize: '12px' }}>
                    <div style={{ color: '#3b82f6', fontWeight: 'bold', fontSize: '14px' }}>
                      {transactions.length}
                    </div>
                    <div style={{ color: '#888', marginTop: '2px' }}>Transactions</div>
                  </div>
                  <div style={{ textAlign: 'center', fontSize: '12px' }}>
                    <div style={{ color: '#10b981', fontWeight: 'bold', fontSize: '14px' }}>
                      ₦{(transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0) / 1000).toFixed(0)}k
                    </div>
                    <div style={{ color: '#888', marginTop: '2px' }}>Spending</div>
                  </div>
                  <div style={{ textAlign: 'center', fontSize: '12px' }}>
                    <div style={{ 
                      color: (transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0) / userProfile.monthlyIncome) > 0.8 ? '#ef4444' : '#f59e0b', 
                      fontWeight: 'bold', 
                      fontSize: '14px' 
                    }}>
                      {((transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0) / userProfile.monthlyIncome) * 100).toFixed(0)}%
                    </div>
                    <div style={{ color: '#888', marginTop: '2px' }}>of Income</div>
                  </div>
                </div>
              )}

              {/* Messages Container */}
              <div style={{ 
                flex: 1, 
                overflowY: 'auto', 
                marginBottom: '12px', 
                padding: '12px',
                backgroundColor: '#0f172a',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column'
              }}>
                
                {chatMessages.length === 0 ? (
                  <div style={{ 
                    margin: 'auto',
                    textAlign: 'center',
                    color: '#888'
                  }}>
                    <div style={{ fontSize: '24px', marginBottom: '12px' }}>💬</div>
                    <p style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>
                      Sentinel Financial Advisor
                    </p>
                    <p style={{ fontSize: '12px', marginBottom: '16px', color: '#666' }}>
                      Ask me anything about your spending habits!
                    </p>
                    <div style={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      gap: '6px',
                      fontSize: '12px',
                      color: '#60a5fa'
                    }}>
                      <p>"How can I save more?"</p>
                      <p>"Is my food spending high?"</p>
                      <p>"Where should I cut back?"</p>
                      <p>"What's my spending ratio?"</p>
                    </div>
                  </div>
                ) : (
                  <>
                    {chatMessages.map((msg, idx) => (
                      <div key={idx} style={{ 
                        marginBottom: '10px', 
                        display: 'flex', 
                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        alignItems: 'flex-end',
                        gap: '8px'
                      }}>
                        {msg.role === 'advisor' && (
                          <div style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            backgroundColor: '#3b82f6',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '12px',
                            flexShrink: 0
                          }}>
                            ★
                          </div>
                        )}
                        <div style={{
                          maxWidth: '75%',
                          padding: '10px 13px',
                          borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                          backgroundColor: msg.role === 'user' ? '#3b82f6' : '#1e293b',
                          color: msg.role === 'user' ? '#fff' : '#e2e8f0',
                          fontSize: '13px',
                          lineHeight: '1.5',
                          wordBreak: 'break-word',
                          border: msg.role === 'advisor' ? '1px solid #334155' : 'none'
                        }}>
                          {msg.content}
                        </div>
                        {msg.role === 'user' && (
                          <div style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            backgroundColor: '#3b82f6',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '12px',
                            flexShrink: 0
                          }}>
                            👤
                          </div>
                        )}
                      </div>
                    ))}
                    
                    {chatLoading && (
                      <div style={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'flex-end', gap: '8px', marginTop: '10px' }}>
                        <div style={{
                          width: '24px',
                          height: '24px',
                          borderRadius: '50%',
                          backgroundColor: '#3b82f6',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '12px'
                        }}>
                          ★
                        </div>
                        <div style={{
                          padding: '10px 13px',
                          borderRadius: '18px 18px 18px 4px',
                          backgroundColor: '#1e293b',
                          color: '#60a5fa',
                          fontSize: '13px',
                          border: '1px solid #334155'
                        }}>
                          <span style={{ display: 'inline-flex', gap: '3px' }}>
                            <span style={{ animation: 'pulse 1s infinite', opacity: 0.7 }}>●</span>
                            <span style={{ animation: 'pulse 1s infinite 0.2s', opacity: 0.7 }}>●</span>
                            <span style={{ animation: 'pulse 1s infinite 0.4s', opacity: 0.7 }}>●</span>
                          </span>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Input Area - Dynamic */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  placeholder={chatLoading ? 'Waiting for response...' : 'Ask Sentinel about your finances...'}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !chatLoading && chatInput.trim()) {
                      handleChatSubmit();
                    }
                  }}
                  disabled={chatLoading}
                  style={{
                    flex: 1,
                    padding: '11px 14px',
                    borderRadius: '8px',
                    border: '1px solid #334155',
                    backgroundColor: '#1e293b',
                    color: '#fff',
                    fontSize: '13px',
                    fontFamily: 'inherit',
                    outline: 'none',
                    transition: 'all 0.2s'
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = '#3b82f6';
                    e.currentTarget.style.backgroundColor = '#0f172a';
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = '#334155';
                    e.currentTarget.style.backgroundColor = '#1e293b';
                  }}
                />
                <button
                  onClick={handleChatSubmit}
                  disabled={chatLoading || !chatInput.trim()}
                  style={{
                    padding: '11px 20px',
                    borderRadius: '8px',
                    border: 'none',
                    backgroundColor: chatLoading || !chatInput.trim() ? '#334155' : '#3b82f6',
                    color: '#fff',
                    cursor: chatLoading || !chatInput.trim() ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    fontWeight: 'bold',
                    transition: 'all 0.2s',
                    opacity: chatLoading || !chatInput.trim() ? 0.6 : 1
                  }}
                >
                  {chatLoading ? '⏳' : '→'}
                </button>
              </div>

              {/* Footer Info */}
              {chatMessages.length > 0 && (
                <div style={{ 
                  marginTop: '8px',
                  fontSize: '11px',
                  color: '#666',
                  textAlign: 'center'
                }}>
                  Advice based on {transactions.length} transactions
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Interactive Loading Overlay - Only for specific operations */}
      {operationLoading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000,
          backdropFilter: 'blur(2px)'
        }}>
          <div style={{
            textAlign: 'center',
            backgroundColor: '#1e293b',
            padding: '40px',
            borderRadius: '16px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              margin: '0 auto 20px',
              borderRadius: '50%',
              border: '3px solid rgba(59, 130, 246, 0.2)',
              borderTop: '3px solid #3b82f6',
              animation: 'spin 0.8s linear infinite'
            }}/>
            <p style={{ color: '#e2e8f0', fontSize: '16px', fontWeight: '500' }}>
              Processing...
            </p>
            <style>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        </div>
      )}
    </div>
  );
}