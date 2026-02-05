"""
Twilio SMS Alert Module for Accident Detection
Sends SMS alerts when severe accidents are detected
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import json
import os
from pathlib import Path
from datetime import datetime

class TwilioSMSAlert:
    """Handles SMS alerts via Twilio"""
    
    def __init__(self, config_file='twilio_config.json'):
        """
        Initialize Twilio SMS client
        
        Args:
            config_file: Path to configuration file with Twilio credentials
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.client = None
        self.enabled = False
        
        if self.config and self.validate_config():
            try:
                self.client = Client(
                    self.config['account_sid'],
                    self.config['auth_token']
                )
                self.enabled = True
                print(f"[Twilio] SMS alerts enabled")
            except Exception as e:
                print(f"[Twilio] Failed to initialize: {e}")
                self.enabled = False
        else:
            print(f"[Twilio] SMS alerts disabled - check configuration")
    
    def load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            # Create default config file
            self.create_default_config()
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Twilio] Error loading config: {e}")
            return None
    
    def create_default_config(self):
        """Create default configuration file template"""
        default_config = {
            "account_sid": "YOUR_TWILIO_ACCOUNT_SID",
            "auth_token": "YOUR_TWILIO_AUTH_TOKEN",
            "from_number": "+1234567890",
            "contacts": [
                {
                    "name": "Emergency Contact",
                    "phone": "+918248450441"
                }
            ]
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"[Twilio] Created default config file: {self.config_file}")
            print(f"[Twilio] Please edit {self.config_file} with your Twilio credentials")
        except Exception as e:
            print(f"[Twilio] Error creating config: {e}")
    
    def validate_config(self):
        """Validate configuration has required fields"""
        required_fields = ['account_sid', 'auth_token', 'from_number', 'contacts']
        
        for field in required_fields:
            if field not in self.config:
                print(f"[Twilio] Missing required field: {field}")
                return False
        
        # Check if credentials are not default placeholders
        if 'YOUR_TWILIO' in self.config.get('account_sid', '') or \
           'YOUR_TWILIO' in self.config.get('auth_token', ''):
            print(f"[Twilio] Please update {self.config_file} with your actual Twilio credentials")
            return False
        
        if not self.config.get('contacts'):
            print(f"[Twilio] No contacts configured")
            return False
        
        return True
    
    def send_accident_alert(self, video_name="Unknown", frame_count=0, 
                           fire_count=0, moderate_count=0, severe_count=0):
        """
        Send SMS alert to all configured contacts when severe accident detected
        
        Args:
            video_name: Name of the video file
            frame_count: Total frames processed
            fire_count: Number of fire detections
            moderate_count: Number of moderate detections
            severe_count: Number of severe detections
        """
        if not self.enabled or not self.client:
            print("[Twilio] SMS alerts not enabled")
            return False
        
        if severe_count < 1:
            print("[Twilio] No severe accident - SMS not sent")
            return False
        
        # Create alert message - SHORT format for better delivery
        message = "🚨 SEVERE ACCIDENT DETECTED! Immediate attention required-loc:sathyabama."
        
        results = []
        from_number = self.config['from_number']
        
        # Send to all contacts
        for contact in self.config['contacts']:
            name = contact.get('name', 'Contact')
            phone = contact.get('phone', '')
            
            if not phone:
                continue
            
            # Ensure phone number has + prefix for India
            if not phone.startswith('+'):
                if phone.startswith('91'):
                    phone = '+' + phone
                elif phone.startswith('0'):
                    phone = '+91' + phone[1:]
                else:
                    phone = '+91' + phone
            
            try:
                print(f"[Twilio] Sending SMS to {name} ({phone})...")
                
                message_obj = self.client.messages.create(
                    body=message,
                    from_=from_number,
                    to=phone
                )
                
                # Check message status
                status = message_obj.status
                error_code = message_obj.error_code
                error_message = message_obj.error_message
                
                if status in ['queued', 'sending', 'sent', 'delivered']:
                    results.append({
                        'contact': name,
                        'phone': phone,
                        'status': 'success',
                        'message_sid': message_obj.sid,
                        'delivery_status': status
                    })
                    
                    if status == 'queued':
                        print(f"[Twilio] SMS queued for {name} (SID: {message_obj.sid})")
                        print(f"[Twilio] ⚠️  WARNING: Status is 'queued' - message may not be delivered!")
                        print(f"[Twilio] ⚠️  For TRIAL accounts, phone number MUST be verified")
                        print(f"[Twilio] ⚠️  Verify {phone} at: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
                        print(f"[Twilio] ⚠️  Check message status in Twilio Console: Monitor → Logs → Messaging")
                    elif status == 'delivered':
                        print(f"[Twilio] ✅ SMS DELIVERED to {name} (SID: {message_obj.sid})")
                    else:
                        print(f"[Twilio] SMS sent to {name} (SID: {message_obj.sid}, Status: {status})")
                    
                    # Warn if account is trial and number might not be verified
                    if error_code == 21211:  # Invalid 'To' Phone Number
                        print(f"[Twilio] ⚠️ WARNING: Phone number may not be verified in Twilio")
                        print(f"[Twilio] Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
                else:
                    results.append({
                        'contact': name,
                        'phone': phone,
                        'status': 'failed',
                        'error': f"Status: {status}, Error: {error_message or 'Unknown'}"
                    })
                    print(f"[Twilio] SMS failed: Status={status}, Error={error_message}")
                    
            except TwilioException as e:
                error_msg = str(e)
                error_code = getattr(e, 'code', None)
                
                results.append({
                    'contact': name,
                    'phone': phone,
                    'status': 'failed',
                    'error': error_msg,
                    'error_code': error_code
                })
                
                print(f"[Twilio] Failed to send SMS to {name}: {error_msg}")
                
                # Check for common trial account errors
                if error_code == 21211:
                    print(f"[Twilio] ⚠️ This phone number needs to be verified in Twilio Console")
                    print(f"[Twilio] Verify at: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
                elif 'trial' in error_msg.lower() or error_code == 20003:
                    print(f"[Twilio] ⚠️ Trial account restriction - verify phone number first")
                
            except TwilioException as e:
                error_msg = str(e)
                results.append({
                    'contact': name,
                    'phone': phone,
                    'status': 'failed',
                    'error': error_msg
                })
                print(f"[Twilio] Failed to send SMS to {name}: {error_msg}")
            except Exception as e:
                error_msg = str(e)
                results.append({
                    'contact': name,
                    'phone': phone,
                    'status': 'failed',
                    'error': error_msg
                })
                print(f"[Twilio] Unexpected error sending to {name}: {error_msg}")
        
        return results
    
    def test_connection(self):
        """Test Twilio connection"""
        if not self.enabled:
            return False, "SMS alerts not enabled"
        
        try:
            # Try to fetch account info
            account = self.client.api.accounts(self.config['account_sid']).fetch()
            return True, f"Connected to Twilio account: {account.friendly_name}"
        except Exception as e:
            return False, f"Connection test failed: {e}"


if __name__ == "__main__":
    # Test the SMS module
    sms_alert = TwilioSMSAlert()
    
    if sms_alert.enabled:
        success, message = sms_alert.test_connection()
        print(f"Connection test: {message}")
        
        # Test SMS (uncomment to send test message)
        # sms_alert.send_accident_alert(
        #     video_name="test_video.mp4",
        #     frame_count=100,
        #     severe_count=1
        # )
    else:
        print("SMS alerts not configured. Please set up twilio_config.json")

