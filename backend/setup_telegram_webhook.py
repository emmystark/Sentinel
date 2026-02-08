#!/usr/bin/env python3
"""
Setup Telegram Webhook for Sentinel Bot
Connects your Telegram bot to the production backend
Run this once after deploying to production
"""

import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_WEBHOOK_URL", "https://sentinel-pchb.onrender.com")
TELEGRAM_API = os.getenv("TELEGRAM_API_BASE_URL", "https://api.telegram.org")

def setup_webhook():
    """Setup Telegram webhook to receive updates"""
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set in environment")
        print("Please set it and try again")
        return False
    
    webhook_url = f"{BACKEND_URL}/api/telegram/webhook"
    
    print(f"Setting up Telegram webhook...")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print(f"Webhook URL: {webhook_url}")
    
    try:
        # Set the webhook
        response = httpx.post(
            f"{TELEGRAM_API}/bot{BOT_TOKEN}/setWebhook",
            json={
                "url": webhook_url,
                "allowed_updates": ["message", "callback_query"]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook setup successful!")
                print(f"Response: {result.get('description', 'Webhook configured')}")
                return True
            else:
                print(f"❌ Webhook setup failed: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ API returned {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up webhook: {e}")
        return False

def verify_webhook():
    """Verify webhook is set correctly"""
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        return False
    
    print(f"\n📋 Verifying webhook configuration...")
    
    try:
        response = httpx.get(
            f"{TELEGRAM_API}/bot{BOT_TOKEN}/getWebhookInfo",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                info = result.get("result", {})
                print(f"✅ Webhook Info:")
                print(f"   URL: {info.get('url', 'Not set')}")
                print(f"   Has custom certificate: {info.get('has_custom_certificate', False)}")
                print(f"   Pending update count: {info.get('pending_update_count', 0)}")
                
                if info.get('last_error_message'):
                    print(f"   ⚠️ Last error: {info.get('last_error_message')}")
                    print(f"   Last error date: {info.get('last_error_date')}")
                
                return True
            else:
                print(f"❌ Could not get webhook info: {result.get('description')}")
                return False
        else:
            print(f"❌ API returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying webhook: {e}")
        return False

def delete_webhook():
    """Remove the webhook (useful for testing with polling)"""
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        return False
    
    print(f"\n🗑️  Deleting webhook...")
    
    try:
        response = httpx.post(
            f"{TELEGRAM_API}/bot{BOT_TOKEN}/deleteWebhook",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook deleted successfully")
                print("Bot will now use polling instead of webhooks")
                return True
            else:
                print(f"❌ Error: {result.get('description')}")
                return False
        else:
            print(f"❌ API returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False

def main():
    """Main setup flow"""
    
    print("=" * 60)
    print("Sentinel Telegram Bot - Webhook Setup")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            success = setup_webhook()
            if success:
                verify_webhook()
            sys.exit(0 if success else 1)
            
        elif command == "verify":
            verify_webhook()
            sys.exit(0)
            
        elif command == "delete":
            success = delete_webhook()
            sys.exit(0 if success else 1)
            
        elif command == "help":
            print("""
Usage:
  python setup_telegram_webhook.py setup    - Setup webhook
  python setup_telegram_webhook.py verify   - Check webhook status
  python setup_telegram_webhook.py delete   - Remove webhook
  python setup_telegram_webhook.py help     - Show this help

Environment Variables Required:
  TELEGRAM_BOT_TOKEN        - Your Telegram bot token from @BotFather
  BACKEND_WEBHOOK_URL       - Base URL of your backend (e.g., https://sentinel-pchb.onrender.com)

Example:
  export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
  export BACKEND_WEBHOOK_URL="https://sentinel-pchb.onrender.com"
  python setup_telegram_webhook.py setup
            """)
            sys.exit(0)
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' for available commands")
            sys.exit(1)
    else:
        # Interactive mode
        print("\nWhat would you like to do?")
        print("1. Setup webhook")
        print("2. Verify webhook status")
        print("3. Delete webhook")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            setup_webhook()
            verify_webhook()
        elif choice == "2":
            verify_webhook()
        elif choice == "3":
            delete_webhook()
        elif choice == "4":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice")
            sys.exit(1)

if __name__ == "__main__":
    main()
