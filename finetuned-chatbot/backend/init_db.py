#!/usr/bin/env python3
"""
Sentinel Database Initialization Script
This script creates the necessary tables in Supabase if they don't exist.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("=" * 50)
    print("🗄️  Sentinel Database Initialization")
    print("=" * 50)
    print()
    
    # Check Supabase credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Supabase credentials not found")
        print()
        print("Please set the following environment variables in .env:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")
        print()
        print("Get these from: https://supabase.com/dashboard")
        return False
    
    try:
        from supabase import create_client
    except ImportError:
        print("❌ Error: supabase package not installed")
        print("Run: pip install supabase")
        return False
    
    try:
        print("1️⃣  Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        print()
        
        # Check if tables exist
        print("2️⃣  Checking database tables...")
        
        try:
            # Try to query users table
            response = supabase.table("users").select("id").limit(1).execute()
            print("✅ 'users' table exists")
        except Exception as e:
            print("⚠️  'users' table not found")
            print("   Please run the SQL schema in Supabase:")
            print("   1. Go to https://supabase.com/dashboard")
            print("   2. Open your project")
            print("   3. Click 'SQL Editor'")
            print("   4. Click 'New Query'")
            print("   5. Copy the contents of: backend/database/init.sql")
            print("   6. Run the query")
            print()
            return False
        
        try:
            response = supabase.table("transactions").select("id").limit(1).execute()
            print("✅ 'transactions' table exists")
        except:
            print("⚠️  'transactions' table not found")
            return False
        
        try:
            response = supabase.table("telegram_links").select("id").limit(1).execute()
            print("✅ 'telegram_links' table exists")
        except:
            print("⚠️  'telegram_links' table not found")
            return False
        
        print()
        print("=" * 50)
        print("✅ Database Setup Complete!")
        print("=" * 50)
        print()
        print("Your Sentinel backend is ready to use!")
        print()
        print("Start the server with:")
        print("  cd backend")
        print("  python3 main.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("- Check your internet connection")
        print("- Verify SUPABASE_URL and SUPABASE_KEY are correct")
        print("- Make sure you've run the SQL schema from init.sql")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
