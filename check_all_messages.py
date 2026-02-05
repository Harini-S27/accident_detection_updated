"""
Check all recent SMS messages and their delivery status
"""

from twilio.rest import Client
import json
from datetime import datetime, timedelta

# Load config
with open('twilio_config.json', 'r') as f:
    config = json.load(f)

# Initialize client
client = Client(config['account_sid'], config['auth_token'])

print("=" * 70)
print("Checking ALL Recent SMS Messages")
print("=" * 70)
print()

try:
    # Get messages from last 24 hours
    messages = client.messages.list(limit=10)
    
    if not messages:
        print("No messages found")
    else:
        print(f"Found {len(messages)} recent message(s):\n")
        
        for i, msg in enumerate(messages, 1):
            print(f"Message #{i}:")
            print(f"  SID: {msg.sid}")
            print(f"  To: {msg.to}")
            print(f"  From: {msg.from_}")
            print(f"  Status: {msg.status}")
            print(f"  Date: {msg.date_sent}")
            
            if msg.status == 'queued':
                print(f"  ⚠️  QUEUED - Not delivered yet")
                print(f"  ⚠️  This usually means:")
                print(f"     - Trial account restriction")
                print(f"     - Number verification issue")
                print(f"     - Network/carrier issue")
            elif msg.status == 'delivered':
                print(f"  ✅ DELIVERED")
            elif msg.status == 'sent':
                print(f"  ✅ SENT (delivery status unknown)")
            elif msg.status == 'failed':
                print(f"  ❌ FAILED")
            elif msg.status == 'undelivered':
                print(f"  ❌ UNDELIVERED")
            
            if msg.error_code:
                print(f"  Error Code: {msg.error_code}")
            if msg.error_message:
                print(f"  Error Message: {msg.error_message}")
            
            # Check if number is verified
            try:
                verified_numbers = client.outgoing_caller_ids.list()
                verified_phones = [v.phone_number for v in verified_numbers]
                if msg.to in verified_phones:
                    print(f"  ✅ Number IS verified")
                else:
                    print(f"  ❌ Number NOT verified")
            except:
                pass
            
            print()
            print("-" * 70)
            print()
    
    # Check account status
    print("Account Information:")
    account = client.api.accounts(config['account_sid']).fetch()
    print(f"  Status: {account.status}")
    print(f"  Type: {account.type}")
    
    if account.type == 'Trial':
        print()
        print("⚠️  TRIAL ACCOUNT LIMITATIONS:")
        print("  - Can only send to verified numbers (which you have)")
        print("  - May have rate limits")
        print("  - Some carriers may block trial account messages")
        print()
        print("💡 Try upgrading your account if messages keep getting queued")
        print("   Go to: Billing → Upgrade Account")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

