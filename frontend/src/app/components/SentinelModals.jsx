
'use client'
import React, { useState } from 'react';
import styles from './styles/SentinelModals.module.css';

export default function SentinelModals() {
  const [activeModal, setActiveModal] = useState(null);

  const openModal = (modalName) => {
    setActiveModal(modalName);
  };

  const closeModal = () => {
    setActiveModal(null);
  };

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
          <div className={styles.dateTime}>Mon, Jan 19 • 9:30 PM</div>
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
        </div>

        <div className={styles.buttonGrid}>
          <button className={styles.demoButton} onClick={() => openModal('profile')}>
            Profile & Settings
          </button>
          <button className={styles.demoButton} onClick={() => openModal('developer')}>
            Developer Console
          </button>
          <button className={styles.demoButton} onClick={() => openModal('transaction')}>
            Transaction Detail
          </button>
          <button className={styles.demoButton} onClick={() => openModal('add')}>
            Add Transaction
          </button>
        </div>
      </main>

      <button className={styles.fab} onClick={() => openModal('add')}>
        <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
      </button>

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
                <h3 className={styles.profileName}>John Doe</h3>
                <p className={styles.profileEmail}>john.doe@example.com</p>
              </div>

              <div className={styles.settingField}>
                <label>
                  <span className={styles.fieldIcon}>$</span>
                  <span>Monthly Income: ₦300,000</span>
                </label>
                <button className={styles.editButton}>✏️</button>
              </div>

              <div className={styles.settingField}>
                <label>
                  <span className={styles.fieldIcon}>📄</span>
                  <span>Fixed Bills: ₦100,000</span>
                </label>
                <button className={styles.editButton}>✏️</button>
              </div>

              <div className={styles.settingField}>
                <label>
                  <span className={styles.fieldIcon}>#</span>
                  <span>Savings Goal: ₦50,000</span>
                </label>
                <button className={styles.editButton}>✏️</button>
              </div>

              <div className={styles.telegramSection}>
                <h4>Telegram Connection</h4>
                <p className={styles.telegramStatus}>Connected as @User123 ✅</p>
                <button className={styles.disconnectButton}>Disconnect</button>
              </div>

              <button className={styles.saveButton}>Save Changes</button>
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
      {activeModal === 'transaction' && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Transaction Detail</h2>
              <button className={styles.closeButton} onClick={closeModal}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.formGroup}>
                <label>Merchant</label>
                <input type="text" className={styles.input} defaultValue="Uber" />
              </div>

              <div className={styles.formGroup}>
                <label>Amount</label>
                <input type="text" className={styles.input} defaultValue="-₦4,000" />
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Date</label>
                  <input type="text" className={styles.input} defaultValue="Mon, Jan 19" />
                </div>
                <div className={styles.formGroup}>
                  <label>Category</label>
                  <select className={styles.select}>
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
                <p>Categorized as &apos;Transport&apos; because &apos;Uber&apos; matches known ride-sharing services. Risk analysis is neutral.</p>
                <p className={styles.traceId}>Opik Trace ID: #99281.</p>
              </div>

              <div className={styles.buttonRow}>
                <button className={styles.updateButton}>Update Transaction</button>
                <button className={styles.deleteButton}>Delete</button>
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
                  rows="5"
                />
                <button className={styles.micButton}>🎤</button>
              </div>

              <div className={styles.actionRow}>
                <button className={styles.scanButton}>
                  <span>📷</span> Scan Receipt
                </button>
                <select className={styles.dateSelect}>
                  <option>📅 Today</option>
                  <option>Yesterday</option>
                  <option>Custom Date</option>
                </select>
              </div>

              <button className={styles.analyzeButton}>Analyze & Log</button>
            </div>
          </div>
        </div>
      )}

      <div className={styles.bottomNav}>
        <div className={styles.navIcon}>👁️</div>
      </div>
    </div>
  );
}