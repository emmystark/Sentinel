-- Migration: Add currency field to transactions table
-- This migration adds support for dynamic currency handling
-- Run this in Supabase SQL Editor

-- Add currency column to transactions table
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'NGN';

-- Also add currency preference to user_profiles for default currency selection
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS preferred_currency TEXT DEFAULT 'NGN';

-- Create an index on currency for faster queries
CREATE INDEX IF NOT EXISTS idx_transactions_currency ON transactions(currency);

-- Add check constraint to ensure valid currency codes (3 letter ISO format)
ALTER TABLE transactions ADD CONSTRAINT check_currency_length CHECK (LENGTH(currency) = 3);

-- Update the description to be clearer
COMMENT ON COLUMN transactions.currency IS 'ISO 4217 currency code (e.g., NGN, USD, EUR, GBP)';
COMMENT ON COLUMN user_profiles.preferred_currency IS 'Default currency for new transactions (ISO 4217 code)';
