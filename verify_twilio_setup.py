"""
Verify Twilio Setup and Check Phone Number Verification Status
"""

from twilio.rest import Client
import json

print("=" * 70)
print("TWILIO SETUP VERIFICATION")
print("=" * 70)
print()

# Load config
try:
    with open('twilio_config.json', 'r') as f:
        config = json.load(f)
    print("✅ Config file loaded successfully")
except Exception as e:
    print(f"❌ Error loading config: {e}")
    exit(1)

print(f"Account SID: {config['account_sid']}")
print(f"From Number: {config['from_number']}")
print(f"Contacts: {len(config.get('contacts', []))} contact(s)")
print()

# Initialize client
try:
    client = Client(config['account_sid'], config['auth_token'])
    print("✅ Twilio client initialized")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    exit(1)

# Check account status
try:
    account = client.api.accounts(config['account_sid']).fetch()
    print(f"Account Status: {account.status}")
    print(f"Account Type: {account.type}")
    
    if account.type == 'Trial':
        print()
        print("⚠️  IMPORTANT: Your account is in TRIAL mode")
        print("   Trial accounts can ONLY send SMS to VERIFIED phone numbers")
        print()
        print("   To verify +918248450441:")
        print("   1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        print("   2. Click 'Add a new number'")
        print("   3. Enter: +918248450441")
        print("   4. Choose SMS or Call verification")
        print("   5. Enter the code you receive")
        print()
except Exception as e:
    print(f"❌ Error checking account: {e}")

# Check verified numbers
print()
print("Checking verified phone numbers...")
try:
    verified_numbers = client.outgoing_caller_ids.list()
    verified_phones = [v.phone_number for v in verified_numbers]
    
    print(f"Found {len(verified_phones)} verified number(s):")
    for phone in verified_phones:
        print(f"  ✅ {phone}")
    
    # Check if our contact is verified
    contact_phone = config['contacts'][0]['phone'] if config.get('contacts') else None
    if contact_phone:
        if contact_phone in verified_phones:
            print()
            print(f"✅ {contact_phone} IS VERIFIED - SMS will be delivered!")
        else:
            print()
            print(f"❌ {contact_phone} IS NOT VERIFIED")
            print(f"   This is why SMS is not being received!")
            print(f"   Please verify this number in Twilio Console")
except Exception as e:
    print(f"⚠️  Could not check verified numbers: {e}")
    print("   (This might be a permissions issue)")

# Check recent messages
print()
print("Checking recent SMS messages...")
try:
    messages = client.messages.list(limit=3)
    if messages:
        print(f"Found {len(messages)} recent message(s):")
        for msg in messages:
            print(f"  To: {msg.to}")
            print(f"  Status: {msg.status}")
            if msg.status != 'delivered':
                print(f"  ⚠️  Status: {msg.status} (not delivered)")
                if msg.error_message:
                    print(f"  Error: {msg.error_message}")
            print()
    else:
        print("No recent messages found")
except Exception as e:
    print(f"⚠️  Could not check messages: {e}")

print()
print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)

