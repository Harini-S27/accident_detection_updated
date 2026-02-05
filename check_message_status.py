"""
Check the status of a specific SMS message
"""

from twilio.rest import Client
import json

# Load config
with open('twilio_config.json', 'r') as f:
    config = json.load(f)

# Initialize client
client = Client(config['account_sid'], config['auth_token'])

# Message SID from your log (update with latest SID)
message_sid = "SMf9816278ddb1af1b2638eac37371e50b"

print("=" * 70)
print(f"Checking Message Status: {message_sid}")
print("=" * 70)
print()

try:
    message = client.messages(message_sid).fetch()
    
    print(f"To: {message.to}")
    print(f"From: {message.from_}")
    print(f"Status: {message.status}")
    print(f"Date Sent: {message.date_sent}")
    print()
    
    if message.status == 'delivered':
        print("✅ MESSAGE WAS DELIVERED!")
        print(f"   Delivered at: {message.date_sent}")
    elif message.status == 'sent':
        print("⚠️  MESSAGE WAS SENT but delivery status unknown")
        print("   This usually means it's on the way or delivered")
    elif message.status == 'queued':
        print("⚠️  MESSAGE IS QUEUED")
        print("   It's waiting to be sent. This might mean:")
        print("   - Phone number is not verified (Trial account)")
        print("   - Network issue")
        print("   - Message is still processing")
    elif message.status == 'failed':
        print("❌ MESSAGE FAILED")
        if message.error_message:
            print(f"   Error: {message.error_message}")
        if message.error_code:
            print(f"   Error Code: {message.error_code}")
    elif message.status == 'undelivered':
        print("❌ MESSAGE UNDELIVERED")
        if message.error_message:
            print(f"   Error: {message.error_message}")
        if message.error_code:
            print(f"   Error Code: {message.error_code}")
    else:
        print(f"Status: {message.status}")
    
    if message.error_code:
        print()
        print("Error Details:")
        print(f"  Error Code: {message.error_code}")
        if message.error_code == 21211:
            print("  ⚠️  This means: Phone number not verified")
            print("  Solution: Verify +918248450441 in Twilio Console")
            print("  Link: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        elif message.error_code == 21608:
            print("  ⚠️  This means: Unsubscribed number")
        elif message.error_code == 21610:
            print("  ⚠️  This means: Invalid phone number format")
    
    print()
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error checking message: {e}")

