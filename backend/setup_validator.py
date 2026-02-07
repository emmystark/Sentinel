#!/usr/bin/env python3
"""
Sentinel Backend - Setup & Diagnostic Script
Helps with database setup, testing APIs, and deployment validation
"""
import os
import sys
import asyncio
import httpx
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

class SentinelSetup:
    def __init__(self):
        self.backend_url = os.getenv("BACKEND_URL", "https://sentinel-pchb.onrender.com")
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.hf_token = os.getenv("HF_TOKEN", "")
        
    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def check_env_vars(self):
        """Check all required environment variables"""
        self.print_header("1️⃣  Environment Variables Check")
        
        vars_to_check = {
            "SUPABASE_URL": self.supabase_url,
            "SUPABASE_KEY": self.supabase_key,
            "TELEGRAM_BOT_TOKEN": self.telegram_token,
            "GEMINI_API_KEY": self.gemini_key,
            "HF_TOKEN (HuggingFace)": self.hf_token,
            "BACKEND_URL": self.backend_url,
        }
        
        missing = []
        for var_name, var_value in vars_to_check.items():
            if var_value:
                status = "✅ Set"
                print(f"{var_name}: {status} (first 20 chars: {var_value[:20]}...)")
            else:
                status = "❌ Missing"
                print(f"{var_name}: {status}")
                missing.append(var_name)
        
        if missing:
            print(f"\n⚠️  Missing variables: {', '.join(missing)}")
            print("   Update .env file with these values\n")
            return False
        
        print(f"\n✅ All environment variables configured!\n")
        return True
    
    def check_database(self):
        """Check database connection and schema"""
        self.print_header("2️⃣  Database Check")
        
        try:
            from supabase import create_client
            
            if not self.supabase_url or not self.supabase_key:
                print("❌ Supabase credentials not configured")
                return False
            
            print("Connecting to Supabase...")
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Check tables
            tables_to_check = ["user_profiles", "transactions", "notifications"]
            
            for table in tables_to_check:
                try:
                    response = supabase.table(table).select("*").limit(1).execute()
                    print(f"  ✅ Table '{table}' exists")
                except Exception as e:
                    print(f"  ❌ Table '{table}' error: {str(e)[:80]}")
            
            # Check critical columns
            try:
                response = supabase.table("user_profiles").select("telegram_chat_id").limit(1).execute()
                print(f"  ✅ Column 'telegram_chat_id' exists")
            except Exception as e:
                print(f"  ❌ Column 'telegram_chat_id' missing: {str(e)[:80]}")
                print("\n   Run migration to fix:")
                print("   python database/migrate.py")
                return False
            
            print("\n✅ Database connection successful!\n")
            return True
            
        except Exception as e:
            print(f"❌ Database check failed: {e}\n")
            return False
    
    async def check_backend(self):
        """Check if backend is running"""
        self.print_header("3️⃣  Backend Service Check")
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.backend_url}/api/health")
                if response.status_code == 200:
                    print(f"✅ Backend running at {self.backend_url}")
                    print(f"   Response: {response.json()}\n")
                    return True
        except Exception as e:
            print(f"❌ Backend not responding: {e}")
            print(f"   Start backend with: uvicorn app:app --reload\n")
            return False
    
    async def check_telegram(self):
        """Check Telegram bot"""
        self.print_header("4️⃣  Telegram Bot Check")
        
        if not self.telegram_token:
            print("❌ TELEGRAM_BOT_TOKEN not configured\n")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{self.telegram_token}/getMe"
                )
                if response.status_code == 200:
                    bot_info = response.json().get("result", {})
                    print(f"✅ Telegram bot connected")
                    print(f"   Bot: @{bot_info.get('username', 'unknown')}")
                    print(f"   ID: {bot_info.get('id')}\n")
                    return True
                else:
                    print(f"❌ Telegram API error: {response.status_code}\n")
                    return False
        except Exception as e:
            print(f"❌ Telegram check failed: {e}\n")
            return False
    
    async def check_backend_endpoints(self):
        """Check key backend endpoints"""
        self.print_header("5️⃣  Backend Endpoints Check")
        
        endpoints = {
            "/api/health": "GET",
            "/api/telegram/verify": "GET",
            "/api/auth/profile": "GET",
        }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                for endpoint, method in endpoints.items():
                    try:
                        if method == "GET":
                            response = await client.get(
                                f"{self.backend_url}{endpoint}",
                                headers={"user-id": "test-user"} if "profile" in endpoint else {}
                            )
                        status = "✅" if response.status_code < 400 else "⚠️"
                        print(f"  {status} {method} {endpoint}: {response.status_code}")
                    except Exception as e:
                        print(f"  ❌ {method} {endpoint}: {str(e)[:50]}")
        except Exception as e:
            print(f"❌ Endpoint check failed: {e}")
        
        print()
    
    async def run_all_checks(self):
        """Run all checks"""
        self.print_header("🔍 Sentinel Backend Setup Validator")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        checks = [
            ("Environment", self.check_env_vars()),
            ("Database", self.check_database()),
        ]
        
        # Async checks
        if await self.check_backend():
            await self.check_telegram()
            await self.check_backend_endpoints()
        
        # Summary
        print("\n" + "="*60)
        print("  ✅ Setup Validation Complete")
        print("="*60)
        
        print("\n📝 Next Steps:")
        print("  1. If any checks failed, fix the issues above")
        print("  2. Run: python database/migrate.py")
        print("  3. Start backend: uvicorn app:app --reload")
        print("  4. Start frontend: cd frontend && npm run dev")
        print("  5. Test at: http://localhost:3001")


def main():
    """Run setup"""
    setup = SentinelSetup()
    
    try:
        asyncio.run(setup.run_all_checks())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
