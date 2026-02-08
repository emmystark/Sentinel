-- ============================================================================
-- SENTINEL - Complete Supabase Setup
-- Run this script in Supabase SQL Editor to set up all tables for per-user data
-- ============================================================================

-- STEP 1: Create user_profiles table (synced with auth.users)
-- This table stores user profile information and settings
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE,
    name TEXT,
    monthly_income NUMERIC DEFAULT 0,
    fixed_bills NUMERIC DEFAULT 0,
    savings_goal NUMERIC DEFAULT 0,
    preferred_currency TEXT DEFAULT 'NGN',
    telegram_chat_id BIGINT,
    telegram_connected BOOLEAN DEFAULT FALSE,
    telegram_username TEXT,
    push_notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT monthly_income_positive CHECK (monthly_income >= 0),
    CONSTRAINT fixed_bills_positive CHECK (fixed_bills >= 0),
    CONSTRAINT savings_goal_positive CHECK (savings_goal >= 0)
);

-- STEP 2: Create transactions table
-- This table stores all financial transactions for each user
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    merchant TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    category TEXT NOT NULL DEFAULT 'Other',
    description TEXT,
    date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    currency TEXT DEFAULT 'NGN',
    source TEXT DEFAULT 'manual',  -- 'manual', 'receipt', 'telegram'
    ai_categorized BOOLEAN DEFAULT FALSE,
    telegram_message_id TEXT,
    receipt_image_url TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT amount_positive CHECK (amount > 0),
    CONSTRAINT valid_category CHECK (category IN ('Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Utilities', 'Health', 'Education', 'Other')),
    CONSTRAINT valid_currency CHECK (currency ~ '^[A-Z]{3}$'),
    CONSTRAINT valid_source CHECK (source IN ('manual', 'receipt', 'telegram'))
);

-- STEP 3: Create telegram_links table
-- This table links Telegram accounts to Sentinel user accounts
CREATE TABLE IF NOT EXISTS telegram_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    telegram_id BIGINT UNIQUE NOT NULL,
    telegram_username TEXT,
    telegram_first_name TEXT,
    telegram_last_name TEXT,
    verification_code TEXT,
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- STEP 4: Create chat_history table
-- This table persists chatbot conversations for AI financial advice
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tokens_used INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT valid_role CHECK (role IN ('user', 'assistant'))
);

-- STEP 5: Create operation_traces table for monitoring
-- This table logs API operations and performance metrics
CREATE TABLE IF NOT EXISTS operation_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'success', 'error', 'pending'
    model_name TEXT,
    latency_ms FLOAT,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT valid_status CHECK (status IN ('success', 'error', 'pending'))
);

-- STEP 6: Create user_preferences table for additional settings
-- This table stores user-specific preferences and settings
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'dark',  -- 'light', 'dark', 'auto'
    language TEXT DEFAULT 'en',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_digest_frequency TEXT DEFAULT 'weekly',  -- 'daily', 'weekly', 'monthly', 'never'
    budget_alert_threshold NUMERIC DEFAULT 80,  -- percentage
    auto_categorize BOOLEAN DEFAULT TRUE,
    receive_tips BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT valid_theme CHECK (theme IN ('light', 'dark', 'auto')),
    CONSTRAINT valid_frequency CHECK (email_digest_frequency IN ('daily', 'weekly', 'monthly', 'never')),
    CONSTRAINT threshold_valid CHECK (budget_alert_threshold >= 0 AND budget_alert_threshold <= 100)
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Transactions indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(user_id, category);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source);

-- Telegram indexes
CREATE INDEX IF NOT EXISTS idx_telegram_links_user_id ON telegram_links(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_links_telegram_id ON telegram_links(telegram_id);

-- Chat history indexes
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at DESC);

