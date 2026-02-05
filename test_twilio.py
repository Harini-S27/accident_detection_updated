"""
Quick test script to verify Twilio SMS configuration
"""

from twilio_sms import TwilioSMSAlert

print("=" * 60)
print("Testing Twilio SMS Configuration")
print("=" * 60)
print()

# Initialize SMS alert system
sms_alert = TwilioSMSAlert('twilio_config.json')

print(f"SMS Alerts Enabled: {sms_alert.enabled}")
print()

if sms_alert.enabled:
    # Test connection
    print("Testing Twilio connection...")
    success, message = sms_alert.test_connection()
    print(f"Connection Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Message: {message}")
    print()
    
    # Show configured contacts
    if sms_alert.config:
        print("Configured Contacts:")
        for contact in sms_alert.config.get('contacts', []):
            print(f"  - {contact.get('name', 'Unknown')}: {contact.get('phone', 'N/A')}")
        print()
    
    print("=" * 60)
    print("✅ Twilio is configured and ready!")
    print("=" * 60)
    print()
    print("When a severe accident is detected, SMS will be sent to:")
    for contact in sms_alert.config.get('contacts', []):
        print(f"  📱 {contact.get('phone', 'N/A')}")
else:
    print("=" * 60)
    print("❌ SMS Alerts are DISABLED")
    print("=" * 60)
    print()
    print("Please check:")
    print("  1. twilio_config.json has correct credentials")
    print("  2. Account SID and Auth Token are valid")
    print("  3. Twilio phone number is correct")

