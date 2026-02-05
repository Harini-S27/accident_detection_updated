# 📱 Twilio SMS Alert Setup Guide

## Quick Setup for Accident Detection SMS Alerts

### Step 1: Create Twilio Account

1. Go to [twilio.com](https://www.twilio.com)
2. Sign up for a free account (includes $15.50 trial credit)
3. Verify your email and phone number

### Step 2: Get Twilio Credentials

1. After logging in, go to your **Console Dashboard**
2. Find your **Account SID** and **Auth Token**
   - Account SID: Starts with "AC..."
   - Auth Token: Click "View" to reveal it

### Step 3: Get a Twilio Phone Number

1. In Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
2. Choose a number (or use free trial number)
3. Make sure it supports **SMS** messaging
4. Copy the phone number (format: +1234567890)

### Step 4: Configure Your Project

1. Open `twilio_config.json` in your project folder
2. Replace the placeholder values:

```json
{
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "your_auth_token_here",
    "from_number": "+1234567890",
    "contacts": [
        {
            "name": "Emergency Contact",
            "phone": "+918248450441"
        }
    ]
}
```

### Step 5: Contact Number Format

For India numbers, use one of these formats:
- `+918248450441` (recommended - with country code)
- `918248450441` (without +)
- `08248450441` (local format - will be auto-converted)

The system automatically formats Indian numbers to `+91XXXXXXXXXX`.

### Step 6: Test the Setup

Run this command to test your Twilio connection:

```bash
python twilio_sms.py
```

### Step 7: Run Your Application

1. Start your accident detection UI:
   ```bash
   python video_test_ui.py
   ```

2. When a **severe accident** is detected, SMS will automatically be sent!

---

## How It Works

✅ **Automatic SMS Trigger**
- When `severe_count >= 1` in video analysis
- SMS is sent to all contacts in `twilio_config.json`
- Message includes video name, timestamp, and detection details

✅ **Message Content**
```
⚠️ ACCIDENT ALERT ⚠️

SEVERE ACCIDENT DETECTED!

Video: testing1.mp4
Time: 2026-01-07 10:30:15
Frames: 356
Severe: 1
Moderate: 258
Fire: 0

Please check immediately!
```

---

## Adding More Contacts

Edit `twilio_config.json` to add multiple contacts:

```json
{
    "contacts": [
        {
            "name": "Emergency Contact 1",
            "phone": "+918248450441"
        },
        {
            "name": "Emergency Contact 2",
            "phone": "+919876543210"
        },
        {
            "name": "Police Control Room",
            "phone": "+911234567890"
        }
    ]
}
```

---

## Cost Information

- **Twilio Free Trial**: $15.50 credit included
- **SMS to India**: ~$0.008 per message (less than 1 rupee)
- **Free Trial**: Enough for ~1,900 SMS messages

---

## Troubleshooting

### ❌ "SMS alerts not enabled"
- Check if `twilio_config.json` exists
- Verify credentials are correct (not placeholder values)
- Check console for error messages

### ❌ "Failed to send SMS"
- Verify Twilio account has credits
- Check phone number format (should include country code)
- Verify Twilio number has SMS capability enabled

### ❌ "Connection test failed"
- Check internet connection
- Verify Account SID and Auth Token are correct
- Check Twilio console for account status

---

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit `twilio_config.json` to public repositories
- Keep your Auth Token secret
- Consider using environment variables for production

---

## Support

- Twilio Documentation: https://www.twilio.com/docs
- Twilio Support: support@twilio.com
- SMS API Docs: https://www.twilio.com/docs/sms

---

**Your contact number (8248450441) is already configured!**
Just add your Twilio credentials to `twilio_config.json` and you're ready to go! 🚀

