"""
Database initialization and migration script.
Run this to set up/fix the database schema.

NOTE: Supabase doesn't support direct SQL execution via the API.
You must run the SQL statements manually in the Supabase SQL Editor.
This script provides verification and instructions.
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_supabase():
    """Initialize Supabase client"""
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)

def print_migration_instructions():
    """Print instructions for manual migration"""
    logger.info("\n" + "="*70)
    logger.info("📋 MANUAL MIGRATION REQUIRED")
    logger.info("="*70)
    logger.info("\nSupabase doesn't support direct SQL execution via API.")
    logger.info("Follow these steps to apply the migration:")
    logger.info("\n1️⃣  Go to: https://app.supabase.com/project/_/sql/new")
    logger.info("2️⃣  Copy the contents of: database/migration_fix_telegram.sql")
    logger.info("3️⃣  Paste into the SQL editor")
    logger.info("4️⃣  Click 'Run' button")
    logger.info("\nOR run them one at a time:")
    logger.info("\n-- Command 1: Add columns to user_profiles")
    logger.info("ALTER TABLE user_profiles")
    logger.info("ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT UNIQUE,")
    logger.info("ADD COLUMN IF NOT EXISTS telegram_connected BOOLEAN DEFAULT FALSE,")
    logger.info("ADD COLUMN IF NOT EXISTS telegram_username TEXT;")
    logger.info("\n-- Command 2: Create transactions table (if missing)")
    logger.info("CREATE TABLE IF NOT EXISTS transactions (")
    logger.info("  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),")
    logger.info("  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,")
    logger.info("  merchant TEXT NOT NULL,")
    logger.info("  amount NUMERIC NOT NULL,")
    logger.info("  category TEXT,")
    logger.info("  description TEXT,")
    logger.info("  source TEXT,")
    logger.info("  ai_categorized BOOLEAN DEFAULT FALSE,")
    logger.info("  created_at TIMESTAMP DEFAULT now(),")
    logger.info("  updated_at TIMESTAMP DEFAULT now(),")
    logger.info("  CONSTRAINT valid_amount CHECK (amount > 0)")
    logger.info(");")
    logger.info("\n" + "="*70 + "\n")

def apply_migration(supabase):
    """Apply database migrations by checking current state"""
    try:
        logger.info("Checking database state...")
        
        # Try to access the tables to see what exists
        try:
            user_profiles = supabase.table("user_profiles").select("id").limit(1).execute()
            logger.info("✅ user_profiles table exists")
        except Exception as e:
            logger.error(f"❌ user_profiles table error: {e}")
        
        try:
            transactions = supabase.table("transactions").select("id").limit(1).execute()
            logger.info("✅ transactions table exists")
        except Exception as e:
            logger.warning(f"⚠️ transactions table may not exist: {e}")
        
        print_migration_instructions()
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration check failed: {e}")
        print_migration_instructions()
        return False
def verify_database(supabase):
    """Verify database setup"""
    try:
        logger.info("\n🔍 Verifying database schema...\n")
        
        # Check tables exist
        tables = ["user_profiles", "transactions"]
        all_good = True
        
        for table in tables:
            try:
                response = supabase.table(table).select("*").limit(1).execute()
                logger.info(f"✅ Table '{table}' exists")
            except Exception as e:
                logger.warning(f"⚠️ Table '{table}' may not exist: {str(e)[:80]}")
                all_good = False
        
        # Check critical column
        try:
            response = supabase.table("user_profiles").select("telegram_chat_id").limit(1).execute()
            logger.info("✅ Column 'telegram_chat_id' exists - MIGRATION APPLIED!")
            return True
        except Exception as e:
            logger.error(f"\n❌ Column 'telegram_chat_id' missing - MIGRATION NEEDED")
            logger.error(f"Error: {str(e)[:100]}\n")
            print_migration_instructions()
            return False
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        print_migration_instructions()
        return False

if __name__ == "__main__":
    try:
        supabase = get_supabase()
        logger.info("\n🚀 Sentinel Database Migration Tool\n")
        apply_migration(supabase)
        verify_database(supabase)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print_migration_instructions()
        exit(1)
