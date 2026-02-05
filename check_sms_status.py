"""
Check SMS delivery status from Twilio
"""

from twilio.rest import Client
import json

# Load config
with open('twilio_config.json', 'r') as f:
    config = json.load(f)

# Initialize client
client = Client(config['account_sid'], config['auth_token'])

print("=" * 60)
print("Checking Recent SMS Messages")
print("=" * 60)
print()

# Get recent messages
messages = client.messages.list(limit=5)

if messages:
    print(f"Found {len(messages)} recent messages:\n")
    for msg in messages:
        print(f"To: {msg.to}")
        print(f"From: {msg.from_}")
        print(f"Status: {msg.status}")
        print(f"SID: {msg.sid}")
        if msg.error_message:
            print(f"Error: {msg.error_message}")
        if msg.error_code:
            print(f"Error Code: {msg.error_code}")
        print(f"Date: {msg.date_sent}")
        print("-" * 60)
        print()
else:
    print("No messages found")

# Check if account is in trial mode
account = client.api.accounts(config['account_sid']).fetch()
print(f"Account Status: {account.status}")
print(f"Account Type: {'Trial' if account.type == 'Trial' else 'Full'}")
print()

if account.type == 'Trial':
    print("⚠️ Your account is in TRIAL mode")
    print("You can only send SMS to verified phone numbers")
    print("Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print("to verify +918248450441")

