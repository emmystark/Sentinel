# 🗄️ Supabase Setup Guide for Sentinel

## Overview

This guide walks you through setting up Supabase for the Sentinel personal finance app. Supabase handles:
- User authentication (sign up, login)
- Per-user data isolation (each user sees only their data)
- Real-time database synchronization
- Automatic profile creation on signup

---

## Prerequisites

- ✅ Supabase account created at https://supabase.com
- ✅ Project created in Supabase dashboard
- ✅ Project URL and API keys copied to `.env` files
- ✅ PostgreSQL database available (included with Supabase)

---

## Step 1: Navigate to Supabase SQL Editor

1. Go to your Supabase dashboard: https://app.supabase.com
2. Select your Sentinel project
3. Click **SQL Editor** in the left sidebar
4. Click **New Query**

---

## Step 2: Run the Complete Setup Script

### Option A: Complete Setup (Recommended)

This includes everything:
- ✅ All 6 tables (user_profiles, transactions, telegram_links, chat_history, operation_traces, user_preferences)
- ✅ Indexes for performance
- ✅ Row Level Security (RLS) policies
- ✅ Automatic triggers for profile creation
- ✅ Timestamp management
- ✅ Helpful views

**Steps:**
1. Copy the entire content from: `/backend/database/supabase_complete_setup.sql`
2. Paste into the Supabase SQL Editor
3. Click **Run**
4. Wait for all queries to complete (usually 30 seconds)
5. You should see: "✅ Success" for each table creation

### Option B: Run Individual Setup Files

If you prefer to run individual migrations:

```sql
-- 1. First run user profiles setup
-- Copy from: /backend/database/user_profiles.sql

-- 2. Then run transaction setup
-- Copy from: /backend/database/add_currency_field.sql

-- 3. Then run migration fixes
-- Copy from: /backend/database/migration_fix_telegram.sql

-- 4. Finally run complete setup
-- Copy from: /backend/database/supabase_complete_setup.sql
```

---

## Step 3: Verify Tables Were Created

After running the setup, verify all tables exist:

```sql
-- Run this query in SQL Editor to verify
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
```

**Expected output:**
```
chat_history
operation_traces
telegram_links
transactions
user_preferences
user_profiles
```

---

## Step 4: Enable Row Level Security (RLS)

RLS is already enabled in the setup script, but verify:

1. Go to **Authentication** → **Policies** in Supabase
2. For each table, you should see multiple policies like:
   - "Users can read own transactions"
   - "Users can insert own transactions"
   - etc.

**If you don't see policies:**
- Run the setup script again
- Or manually enable: `ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;`

---

## Step 5: Configure Authentication

### Email/Password Authentication

1. Go to **Authentication** → **Providers** → **Email**
2. Toggle **Email** to **ON**
3. Find **Disable email verification** (important!)
   - Uncheck "Confirm email"
   - This allows users to sign up without email verification
4. Click **Save**

### Google OAuth (Optional)

For easy social login:

1. Go to **Authentication** → **Providers** → **Google**
2. Get credentials from: https://console.cloud.google.com
3. Paste OAuth Client ID and Secret
4. Click **Save**

---

## Step 6: Test Database Connection

### From Backend

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Test read
data = supabase.table("user_profiles").select("*").execute()
print("✅ Connected!" if data else "❌ Failed")
```

### From Frontend

```typescript
import { supabase } from '@/lib/supabase';

// Test read
const { data, error } = await supabase
  .from('user_profiles')
  .select('*')
  .limit(1);

console.log(error ? '❌ Error' : '✅ Connected');
```

---

## Step 7: Set Environment Variables

### Backend (`.env`)

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-key-here
```

### Frontend (`.env.local`)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Where to find keys:**
- Supabase dashboard → Settings → API
- `Service Role Key` = Backend only (never expose to frontend)
- `Anon Key` = Frontend (public key, safe to expose)

---

## Database Schema

### `user_profiles` (Per-User Profile)
```
id (UUID)               - User ID from auth
email (TEXT)            - User email
name (TEXT)             - Display name
monthly_income (NUMERIC)- User's monthly income
fixed_bills (NUMERIC)   - Fixed monthly expenses
savings_goal (NUMERIC)  - Monthly savings target
preferred_currency      - Default currency (NGN, USD, etc.)
telegram_chat_id        - Telegram user ID if linked
telegram_connected      - Is Telegram linked?
push_notification_enabled - Notification preference
created_at / updated_at - Timestamps
```

### `transactions` (User Expenses)
```
id (UUID)               - Transaction ID
user_id (UUID)          - User who owns this
merchant (TEXT)         - Where money was spent
amount (NUMERIC)        - Amount spent
category (TEXT)         - Food, Transport, etc.
description (TEXT)      - Additional details
date (TIMESTAMP)        - When spent
currency (TEXT)         - NGN, USD, EUR, etc.
source (TEXT)           - manual, receipt, telegram
ai_categorized (BOOL)   - Auto-categorized?
receipt_image_url       - Image of receipt
created_at / updated_at - Timestamps
```

### `telegram_links` (Telegram Bot Integration)
```
id (UUID)               - Link ID
user_id (UUID)          - User who linked
telegram_id (BIGINT)    - Telegram user ID
telegram_username       - Telegram @username
verified (BOOL)         - Email verified?
verification_code       - 6-digit code
created_at / updated_at - Timestamps
```

