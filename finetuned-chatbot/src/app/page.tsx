"use client";
import React, { useState } from 'react';
import styles from './components/styles/Dashboard.module.css';

interface Transaction {
  id: number;
  merchant: string;
  amount: number;
  category: string;
  icon: string;
  date: string;
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

export default function Dashboard() {
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([
    { id: 1, merchant: 'Chicken Republic', amount: -4500, category: 'Food', icon: '🍔', date: 'Mon, Jan 19' },
    { id: 2, merchant: 'Uber', amount: -4000, category: 'Transport', icon: '🚗', date: 'Mon, Jan 19' },
    { id: 3, merchant: 'Cafe Neo', amount: -1200, category: 'Food', icon: '☕', date: 'Mon, Jan 19' }
  ]);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile>({
    name: 'John Doe',
    email: 'john.doe@example.com',
    monthlyIncome: 300000,
    fixedBills: 100000,
    savingsGoal: 50000,
    telegramConnected: true,
    telegramUsername: '@User123'
  });
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    merchant: '',
    amount: '',
    category: 'Food',
    date: 'Today'
  });

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
      date: 'Today'
    });
  };

  const handleTransactionClick = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    openModal('transaction');
  };

  const handleUpdateTransaction = () => {
    if (selectedTransaction) {
      setTransactions(transactions.map(t => 
        t.id === selectedTransaction.id ? selectedTransaction : t
      ));
      closeModal();
    }
  };

  const handleDeleteTransaction = () => {
    if (selectedTransaction) {
      setTransactions(transactions.filter(t => t.id !== selectedTransaction.id));
      closeModal();
    }
  };

  const handleAddTransaction = () => {
    const newId = Math.max(...transactions.map(t => t.id)) + 1;
    const amount = parseFloat(newTransaction.amount) || 0;
    const categoryIcons: Record<string, string> = {
      'Food': '🍔',
      'Transport': '🚗',
      'Entertainment': '🎬',
      'Shopping': '🛍️',
      'Bills': '📄'
    };

    const transaction = {
      id: newId,
      merchant: newTransaction.merchant || 'Unknown',
      amount: -Math.abs(amount),
      category: newTransaction.category,
      icon: categoryIcons[newTransaction.category] || '💰',
      date: newTransaction.date === 'Today' ? 'Mon, Jan 19' : newTransaction.date
    };

    setTransactions([transaction, ...transactions]);
    closeModal();
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
  const dailyLimit = 5000;
  const remaining = dailyLimit - totalSpent;

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>S</div>
          <span className={styles.logoText}>sentinel</span>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.telegramStatus}>
            Telegram: Connected ✓
          </div>
          <div className={styles.userAvatar} onClick={() => openModal('profile')}>
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
        </div>
      </header>

      <main className={styles.mainContent}>
        <div className={styles.healthScore}>
          <div className={styles.scoreRing}>
            <svg className={styles.ringSvg} viewBox="0 0 200 200">
              <defs>
                <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#4ade80" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
              </defs>
              <circle cx="100" cy="100" r="85" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
              <circle cx="100" cy="100" r="85" fill="none" stroke="url(#ringGradient)" strokeWidth="8" strokeLinecap="round" strokeDasharray="534" strokeDashoffset="80" transform="rotate(-90 100 100)" />
            </svg>
            <div className={styles.scoreContent}>
              <div className={styles.scoreNumber}>84</div>
              <div className={styles.scoreLabel}>Financial Health:</div>
              <div className={styles.scoreStatus}>Stable</div>
            </div>
          </div>
          <p className={styles.stabilityMessage}>Stable because your pace is within the safe range.</p>
        </div>

        <div className={styles.fuelGauge}>
          <div className={styles.gaugeHeader}>
            <span className={styles.gaugeTitle}>Fuel Gauge</span>
            <span className={styles.gaugeAmount}>₦{totalSpent.toLocaleString()}</span>
          </div>
          <div className={styles.gaugeBar}>
            <div className={styles.gaugeFill} style={{width: `${(totalSpent / dailyLimit) * 100}%`}}></div>
          </div>
          <div className={styles.gaugeLabels}>
            <span className={styles.gaugeLeft}>₦{remaining.toLocaleString()} Left today</span>
            <span className={styles.gaugeCenter}>₦{totalSpent.toLocaleString()}</span>
            <span className={styles.gaugeRight}>₦{dailyLimit.toLocaleString()} (Limit)</span>
          </div>
          <div className={styles.gaugeTime}>
            <span>🕐 3:42 PM | Day 12 of 30</span>
          </div>
        </div>

        <div className={styles.todaysActivity}>
          <h2 className={styles.sectionTitle}>Today&apos;s Activity</h2>
          <div className={styles.activityCards}>
            {transactions.map(transaction => (
              <div 
                key={transaction.id} 
                className={styles.activityCard}
                onClick={() => handleTransactionClick(transaction)}
              >
                <div className={styles.activityIcon}>{transaction.icon}</div>
                <div className={styles.activityDetails}>
                  <div className={styles.activityName}>{transaction.merchant}</div>
                  <div className={styles.activityAmount}>₦{transaction.amount.toLocaleString()}</div>
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
              const icons: Record<string, string> = { Food: '🍴', Transport: '🚗', Entertainment: '🎬', Shopping: '🛍️', Bills: '📄' };
              return (
                <div key={category} className={styles.breakdownCard}>
                  <div className={styles.breakdownIcon}>{icons[category] || '💰'}</div>
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
      </main>

      <button className={styles.fab} onClick={() => openModal('add')}>
        <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
      </button>

      <div className={styles.bottomNav}>
        {/* <div className={styles.navIcon} onClick={() => openModal('developer')}>👁️</div> */}
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
                  <span className={styles.fieldIcon}>💰</span>
                  <span>Monthly Income: ₦{userProfile.monthlyIncome.toLocaleString()}</span>
                </label>
                <button className={styles.editButton}>✏️</button>
              </div>

              <div className={styles.settingField}>
                <label>
                  <span className={styles.fieldIcon}>📄</span>
                  <span>Fixed Bills: ₦{userProfile.fixedBills.toLocaleString()}</span>
                </label>
                <button className={styles.editButton}>✏️</button>
              </div>

              <div className={styles.settingField}>
                <label>
                  <span className={styles.fieldIcon}>🎯</span>
                  <span>Savings Goal: ₦{userProfile.savingsGoal.toLocaleString()}</span>
                </label>
                <button className={styles.editButton}>✏️</button>
              </div>

              <div className={styles.telegramSection}>
                <h4>Telegram Connection</h4>
                <p className={styles.telegramConnectedText}>
                  Connected as {userProfile.telegramUsername} ✅
                </p>
                <button className={styles.disconnectButton}>Disconnect</button>
              </div>

              <button className={styles.saveButton} onClick={closeModal}>Save Changes</button>
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
                  value={`₦${selectedTransaction.amount.toLocaleString()}`}
                  onChange={(e) => {
                    const value = e.target.value.replace(/[₦,]/g, '');
                    setSelectedTransaction({...selectedTransaction, amount: parseFloat(value) || 0});
                  }}
                />
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
                  </select>
                </div>
              </div>

              <div className={styles.insightBox}>
                <h4>AI Insight (Opik Trace)</h4>
                <p>Categorized as &apos;{selectedTransaction.category}&apos; because &apos;{selectedTransaction.merchant}&apos; matches known {selectedTransaction.category.toLowerCase()} services. Risk analysis is neutral.</p>
                <p className={styles.traceId}>Opik Trace ID: #{99280 + selectedTransaction.id}.</p>
              </div>

              <div className={styles.buttonRow}>
                <button className={styles.updateButton} onClick={handleUpdateTransaction}>Update Transaction</button>
                <button className={styles.deleteButton} onClick={handleDeleteTransaction}>Delete</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Transaction Modal */}
      {activeModal === 'add' && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Add Transaction</h2>
              <button className={styles.closeButton} onClick={closeModal}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.textareaGroup}>
                <textarea 
                  className={styles.textarea} 
                  placeholder="e.g., 'Spent 5k on fuel'"
                  rows={4}
                  value={newTransaction.description}
                  onChange={(e) => setNewTransaction({...newTransaction, description: e.target.value})}
                />
                <button className={styles.micButton}>🎤</button>
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

              <div className={styles.formGroup}>
                <label>Amount (₦)</label>
                <input 
                  type="number" 
                  className={styles.input} 
                  placeholder="5000"
                  value={newTransaction.amount}
                  onChange={(e) => setNewTransaction({...newTransaction, amount: e.target.value})}
                />
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Category</label>
                  <select 
                    className={styles.select}
                    value={newTransaction.category}
                    onChange={(e) => setNewTransaction({...newTransaction, category: e.target.value})}
                  >
                    <option>Food</option>
                    <option>Transport</option>
                    <option>Entertainment</option>
                    <option>Shopping</option>
                    <option>Bills</option>
                  </select>
                </div>
                <div className={styles.formGroup}>
                  <label>Date</label>
                  <select 
                    className={styles.select}
                    value={newTransaction.date}
                    onChange={(e) => setNewTransaction({...newTransaction, date: e.target.value})}
                  >
                    <option>Today</option>
                    <option>Yesterday</option>
                    <option>Custom Date</option>
                  </select>
                </div>
              </div>

              <div className={styles.actionRow}>
                <button className={styles.scanButton}>
                  <span>📷</span> Scan Receipt
                </button>
              </div>

              <button className={styles.analyzeButton} onClick={handleAddTransaction}>Analyze & Log</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}