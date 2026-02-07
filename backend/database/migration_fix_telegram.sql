-- Migration: Fix telegram_chat_id column and add missing fields
-- Run this in Supabase SQL Editor to fix the database schema

-- 1. Add missing columns to user_profiles if they don't exist
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT UNIQUE,
ADD COLUMN IF NOT EXISTS telegram_connected BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS telegram_username TEXT,
ADD COLUMN IF NOT EXISTS push_notification_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS notification_token TEXT,
ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{"telegram": true, "push": true, "email": false}'::jsonb;

-- 2. Create transactions table if it doesn't exist
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    merchant TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    category TEXT,
    description TEXT,
    source TEXT,
    ai_categorized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    CONSTRAINT valid_amount CHECK (amount > 0)
);

-- 3. Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_user_profiles_telegram_chat_id ON user_profiles(telegram_chat_id);

-- 4. Create notifications table for storing notification history
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    title TEXT,
    message TEXT,
    channel TEXT,
    sent_at TIMESTAMP DEFAULT now(),
    read_at TIMESTAMP,
    CONSTRAINT valid_type CHECK (type IN ('budget_alert', 'spending_insight', 'health_tip', 'goal_progress', 'high_risk_transaction', 'weekly_summary', 'monthly_summary'))
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications(sent_at);

-- 5. Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON transactions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON notifications TO authenticated;