### `chat_history` (AI Conversation Logs)
```
id (UUID)               - Message ID
user_id (UUID)          - Who sent message
role (TEXT)             - 'user' or 'assistant'
content (TEXT)          - Message content
tokens_used (INT)       - API tokens used
created_at              - Timestamp
```

### `user_preferences` (User Settings)
```
id (UUID)               - Preference ID
user_id (UUID)          - User
theme (TEXT)            - light, dark, auto
language (TEXT)         - en, es, fr, etc.
notifications_enabled   - Get notifications?
email_digest_frequency  - daily, weekly, monthly
budget_alert_threshold  - Alert at X% budget
auto_categorize         - Auto-categorize expenses?
receive_tips            - Get AI tips?
```

---

## Row Level Security (RLS) Policies

### Why RLS?

RLS ensures users can ONLY access their own data:

```
❌ Without RLS: User A can see User B's transactions
✅ With RLS: User A can only see User A's transactions
```

### Policy Types

Each table has 4 policies:

1. **SELECT Policy**: Can user READ this data?
2. **INSERT Policy**: Can user CREATE new data?
3. **UPDATE Policy**: Can user MODIFY existing data?
4. **DELETE Policy**: Can user DELETE this data?

### Example Policy (Transactions)

```sql
-- Only show transactions where user_id = auth.uid()
CREATE POLICY "Users can read own transactions"
    ON transactions FOR SELECT
    USING (user_id = auth.uid());
```

This means: "Show only rows where the user_id equals the currently logged-in user's ID"

---

## Automatic Profile Creation

When a user signs up, a database trigger automatically:
1. Creates a profile in `user_profiles` table
2. Sets `preferred_currency` to NGN
3. Creates preferences in `user_preferences` table

**Trigger Code:**
```sql
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

This runs whenever `auth.users` gets a new record.

---

## Performance Indexes

Indexes speed up queries. Created indexes:

```sql
-- Users can quickly find their transactions
CREATE INDEX idx_transactions_user_id ON transactions(user_id);

-- Filter by date efficiently
CREATE INDEX idx_transactions_user_date ON transactions(user_id, date DESC);

-- Group by category quickly
CREATE INDEX idx_transactions_category ON transactions(user_id, category);
```

---

## Troubleshooting

### Issue: "User doesn't have permission error"

**Cause**: RLS policy is missing or misconfigured

**Fix**:
1. Check that RLS is enabled: `ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;`
2. Verify policies exist in SQL Editor
3. Re-run the complete setup script

### Issue: "relation 'user_profiles' does not exist"

**Cause**: Tables weren't created

**Fix**:
1. Run the complete setup script again
2. Check for errors in SQL Editor output
3. If still failing, delete and recreate the project

### Issue: "New users can't sign up"

**Cause**: Email verification is required, or auth is disabled

**Fix**:
1. Go to **Authentication** → **Policies**
2. Disable email verification: uncheck "Confirm email"
3. Go to **Providers** → Enable **Email**

### Issue: "Foreign key constraint violation"

**Cause**: Trying to insert transaction for user that doesn't exist

**Fix**:
1. Create profile first:
   ```sql
   INSERT INTO user_profiles (id, email, name) 
   VALUES ('user-uuid', 'email@example.com', 'Name');
   ```
2. Then create transaction:
   ```sql
   INSERT INTO transactions (user_id, merchant, amount) 
   VALUES ('user-uuid', 'Store', 5000);
   ```

---

## Maintenance

### Backup Database

In Supabase dashboard:
1. Go to **Settings** → **Backups**
2. Click **Request backup now**
3. Download backup file (contains all data)

### Clean Old Data

Remove old chat history (older than 30 days):
```sql
DELETE FROM chat_history 
WHERE created_at < now() - INTERVAL '30 days';
```

### Monitor Table Sizes

Check how much storage each table uses:
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Security Checklist

- ✅ RLS enabled on all tables
- ✅ Service role key kept secret (backend only)
- ✅ Anon key can be public (frontend)
- ✅ Email verification disabled (for UX)
- ✅ Password minimum 8 characters enforced
- ✅ User data isolated by RLS policies
- ✅ Never trust client-submitted user_id (use auth.uid())

---

## Next Steps

1. ✅ Run setup script in SQL Editor
2. ✅ Verify tables created (see Step 3)
3. ✅ Disable email verification
4. ✅ Set environment variables
5. ✅ Test connection from frontend & backend
6. ✅ Create test user account
7. ✅ Verify user can only see own data

---

## Useful SQL Queries

### Count users
```sql
SELECT COUNT(*) FROM user_profiles;
```

### Find user by email
```sql
SELECT * FROM user_profiles WHERE email = 'user@example.com';
```

### Get user's transactions
```sql
SELECT * FROM transactions 
WHERE user_id = 'user-uuid-here' 
ORDER BY date DESC;
```

### Get total spending by category
```sql
SELECT category, SUM(amount) as total 
FROM transactions 
WHERE user_id = 'user-uuid-here'
GROUP BY category 
ORDER BY total DESC;
```

### Get monthly spending
```sql
SELECT 
    date_trunc('month', date) as month,
    SUM(amount) as total
FROM transactions 
WHERE user_id = 'user-uuid-here'
GROUP BY month 
ORDER BY month DESC;
```

---

**📝 Last Updated**: February 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