-- Operation traces indexes
CREATE INDEX IF NOT EXISTS idx_operation_traces_user_id ON operation_traces(user_id);
CREATE INDEX IF NOT EXISTS idx_operation_traces_created_at ON operation_traces(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Enforce per-user data isolation
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE telegram_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE operation_traces ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES - user_profiles
-- ============================================================================

-- Users can read their own profile
CREATE POLICY "Users can read own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = id);

-- Users can insert their profile (handled by trigger)
CREATE POLICY "Users can insert own profile"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ============================================================================
-- RLS POLICIES - transactions
-- ============================================================================

-- Users can read only their own transactions
CREATE POLICY "Users can read own transactions"
    ON transactions FOR SELECT
    USING (user_id = auth.uid());

-- Users can insert transactions for themselves
CREATE POLICY "Users can insert own transactions"
    ON transactions FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Users can update their own transactions
CREATE POLICY "Users can update own transactions"
    ON transactions FOR UPDATE
    USING (user_id = auth.uid());

-- Users can delete their own transactions
CREATE POLICY "Users can delete own transactions"
    ON transactions FOR DELETE
    USING (user_id = auth.uid());

-- ============================================================================
-- RLS POLICIES - telegram_links
-- ============================================================================

-- Users can read their own Telegram links
CREATE POLICY "Users can read own telegram links"
    ON telegram_links FOR SELECT
    USING (user_id = auth.uid());

-- Users can insert Telegram links for themselves
CREATE POLICY "Users can insert own telegram links"
    ON telegram_links FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Users can update their own Telegram links
CREATE POLICY "Users can update own telegram links"
    ON telegram_links FOR UPDATE
    USING (user_id = auth.uid());

-- ============================================================================
-- RLS POLICIES - chat_history
-- ============================================================================

-- Users can read their own chat history
CREATE POLICY "Users can read own chat history"
    ON chat_history FOR SELECT
    USING (user_id = auth.uid());

-- Users can insert messages to their chat history
CREATE POLICY "Users can insert own chat history"
    ON chat_history FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- ============================================================================
-- RLS POLICIES - operation_traces
-- ============================================================================

-- Users can read their own operation traces (for debugging)
CREATE POLICY "Users can read own operation traces"
    ON operation_traces FOR SELECT
    USING (user_id = auth.uid());

-- ============================================================================
-- RLS POLICIES - user_preferences
-- ============================================================================

-- Users can read their own preferences
CREATE POLICY "Users can read own preferences"
    ON user_preferences FOR SELECT
    USING (user_id = auth.uid());

-- Users can update their own preferences
CREATE POLICY "Users can update own preferences"
    ON user_preferences FOR UPDATE
    USING (user_id = auth.uid());

-- Users can insert their preferences
CREATE POLICY "Users can insert own preferences"
    ON user_preferences FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- ============================================================================
-- TRIGGERS - Automatic Profile Creation
-- ============================================================================

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Function to create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Create user profile
  INSERT INTO public.user_profiles (id, email, name, preferred_currency)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
    'NGN'  -- Default to Nigerian Naira
  )
  ON CONFLICT (id) DO NOTHING;
  
  -- Create user preferences with defaults
  INSERT INTO public.user_preferences (user_id)
  VALUES (NEW.id)
  ON CONFLICT (user_id) DO NOTHING;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create profile for new users
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ============================================================================
-- TRIGGERS - Update timestamps
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply timestamp trigger to all relevant tables
DROP TRIGGER IF EXISTS update_user_profiles_timestamp ON user_profiles;
CREATE TRIGGER update_user_profiles_timestamp
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE PROCEDURE public.update_timestamp();

DROP TRIGGER IF EXISTS update_transactions_timestamp ON transactions;
CREATE TRIGGER update_transactions_timestamp
  BEFORE UPDATE ON transactions
  FOR EACH ROW EXECUTE PROCEDURE public.update_timestamp();

DROP TRIGGER IF EXISTS update_telegram_links_timestamp ON telegram_links;
CREATE TRIGGER update_telegram_links_timestamp
  BEFORE UPDATE ON telegram_links
  FOR EACH ROW EXECUTE PROCEDURE public.update_timestamp();

DROP TRIGGER IF EXISTS update_user_preferences_timestamp ON user_preferences;
CREATE TRIGGER update_user_preferences_timestamp
  BEFORE UPDATE ON user_preferences
  FOR EACH ROW EXECUTE PROCEDURE public.update_timestamp();

-- ============================================================================
-- PERMISSIONS - Service Role (Backend)
-- Service role has full access for backend operations
-- ============================================================================

-- Note: Service role keys have full access by design
-- Use with caution and never expose service role key to frontend

-- ============================================================================
-- PERMISSIONS - Authenticated Users
-- Limited access for authenticated users (enforced by RLS)
-- ============================================================================

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON transactions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON telegram_links TO authenticated;
GRANT SELECT, INSERT ON chat_history TO authenticated;
GRANT SELECT ON operation_traces TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_preferences TO authenticated;

-- ============================================================================
-- VIEWS - Optional useful views for analysis
-- ============================================================================

-- Monthly spending summary
CREATE OR REPLACE VIEW user_monthly_spending AS
SELECT
    user_id,
    date_trunc('month', date) as month,
    SUM(amount) as total_spent,
    AVG(amount) as avg_transaction,
    COUNT(*) as transaction_count
FROM transactions
WHERE source != 'telegram' OR source IS NOT NULL
GROUP BY user_id, date_trunc('month', date);

-- Category breakdown
CREATE OR REPLACE VIEW user_category_spending AS
SELECT
    user_id,
    category,
    SUM(amount) as total,
    COUNT(*) as count,
    AVG(amount) as avg_amount
FROM transactions
GROUP BY user_id, category;

-- ============================================================================
-- CLEANUP & VERIFICATION
-- ============================================================================

-- Display table information
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;