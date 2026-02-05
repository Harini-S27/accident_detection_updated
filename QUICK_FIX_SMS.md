# ⚠️ SMS Alert Not Working - Quick Fix

## Problem
When severe accident is detected, SMS is **NOT** being sent to +918248450441 because **Twilio credentials are not configured**.

## Why SMS Didn't Send

1. ✅ Severe accident detected: **YES** (1 severe accident found)
2. ❌ SMS alerts enabled: **NO** (Twilio not configured)
3. ❌ SMS sent: **NO** (because SMS is disabled)

## Solution - Configure Twilio (5 minutes)

### Step 1: Get Twilio Account
1. Go to https://www.twilio.com
2. Sign up for FREE account (get $15.50 credit)
3. Verify your email

### Step 2: Get Your Credentials
1. After login, go to **Console Dashboard**
2. Copy your **Account SID** (starts with "AC...")
3. Click "View" to reveal **Auth Token**
4. Go to **Phone Numbers** → Get a phone number (free trial number works)

### Step 3: Update twilio_config.json

Open `twilio_config.json` and replace:

```json
{
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "your_actual_auth_token_here",
    "from_number": "+1234567890",
    "contacts": [
        {
            "name": "Emergency Contact",
            "phone": "+918248450441"
        }
    ]
}
```

Replace:
- `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` → Your Account SID
- `your_actual_auth_token_here` → Your Auth Token
- `+1234567890` → Your Twilio phone number

### Step 4: Test

Run this to test:
```bash
python twilio_sms.py
```

Should show: `[Twilio] SMS alerts enabled`

### Step 5: Restart UI

Restart your application:
```bash
python video_test_ui.py
```

Now when severe accident is detected, you'll see:
- ✅ "Success! SMS sent to 1 contact(s)"
- 📱 "Sent to: +918248450441"

## UI Now Shows Status

After this update, the UI will show:

**When SMS is DISABLED (current state):**
```
⚠️ SMS Alerts Disabled - Twilio not configured
📱 Contact: +918248450441 (configure in twilio_config.json)
```

**When SMS is SENT (after configuration):**
```
✅ Success! SMS sent to 1 contact(s)
📱 Sent to: +918248450441
```

**When SMS FAILS:**
```
❌ SMS failed to send. Check Twilio credentials.
```

---

**Your contact number (8248450441) is ready - just add Twilio credentials!** 🚀

