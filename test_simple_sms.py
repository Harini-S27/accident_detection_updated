"""
Send a simple test SMS to check if it's a content issue
"""

from twilio.rest import Client
import json

# Load config
with open('twilio_config.json', 'r') as f:
    config = json.load(f)

# Initialize client
client = Client(config['account_sid'], config['auth_token'])

print("=" * 70)
print("Sending Simple Test SMS")
print("=" * 70)
print()

try:
    # Send simple test message
    message = client.messages.create(
        body="Test message from Accident Detection System",
        from_=config['from_number'],
        to=config['contacts'][0]['phone']
    )
    
    print(f"✅ Message sent!")
    print(f"SID: {message.sid}")
    print(f"Status: {message.status}")
    print(f"To: {message.to}")
    print()
    
    if message.status == 'queued':
        print("⚠️  Status is 'queued'")
        print("   This might be a trial account restriction")
        print("   Check status in Twilio Console in a few minutes")
    elif message.status == 'sent':
        print("✅ Message sent (check phone for delivery)")
    elif message.status == 'delivered':
        print("✅ Message delivered!")
    
    print()
    print("Check your phone (+918248450441) for the message")
    print("If you don't receive it, check Twilio Console for status")
    print("Link: https://console.twilio.com/us1/monitor/logs/messaging")
    
except Exception as e:
    print(f"❌ Error: {e}")

